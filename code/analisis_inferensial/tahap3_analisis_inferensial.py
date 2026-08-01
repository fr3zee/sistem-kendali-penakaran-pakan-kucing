#!/usr/bin/env python3
"""
Tahap 3 — Analisis Inferensial Final
=====================================
Skrip reproduktif sesuai implementation_plan.md yang di-ACC Final.

Menghitung seluruh uji omnibus, post-hoc, ukuran efek, konsistensi,
proporsi WithinTolerance, settling kondisional, dan bridging deskriptif.

Seluruh metode omnibus mengikuti keputusan Tahap 2 tanpa seleksi ulang.
Metode tidak boleh diubah berdasarkan hasil signifikansi.
"""

import datetime, platform, sys, warnings, os
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import (
    kruskal, f_oneway, levene,
    chi2_contingency, fisher_exact,
    mannwhitneyu
)
from statsmodels.stats.oneway import effectsize_oneway
from statsmodels.stats.multitest import multipletests
import pingouin as pg
import scikit_posthocs as sp
import openpyxl
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

warnings.filterwarnings("ignore", category=FutureWarning)

# ============================================================
# CONFIG
# ============================================================
ALPHA = 0.05
SEED  = 42
N_BOOTSTRAP = 10000
N_MC  = 100_000
np.random.seed(SEED)

BASE_DIR = Path(r"d:\SKRIPSI\draft\3. dok trial hasil\Pengambilan Data\rekap data")
DATASET_PATH = BASE_DIR / "antigravity (md & csv)" / "master_dataset_160.csv"
REKOM_PATH = BASE_DIR / "Laporan" / "Tahap2" / "rekomendasi_uji_tahap3.csv"
OUTPUT_DIR = BASE_DIR / "Laporan" / "Tahap3"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS = [15, 20, 25, 30]
METRICS_CONTINUOUS = ["AbsError_pct", "MaxOvershoot_pct", "Duration_s",
                      "RiseTime_10_90_s"]

# Version info
VERSION_INFO = {
    "Python": sys.version,
    "pandas": pd.__version__,
    "numpy": np.__version__,
    "scipy": __import__('scipy').__version__,
    "statsmodels": __import__('statsmodels').__version__,
    "pingouin": pg.__version__,
    "scikit_posthocs": sp.__version__,
    "openpyxl": openpyxl.__version__,
    "python-docx": __import__('docx').__version__,
    "OS": platform.platform(),
    "Timestamp": datetime.datetime.now().isoformat(),
    "Seed": SEED,
    "N_Bootstrap": N_BOOTSTRAP,
}

print("=" * 60)
print("TAHAP 3 — ANALISIS INFERENSIAL FINAL")
print("=" * 60)
for k, v in VERSION_INFO.items():
    print(f"  {k}: {v}")
print()

# ============================================================
# 1. LOAD & AUDIT
# ============================================================
print(">>> 1. Audit Input")
df    = pd.read_csv(DATASET_PATH)
rekom = pd.read_csv(REKOM_PATH)

TAHAP2_DIR = BASE_DIR / "Laporan" / "Tahap2"
df_shapiro_residual = pd.read_csv(TAHAP2_DIR / "hasil_shapiro_residual_per_setpoint.csv")
df_homogeneity      = pd.read_csv(TAHAP2_DIR / "hasil_brown_forsythe_per_setpoint.csv")
df_recommendation   = pd.read_csv(REKOM_PATH)

# Build recommendation lookup
rekom_lookup = {}
for _, row in rekom.iterrows():
    key = (row["Metric"], int(row["Setpoint_g"]))
    rekom_lookup[key] = {
        "uji": row["Uji_yang_direkomendasikan"],
        "posthoc": row["Post_hoc_yang_direkomendasikan"],
    }

# Audit checks
assert len(df) == 160, f"Expected 160 rows, got {len(df)}"
combos = df.groupby(["Scenario", "Setpoint_g"]).size()
assert len(combos) == 16, f"Expected 16 combinations, got {len(combos)}"
assert (combos == 10).all(), f"Not all combinations have 10 trials"
assert df["Valid"].all(), "Not all Valid == TRUE"
assert (df["StopReason"] == "TARGET").all(), "Not all StopReason == TARGET"

# Recompute WithinTolerance
df["WithinTolerance"] = (df["FinalError_pct"].abs() <= 5).astype(int)

# Handle SettlingTime_s
if df["SettlingTime_s"].dtype == object:
    df["SettlingTime_s"] = pd.to_numeric(df["SettlingTime_s"], errors="coerce")
df["ST_available"] = df["SettlingTime_s"].notna()

# Mismatch check
mismatch = ((df["WithinTolerance"] == 1) != df["ST_available"]).sum()
assert mismatch == 0, f"Mismatch WithinTolerance vs SettlingTime: {mismatch}"

# Freeze scenario order
df["Scenario"] = pd.Categorical(df["Scenario"], categories=SCENARIOS, ordered=True)

print(f"  Rows: {len(df)}")
print(f"  Combinations: {len(combos)}")
print(f"  WithinTolerance mismatch: {mismatch}")
print("  Audit PASSED\n")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_groups(df_sp, metric):
    groups = []
    for sc in SCENARIOS:
        vals = df_sp.loc[df_sp["Scenario"] == sc, metric].dropna().values
        groups.append(vals)
    return groups

def epsilon_squared(H, n):
    return H / ((n**2 - 1) / (n + 1))

def omega_squared_anova(F, df_between, df_within, n_total):
    numerator = df_between * (F - 1)
    return numerator / (numerator + n_total)

def f2_welch_manual(means, variances, nobs):
    means = np.asarray(means, dtype=float)
    variances = np.asarray(variances, dtype=float)
    nobs = np.asarray(nobs, dtype=float)
    assert np.all(np.isfinite(variances)), "Variances must be finite"
    assert np.all(variances > 0), "Variances must be > 0"
    weights = nobs / variances
    w_total = weights.sum()
    w_rel = weights / w_total
    mean_weighted = w_rel @ means
    N = nobs.sum()
    f2 = np.dot(weights, (means - mean_weighted) ** 2) / N
    return f2

def hedges_g(x, y):
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return np.nan, np.nan, np.nan
    mx, my = np.mean(x), np.mean(y)
    sx, sy = np.var(x, ddof=1), np.var(y, ddof=1)
    pooled_sd = np.sqrt(((nx - 1) * sx + (ny - 1) * sy) / (nx + ny - 2))
    if pooled_sd == 0:
        return 0.0, 0.0, 0.0
    d = (mx - my) / pooled_sd
    df_total = nx + ny - 2
    j = 1 - 3 / (4 * df_total - 1)
    g = d * j
    se = np.sqrt((nx + ny) / (nx * ny) + g**2 / (2 * (nx + ny)))
    ci_lo = g - 1.96 * se
    ci_hi = g + 1.96 * se
    return g, ci_lo, ci_hi

def cliffs_delta(x, y):
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return np.nan, np.nan, np.nan
    more = sum(1 for xi in x for yi in y if xi > yi)
    less = sum(1 for xi in x for yi in y if xi < yi)
    delta = (more - less) / (nx * ny)
    rng = np.random.RandomState(SEED)
    deltas_boot = []
    for _ in range(N_BOOTSTRAP):
        bx = rng.choice(x, size=nx, replace=True)
        by = rng.choice(y, size=ny, replace=True)
        m = sum(1 for bxi in bx for byi in by if bxi > byi)
        l_ = sum(1 for bxi in bx for byi in by if bxi < byi)
        deltas_boot.append((m - l_) / (nx * ny))
    ci_lo = np.percentile(deltas_boot, 2.5)
    ci_hi = np.percentile(deltas_boot, 97.5)
    return delta, ci_lo, ci_hi

def cramers_v(chi2, n, k, r):
    return np.sqrt(chi2 / (n * min(k - 1, r - 1)))

def holm_correction(pvals):
    if len(pvals) == 0:
        return np.array([])
    _, pvals_corrected, _, _ = multipletests(pvals, alpha=ALPHA, method="holm")
    return pvals_corrected

def determine_test(metric, sp_val):
    key = (metric, sp_val)
    if key not in rekom_lookup:
        return None, None
    r = rekom_lookup[key]
    return r["uji"], r["posthoc"]

# ============================================================
# 2. UJI OMNIBUS METRIK KONTINU
# ============================================================
print(">>> 2. Uji Omnibus Metrik Kontinu")

omnibus_results = []

for metric in METRICS_CONTINUOUS:
    raw_pvals = []
    raw_rows = []

    for sp_val in SETPOINTS:
        df_sp = df[df["Setpoint_g"] == sp_val]
        groups = get_groups(df_sp, metric)
        n_per_group = [len(g) for g in groups]

        if any(len(g) < 2 for g in groups):
            raw_pvals.append(np.nan)
            raw_rows.append({
                "Metric": metric, "Setpoint_g": sp_val,
                "n_ManualCepat": n_per_group[0], "n_ManualPresisi": n_per_group[1],
                "n_FixedPID": n_per_group[2], "n_GSPID": n_per_group[3],
                "Test": "SKIPPED", "Statistic": np.nan, "df1": "",
                "df2": "", "p_raw": np.nan, "EffectSize_name": "N/A",
                "EffectSize_value": np.nan, "Note": "Insufficient data"
            })
            continue

        test_name, posthoc_name = determine_test(metric, sp_val)
        assert test_name is not None, f"No recommendation for {metric} SP{sp_val}"

        stat_val = np.nan
        p_val = np.nan
        df1, df2 = np.nan, np.nan
        es_name = ""
        es_val = np.nan

        if "Kruskal" in test_name:
            H, p_val = kruskal(*groups)
            stat_val = H
            df1 = len(groups) - 1
            n_total = sum(n_per_group)
            es_val = epsilon_squared(H, n_total)
            es_name = "rank_epsilon_squared"

        elif "Welch" in test_name:
            df_long = df_sp[[metric, "Scenario"]].dropna()
            welch_res = pg.welch_anova(data=df_long, dv=metric, between="Scenario")
            stat_val = welch_res["F"].iloc[0]
            df1 = welch_res["ddof1"].iloc[0]
            df2 = welch_res["ddof2"].iloc[0]
            p_val = welch_res["p_unc"].iloc[0]

            eta_p2 = welch_res["np2"].iloc[0]
            if -1e-12 <= eta_p2 < 0:
                eta_p2 = 0.0
                print(f"    AUDIT: eta_p2 truncated to 0 for {metric} SP{sp_val}")
            assert 0 <= eta_p2 <= 1, \
                f"eta_p2 out of range for {metric} SP{sp_val}: {eta_p2}"
            es_val = eta_p2
            es_name = "eta_p2"

        elif "ANOVA" in test_name:
            F, p_val = f_oneway(*groups)
            stat_val = F
            df1 = len(groups) - 1
            df2 = sum(n_per_group) - len(groups)
            n_total = sum(n_per_group)
            es_val = omega_squared_anova(F, df1, df2, n_total)
            if es_val < 0:
                es_val = 0.0
            es_name = "omega_squared"

        raw_pvals.append(p_val)
        raw_rows.append({
            "Metric": metric, "Setpoint_g": sp_val,
            "n_ManualCepat": n_per_group[0], "n_ManualPresisi": n_per_group[1],
            "n_FixedPID": n_per_group[2], "n_GSPID": n_per_group[3],
            "Test": test_name, "Statistic": round(stat_val, 4),
            "df1": df1 if not np.isnan(df1) else "",
            "df2": round(df2, 2) if not np.isnan(df2) else "",
            "p_raw": p_val, "EffectSize_name": es_name,
            "EffectSize_value": round(es_val, 6) if np.isfinite(es_val) else es_val,
        })

    valid_mask = [not np.isnan(p) for p in raw_pvals]
    valid_pvals = [p for p in raw_pvals if not np.isnan(p)]
    if valid_pvals:
        corrected = holm_correction(valid_pvals)
        j = 0
        for i in range(len(raw_rows)):
            if valid_mask[i]:
                raw_rows[i]["p_holm"] = round(corrected[j], 6)
                raw_rows[i]["Significant_holm"] = corrected[j] < ALPHA
                j += 1
            else:
                raw_rows[i]["p_holm"] = np.nan
                raw_rows[i]["Significant_holm"] = False

    omnibus_results.extend(raw_rows)

df_omnibus = pd.DataFrame(omnibus_results)
print(f"  Omnibus results: {len(df_omnibus)} rows")
for _, r in df_omnibus.iterrows():
    sig = "***" if r.get("Significant_holm") else ""
    p_r = r['p_raw']
    p_h = r.get('p_holm', np.nan)
    p_r_s = f"{p_r:.4f}" if np.isfinite(p_r) else "N/A"
    p_h_s = f"{p_h:.4f}" if isinstance(p_h, float) and np.isfinite(p_h) else "N/A"
    es_v = r['EffectSize_value']
    es_s = f"{es_v:.4f}" if isinstance(es_v, float) and np.isfinite(es_v) else "N/A"
    print(f"    {r['Metric']:20s} SP{r['Setpoint_g']:2d}: {r['Test']:20s} "
          f"stat={r['Statistic']}  p_raw={p_r_s}  p_holm={p_h_s}  "
          f"{r['EffectSize_name']}={es_s} {sig}")
print()

# ============================================================
# 3. POST-HOC METRIK KONTINU
# ============================================================
print(">>> 3. Post-hoc Metrik Kontinu")

posthoc_results = []
pairs = list(combinations(range(4), 2))
pair_names = [(SCENARIOS[i], SCENARIOS[j]) for i, j in pairs]

for _, omni in df_omnibus.iterrows():
    if not omni.get("Significant_holm", False):
        continue
    if omni["Test"] == "SKIPPED":
        continue

    metric = omni["Metric"]
    sp_val = omni["Setpoint_g"]
    test_name = omni["Test"]
    df_sp = df[df["Setpoint_g"] == sp_val]
    groups = get_groups(df_sp, metric)

    if "Kruskal" in test_name:
        df_long = df_sp[[metric, "Scenario"]].dropna()
        dunn_res = sp.posthoc_dunn(
            df_long, val_col=metric, group_col="Scenario", p_adjust="holm"
        )
        for (sc_a, sc_b) in pair_names:
            p_adj = dunn_res.loc[sc_a, sc_b]
            idx_a, idx_b = SCENARIOS.index(sc_a), SCENARIOS.index(sc_b)
            ga, gb = groups[idx_a], groups[idx_b]
            delta, ci_lo, ci_hi = cliffs_delta(ga, gb)
            direction = f"{sc_a} > {sc_b}" if np.median(ga) > np.median(gb) else f"{sc_b} >= {sc_a}"
            posthoc_results.append({
                "Metric": metric, "Setpoint_g": sp_val,
                "Omnibus_test": test_name, "PostHoc_test": "Dunn-Holm",
                "Group_A": sc_a, "Group_B": sc_b,
                "p_adjusted": round(p_adj, 6), "Significant": p_adj < ALPHA,
                "EffectSize_name": "Cliff_delta",
                "EffectSize_value": round(delta, 4),
                "CI_lo": round(ci_lo, 4), "CI_hi": round(ci_hi, 4),
                "Direction": direction,
            })

    elif "Welch" in test_name:
        df_long = df_sp[[metric, "Scenario"]].dropna()
        gh_res = pg.pairwise_gameshowell(data=df_long, dv=metric, between="Scenario")
        for _, gh_row in gh_res.iterrows():
            sc_a, sc_b = gh_row["A"], gh_row["B"]
            idx_a, idx_b = SCENARIOS.index(sc_a), SCENARIOS.index(sc_b)
            ga, gb = groups[idx_a], groups[idx_b]
            g_val, ci_lo, ci_hi = hedges_g(ga, gb)
            direction = f"{sc_a} > {sc_b}" if np.mean(ga) > np.mean(gb) else f"{sc_b} >= {sc_a}"
            posthoc_results.append({
                "Metric": metric, "Setpoint_g": sp_val,
                "Omnibus_test": test_name, "PostHoc_test": "Games-Howell",
                "Group_A": sc_a, "Group_B": sc_b,
                "p_adjusted": round(gh_row["pval"], 6),
                "Significant": gh_row["pval"] < ALPHA,
                "EffectSize_name": "Hedges_g",
                "EffectSize_value": round(g_val, 4),
                "CI_lo": round(ci_lo, 4), "CI_hi": round(ci_hi, 4),
                "Direction": direction,
            })

    elif "ANOVA" in test_name:
        df_long = df_sp[[metric, "Scenario"]].dropna()
        tukey_res = pg.pairwise_tukey(data=df_long, dv=metric, between="Scenario")
        for _, t_row in tukey_res.iterrows():
            sc_a, sc_b = t_row["A"], t_row["B"]
            idx_a, idx_b = SCENARIOS.index(sc_a), SCENARIOS.index(sc_b)
            ga, gb = groups[idx_a], groups[idx_b]
            g_val, ci_lo, ci_hi = hedges_g(ga, gb)
            direction = f"{sc_a} > {sc_b}" if np.mean(ga) > np.mean(gb) else f"{sc_b} >= {sc_a}"
            posthoc_results.append({
                "Metric": metric, "Setpoint_g": sp_val,
                "Omnibus_test": test_name, "PostHoc_test": "Tukey HSD",
                "Group_A": sc_a, "Group_B": sc_b,
                "p_adjusted": round(t_row["p_tukey"], 6),
                "Significant": t_row["p_tukey"] < ALPHA,
                "EffectSize_name": "Hedges_g",
                "EffectSize_value": round(g_val, 4),
                "CI_lo": round(ci_lo, 4), "CI_hi": round(ci_hi, 4),
                "Direction": direction,
            })

df_posthoc = pd.DataFrame(posthoc_results)
print(f"  Post-hoc results: {len(df_posthoc)} rows")
if len(df_posthoc) > 0:
    for _, r in df_posthoc.iterrows():
        sig = "***" if r["Significant"] else ""
        print(f"    {r['Metric']:20s} SP{r['Setpoint_g']:2d} {r['Group_A']:16s} vs {r['Group_B']:16s}: "
              f"p={r['p_adjusted']:.4f} {r['EffectSize_name']}={r['EffectSize_value']:.3f} "
              f"[{r['CI_lo']:.3f}, {r['CI_hi']:.3f}] {sig}")
print()

# ============================================================
# 4. KONSISTENSI FinalError_g (Brown-Forsythe)
# ============================================================
print(">>> 4. Konsistensi FinalError_g")

consistency_results = []
bf_pvals_raw = []
bf_rows = []

for sp_val in SETPOINTS:
    df_sp = df[df["Setpoint_g"] == sp_val]
    groups = get_groups(df_sp, "FinalError_g")
    n_per = [len(g) for g in groups]
    bf_stat, bf_p = levene(*groups, center="median")
    sds = [np.std(g, ddof=1) for g in groups]
    varis = [np.var(g, ddof=1) for g in groups]
    var_ratio = max(varis) / min(varis) if min(varis) > 0 else np.inf
    min_var_idx = np.argmin(varis)
    bf_pvals_raw.append(bf_p)
    bf_rows.append({
        "Setpoint_g": sp_val, "BF_statistic": round(bf_stat, 4),
        "df1": len(groups) - 1, "df2": sum(n_per) - len(groups),
        "p_raw": bf_p,
        "SD_ManualCepat": round(sds[0], 4), "SD_ManualPresisi": round(sds[1], 4),
        "SD_FixedPID": round(sds[2], 4), "SD_GSPID": round(sds[3], 4),
        "Var_ManualCepat": round(varis[0], 4), "Var_ManualPresisi": round(varis[1], 4),
        "Var_FixedPID": round(varis[2], 4), "Var_GSPID": round(varis[3], 4),
        "VarRatio_max_min": round(var_ratio, 4),
        "MinVar_scenario": SCENARIOS[min_var_idx],
    })

bf_holm = holm_correction(bf_pvals_raw)
for i, row in enumerate(bf_rows):
    row["p_holm"] = round(bf_holm[i], 6)
    row["Significant_holm"] = bf_holm[i] < ALPHA
    consistency_results.append(row)

print("  Brown-Forsythe Omnibus:")
for r in consistency_results:
    sig = "***" if r["Significant_holm"] else ""
    print(f"    SP{r['Setpoint_g']}: F={r['BF_statistic']:.4f} p_raw={r['p_raw']:.4f} "
          f"p_holm={r['p_holm']:.4f} VarRatio={r['VarRatio_max_min']:.2f} "
          f"MinVar={r['MinVar_scenario']} {sig}")

# Post-hoc pairwise BF dihapus (keputusan 2026-07-17):
# f_oneway pada deviasi absolut tidak memiliki nama standar dalam literatur;
# tidak dapat dikutip langsung. BF omnibus + tabel SD deskriptif sudah cukup.

df_consistency = pd.DataFrame(consistency_results)
print()

# ============================================================
# 5. PROPORSI WithinTolerance (Monte Carlo Exact Test)
# ============================================================
print(">>> 5. Proporsi WithinTolerance (Monte Carlo exact)")
# N_MC already declared in CONFIG (baris 42)

def monte_carlo_4x2_exact(table, n_sim=N_MC, seed=SEED):
    """Monte Carlo exact test for 4x2 table (Fisher-Freeman-Halton equivalent).
    Fixed row & column marginals. Test statistic: Pearson chi-square."""
    table = np.asarray(table, dtype=int)
    chi2_obs, _, _, expected = chi2_contingency(table, correction=False)
    row_totals = table.sum(axis=1)
    col_total_1 = table[:, 1].sum()
    n_total = row_totals.sum()
    row_cumsum = np.concatenate([[0], np.cumsum(row_totals)])
    sim_rng = np.random.RandomState(seed)
    count_extreme = 0
    for _ in range(n_sim):
        within_idx = sim_rng.choice(n_total, size=col_total_1, replace=False)
        within_mask = np.zeros(n_total, dtype=bool)
        within_mask[within_idx] = True
        sim_table = np.zeros((4, 2), dtype=int)
        for r_idx in range(4):
            a, b = row_cumsum[r_idx], row_cumsum[r_idx + 1]
            sim_table[r_idx, 1] = within_mask[a:b].sum()
            sim_table[r_idx, 0] = row_totals[r_idx] - sim_table[r_idx, 1]
        chi2_sim, _, _, _ = chi2_contingency(sim_table, correction=False)
        if chi2_sim >= chi2_obs:
            count_extreme += 1
    p_mc = (count_extreme + 1) / (n_sim + 1)
    return chi2_obs, p_mc, expected, count_extreme

proportion_results = []
proportion_posthoc = []
prop_pvals_mc = []
prop_rows = []

for sp_val in SETPOINTS:
    df_sp = df[df["Setpoint_g"] == sp_val]
    ct = pd.crosstab(df_sp["Scenario"], df_sp["WithinTolerance"])
    for col in [0, 1]:
        if col not in ct.columns:
            ct[col] = 0
    ct = ct[[0, 1]]
    ct = ct.reindex(SCENARIOS)
    table = ct.values
    n_total = table.sum()

    # Diagnostic: asymptotic chi²
    chi2_asym, p_asym, dof, expected = chi2_contingency(table, correction=False)
    min_expected = expected.min()
    V = cramers_v(chi2_asym, n_total, ct.shape[0], ct.shape[1])

    # Monte Carlo exact
    chi2_obs, p_mc, _, count_extreme = monte_carlo_4x2_exact(table, n_sim=N_MC, seed=SEED)

    prop_pvals_mc.append(p_mc)

    proportions = {}
    for sc in SCENARIOS:
        sc_data = df_sp[df_sp["Scenario"] == sc]
        proportions[sc] = sc_data["WithinTolerance"].mean()

    prop_rows.append({
        "Setpoint_g": sp_val,
        "Test": "Monte Carlo exact (Fisher-Freeman-Halton equivalent)",
        "Statistic": round(chi2_asym, 4),
        "df": dof,
        "p_asymptotic": round(p_asym, 6),
        "p_MonteCarlo": round(p_mc, 6),
        "N_MC": N_MC, "Seed": SEED,
        "Count_extreme": count_extreme,
        "MinExpected": round(min_expected, 2),
        "CramersV": round(V, 4),
        "Prop_ManualCepat": round(proportions["Manual Cepat"], 2),
        "Prop_ManualPresisi": round(proportions["Manual Presisi"], 2),
        "Prop_FixedPID": round(proportions["Fixed PID"], 2),
        "Prop_GSPID": round(proportions["GS PID"], 2),
        "n_ManualCepat_within": int(ct.loc["Manual Cepat", 1]),
        "n_ManualPresisi_within": int(ct.loc["Manual Presisi", 1]),
        "n_FixedPID_within": int(ct.loc["Fixed PID", 1]),
        "n_GSPID_within": int(ct.loc["GS PID", 1]),
    })

mc_holm = holm_correction(prop_pvals_mc)
for i, row in enumerate(prop_rows):
    row["p_holm"] = round(mc_holm[i], 6)
    row["Significant_holm"] = mc_holm[i] < ALPHA
    proportion_results.append(row)

print("  Omnibus (Monte Carlo exact, seed=42, N=100k):")
for r in proportion_results:
    sig = "***" if r["Significant_holm"] else ""
    print(f"    SP{r['Setpoint_g']}: chi2_asym={r['Statistic']:.4f} p_asym={r['p_asymptotic']} "
          f"p_MC={r['p_MonteCarlo']} p_holm={r['p_holm']:.4f} V={r['CramersV']:.3f} "
          f"count_extreme={r['Count_extreme']} {sig}")

# Post-hoc Fisher if omnibus significant
for r in proportion_results:
    if not r["Significant_holm"]:
        continue
    sp_val = r["Setpoint_g"]
    df_sp = df[df["Setpoint_g"] == sp_val]
    pair_pvals_prop = []
    pair_rows_prop = []
    for sc_a, sc_b in pair_names:
        da = df_sp[df_sp["Scenario"] == sc_a]["WithinTolerance"]
        db = df_sp[df_sp["Scenario"] == sc_b]["WithinTolerance"]
        ct2x2 = np.array([
            [int((da == 1).sum()), int((da == 0).sum())],
            [int((db == 1).sum()), int((db == 0).sum())],
        ])
        odds_ratio, p_fisher = fisher_exact(ct2x2)
        prop_a, prop_b = da.mean(), db.mean()
        pair_pvals_prop.append(p_fisher)
        pair_rows_prop.append({
            "Setpoint_g": sp_val, "Group_A": sc_a, "Group_B": sc_b,
            "Prop_A": round(prop_a, 2), "Prop_B": round(prop_b, 2),
            "Prop_diff": round(prop_a - prop_b, 2),
            "OddsRatio": round(odds_ratio, 4), "p_fisher_raw": p_fisher,
        })
    ph_holm = holm_correction(pair_pvals_prop)
    for k, pr in enumerate(pair_rows_prop):
        pr["p_holm"] = round(ph_holm[k], 6)
        pr["Significant_holm"] = ph_holm[k] < ALPHA
        proportion_posthoc.append(pr)
        sig = "***" if pr["Significant_holm"] else ""
        print(f"    PostHoc SP{sp_val}: {pr['Group_A']:16s} vs {pr['Group_B']:16s} "
              f"diff={pr['Prop_diff']:.2f} OR={pr['OddsRatio']:.3f} p_holm={pr['p_holm']:.4f} {sig}")

df_proportion = pd.DataFrame(proportion_results)
df_proportion_ph = pd.DataFrame(proportion_posthoc)
print()

# ============================================================
# 6. SettlingTime_s KONDISIONAL (deskriptif saja)
# ============================================================
print(">>> 6. SettlingTime_s Kondisional — Deskriptif")
settling_results = []
for sp_val in SETPOINTS:
    df_sp = df[df["Setpoint_g"] == sp_val]
    for sc in SCENARIOS:
        vals = df_sp.loc[df_sp["Scenario"] == sc, "SettlingTime_s"].dropna()
        if len(vals) > 0:
            q1, q3 = np.percentile(vals, [25, 75])
            median = np.median(vals)
            settling_results.append({
                "Setpoint_g": sp_val, "Scenario": sc,
                "n_available": len(vals), "n_total": 10,
                "Median": median, "Q1": q1, "Q3": q3, "IQR": q3 - q1,
            })
            print(f"    SP{sp_val} {sc:16s}: n={len(vals):2d}/10 median={median:.2f} "
                  f"IQR=[{q1:.2f}, {q3:.2f}]")
        else:
            settling_results.append({
                "Setpoint_g": sp_val, "Scenario": sc,
                "n_available": 0, "n_total": 10,
                "Median": np.nan, "Q1": np.nan, "Q3": np.nan, "IQR": np.nan,
            })
            print(f"    SP{sp_val} {sc:16s}: n= 0/10")
df_settling = pd.DataFrame(settling_results)
print()

# ============================================================
# 7. BridgingCount DESKRIPTIF
# ============================================================
print(">>> 7. BridgingCount Deskriptif")
bridging_results = []
for sp_val in SETPOINTS:
    df_sp = df[df["Setpoint_g"] == sp_val]
    for sc in SCENARIOS:
        vals = df_sp.loc[df_sp["Scenario"] == sc, "BridgingCount"].values
        bridging_results.append({
            "Setpoint_g": sp_val, "Scenario": sc, "n": len(vals),
            "Total_events": int(vals.sum()), "Median": np.median(vals),
            "IQR_lo": np.percentile(vals, 25), "IQR_hi": np.percentile(vals, 75),
            "Min": int(vals.min()), "Max": int(vals.max()),
            "Prop_nonzero": round((vals > 0).mean(), 2),
        })
df_bridging = pd.DataFrame(bridging_results)
print(df_bridging.to_string(index=False))
print()

# ============================================================
# 8. SAVE CSVs
# ============================================================
# ── Validasi seluruh DataFrame sebelum simpan ──
assert len(df_omnibus)       == 16,  f"omnibus rows: {len(df_omnibus)}"
assert len(df_consistency)   == 4,   f"consistency rows: {len(df_consistency)}"
assert len(df_proportion)    == 4,   f"proportion rows: {len(df_proportion)}"
assert len(df_settling)      == 16,  f"settling rows: {len(df_settling)}"
assert len(df_bridging)      == 16,  f"bridging rows: {len(df_bridging)}"
if len(df_proportion_ph) > 0:
    assert len(df_proportion_ph) == 12, f"proportion posthoc rows: {len(df_proportion_ph)}"
if len(df_posthoc) > 0:
    n_sig = df_omnibus["Significant_holm"].sum()
    assert len(df_posthoc) == n_sig * 6, \
        f"posthoc rows: expected {n_sig*6}, got {len(df_posthoc)}"
print("  validate_frames PASSED")

# Validasi struktur omnibus (umum)
assert len(df_omnibus) == 16, f"Baris omnibus salah: {len(df_omnibus)}"
_test_counts = df_omnibus["Test"].value_counts().to_dict()
assert _test_counts.get("Kruskal-Wallis") == 13, f"KW count: {_test_counts}"
assert _test_counts.get("Welch ANOVA") == 3, f"Welch count: {_test_counts}"
_welch = df_omnibus[df_omnibus["Test"] == "Welch ANOVA"]
assert set(_welch["EffectSize_name"]) == {"eta_p2"}, \
    f"Welch effect name salah: {set(_welch['EffectSize_name'])}"
assert _welch["EffectSize_value"].between(0, 1).all(), "eta_p2 di luar [0,1]"
assert set(df_omnibus[df_omnibus["Test"] == "Kruskal-Wallis"]["EffectSize_name"]) == \
    {"rank_epsilon_squared"}, "KW effect name salah"

# Validasi snapshot nilai final
_expected_eta = {
    ("Duration_s", 25): 0.597385,
    ("RiseTime_10_90_s", 25): 0.642618,
    ("RiseTime_10_90_s", 30): 0.659108,
}
for (_m, _s), _exp in _expected_eta.items():
    _row = _welch[(_welch["Metric"] == _m) & (_welch["Setpoint_g"] == _s)]
    assert len(_row) == 1, f"Welch row hilang: {_m} SP{_s}"
    assert np.isclose(float(_row.iloc[0]["EffectSize_value"]), _exp, atol=1e-6), \
        f"eta_p2 mismatch {_m} SP{_s}: expected {_exp}, got {_row.iloc[0]['EffectSize_value']}"
print("  validate_omnibus PASSED")
df_omnibus.to_csv(OUTPUT_DIR / "hasil_omnibus_tahap3.csv", index=False)
df_posthoc.to_csv(OUTPUT_DIR / "hasil_posthoc_tahap3.csv", index=False)
df_consistency.to_csv(OUTPUT_DIR / "hasil_konsistensi_finalerror_omnibus.csv", index=False)
# Hapus artefak usang agar tidak terbaca lagi oleh tahap berikutnya.
(OUTPUT_DIR / "hasil_konsistensi_finalerror_posthoc.csv").unlink(missing_ok=True)
df_proportion.to_csv(OUTPUT_DIR / "hasil_proporsi_within_tolerance_omnibus.csv", index=False)
df_proportion_ph.to_csv(OUTPUT_DIR / "hasil_proporsi_within_tolerance_posthoc.csv", index=False)
df_settling.to_csv(OUTPUT_DIR / "hasil_settlingtime_deskriptif.csv", index=False)
df_bridging.to_csv(OUTPUT_DIR / "hasil_bridging_deskriptif.csv", index=False)
print("  All CSV saved")
print()

# ============================================================
# 9. SAVE XLSX
# ============================================================
print(">>> 9. Menyimpan XLSX")
xlsx_path = OUTPUT_DIR / "hasil_lengkap_tahap3.xlsx"
with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    cover = pd.DataFrame([{"Item": k, "Value": str(v)} for k, v in VERSION_INFO.items()])
    cover.to_excel(writer, sheet_name="Info", index=False)
    df_omnibus.to_excel(writer, sheet_name="Omnibus", index=False)
    if len(df_posthoc) > 0:
        df_posthoc.to_excel(writer, sheet_name="PostHoc", index=False)
    df_consistency.to_excel(writer, sheet_name="Konsistensi_Omnibus", index=False)
    df_proportion.to_excel(writer, sheet_name="Proporsi_Omnibus", index=False)
    if len(df_proportion_ph) > 0:
        df_proportion_ph.to_excel(writer, sheet_name="Proporsi_PostHoc", index=False)
    df_settling.to_excel(writer, sheet_name="Settling_Deskriptif", index=False)
    df_bridging.to_excel(writer, sheet_name="Bridging", index=False)
print(f"  Saved: {xlsx_path.name}")
print()



# ============================================================
# 11. LAPORAN DOCX UTAMA + LAMPIRAN TEKNIS
# ============================================================
print(">>> 11. Menyimpan Laporan Utama dan Lampiran Teknis DOCX")
try:
    from tahap3_generate_reports import generate_reports, validate_report_files
except ModuleNotFoundError as exc:
    if exc.name == "tahap3_generate_reports":
        raise RuntimeError(
            "Modul tahap3_generate_reports.py tidak ditemukan. "
            "Artefak numerik mungkin sudah tersimpan, tetapi pipeline "
            "belum selesai dan laporan belum dapat dianggap final."
        ) from exc
    raise

report_paths = generate_reports(
    results={
        "assumption_residual":    df_shapiro_residual,
        "assumption_homogeneity": df_homogeneity,
        "test_recommendation":    df_recommendation,
        "omnibus":            df_omnibus,
        "posthoc":            df_posthoc,
        "consistency":        df_consistency,
        "proportion_omnibus": df_proportion,
        "proportion_posthoc": df_proportion_ph,
        "settling":           df_settling,
        "bridging":           df_bridging,
        "environment":        VERSION_INFO,
        "config": {
            "alpha":         ALPHA,
            "seed":          SEED,
            "n_monte_carlo": N_MC,
            "n_bootstrap":   N_BOOTSTRAP,
        },
    },
    output_dir=OUTPUT_DIR,
)
for p in report_paths:
    print(f"  Saved: {p.name}")
validate_report_files(report_paths)
print("  Report validation PASSED")
print()

# ============================================================
# 12. VERIFICATION
# ============================================================
print(">>> 12. Verifikasi Final")

for _, omni in df_omnibus.iterrows():
    if omni.get("Significant_holm") and omni["Test"] != "SKIPPED":
        n_ph = len(df_posthoc[(df_posthoc["Metric"] == omni["Metric"]) & (df_posthoc["Setpoint_g"] == omni["Setpoint_g"])])
        assert n_ph == 6, f"Post-hoc count != 6: {omni['Metric']} SP{omni['Setpoint_g']} got {n_ph}"

assert "SettlingTime_s" not in set(df_omnibus["Metric"]), "SettlingTime_s tidak boleh masuk omnibus"
assert "SettlingTime_s" not in set(df_posthoc["Metric"]), "SettlingTime_s tidak boleh masuk post-hoc"
assert len(df_settling) == len(SETPOINTS) * len(SCENARIOS), "Ringkasan SettlingTime_s tidak lengkap"

print("  All checks PASSED")
print()
print("=" * 60)
print("TAHAP 3 SELESAI")
print("=" * 60)
