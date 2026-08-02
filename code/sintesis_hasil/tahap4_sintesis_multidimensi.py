#!/usr/bin/env python3
"""
Tahap 4 - Sintesis Multidimensi
Menghitung profil primer (ranking) dan profil tambahan kondisional.
Output: tahap4_profil_primer.csv, tahap4_profil_tambahan_kondisional.csv
"""

import sys
import platform
import hashlib
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================
BASE = Path(__file__).resolve().parents[2]
DATA_ROOT = BASE
TAHAP3 = BASE / "hasil" / "analisis_inferensial"
SINTESIS = BASE / "hasil" / "sintesis_hasil"
import os as _os
_raw_out = _os.environ.get("PIPELINE_OUTPUT_DIR",
           str(BASE / "hasil" / "sintesis_hasil"))
OUTPUT = (Path(_raw_out) if Path(_raw_out).is_absolute()
          else BASE / _raw_out).resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)

MASTER_DATASET = DATA_ROOT / "data" / "pengujian_final" / "master_dataset_160.csv"
OMNIBUS_CSV = TAHAP3 / "hasil_omnibus_tahap3.csv"
POSTHOC_CSV = TAHAP3 / "hasil_posthoc_tahap3.csv"
CONSISTENCY_OMNIBUS_CSV = TAHAP3 / "hasil_konsistensi_finalerror_omnibus.csv"
TOLERANCE_OMNIBUS_CSV = TAHAP3 / "hasil_proporsi_within_tolerance_omnibus.csv"
TOLERANCE_POSTHOC_CSV = TAHAP3 / "hasil_proporsi_within_tolerance_posthoc.csv"
BRIDGING_CSV = SINTESIS / "hasil_bridging_deskriptif.csv"

TAHAP3_FILES = [
    OMNIBUS_CSV, POSTHOC_CSV, CONSISTENCY_OMNIBUS_CSV,
    TOLERANCE_OMNIBUS_CSV, TOLERANCE_POSTHOC_CSV
]
SCENARIOS = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS = [15, 20, 25, 30]

VERSION_INFO = {
    "Python": sys.version.split()[0],
    "pandas": pd.__version__,
    "numpy": np.__version__,
    "OS": platform.platform(),
    "Timestamp": datetime.now().isoformat(),
    "Revision": "Paket Lengkap dengan Matriks Dominasi dan Workbook Extended"
}

# ============================================================
# SHA-256 HASHING
# ============================================================

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    if not filepath.exists(): return None
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_tahap3_integrity(hashes_before):
    mismatches = []
    for filepath, hash_before in hashes_before.items():
        hash_after = compute_sha256(filepath)
        if hash_before != hash_after:
            mismatches.append(filepath.name)
    return len(mismatches) == 0, mismatches


def rank_within_group(series, ascending=True):
    return series.rank(method="average", ascending=ascending)



def correction_method(posthoc_test):
    mapping = {"Dunn-Holm": "Holm", "Tukey HSD": "Tukey HSD", "Games-Howell": "Games-Howell"}
    assert posthoc_test in mapping, f"PostHoc_test tidak dikenal: {posthoc_test}"
    return mapping[posthoc_test]


def assert_close(actual, expected, label):
    assert np.isclose(float(actual), float(expected), rtol=1e-12, atol=1e-12), label

# ============================================================
# MAIN PIPELINE
# ============================================================

print("=" * 70)
print("TAHAP 4 - SINTESIS MULTIDIMENSI")
print("=" * 70)
print()

print(">>> 0. Computing SHA-256 hashes of Tahap 3 inputs")
tahap3_hashes_before = {}
for filepath in TAHAP3_FILES:
    if filepath.exists():
        tahap3_hashes_before[filepath] = compute_sha256(filepath)

print(">>> 2. Loading data sources")
df_master = pd.read_csv(MASTER_DATASET)
df_omnibus = pd.read_csv(OMNIBUS_CSV)
df_posthoc = pd.read_csv(POSTHOC_CSV)
df_cons_omni = pd.read_csv(CONSISTENCY_OMNIBUS_CSV)
df_tol_omni = pd.read_csv(TOLERANCE_OMNIBUS_CSV)
df_tol_ph = pd.read_csv(TOLERANCE_POSTHOC_CSV)
df_bridging = pd.read_csv(BRIDGING_CSV)

print(">>> 3. Validating structure and integrity")
assert len(df_master) == 160, f"Expected 160 trials, got {len(df_master)}"
valid_values = df_master.Valid.astype(str).str.upper()
assert valid_values.isin(["TRUE", "1"]).all(), "Not all trials Valid==TRUE"
assert (df_master.StopReason == "TARGET").all(), "Not all trials StopReason==TARGET"

design_check = df_master.groupby(["Scenario", "Setpoint_g"]).size()
assert len(design_check) == 16 and (design_check == 10).all(), "Design not balanced 4x4x10"

assert np.allclose(
    df_master["AbsError_pct"].to_numpy(float),
    df_master["FinalError_pct"].abs().to_numpy(float),
    rtol=1e-12,
    atol=1e-12,
), "AbsError_pct != abs(FinalError_pct)"
df_master["WithinTolerance"] = (df_master.FinalError_pct.abs() <= 5).astype(int)
df_master["HasSettling"] = df_master.SettlingTime_s.notna().astype(int)
assert (df_master.WithinTolerance == df_master.HasSettling).all(), "WithinTolerance <-> SettlingTime availability mismatch"

print(">>> 4. Computing primary summaries per scenario-setpoint")
summary_rows = []
for scenario in SCENARIOS:
    for sp in SETPOINTS:
        subset = df_master[(df_master.Scenario == scenario) & (df_master.Setpoint_g == sp)]
        
        summary_rows.append({
            "Scenario": scenario,
            "Setpoint_g": sp,
            "n": len(subset),
            "MAE_pct": subset.AbsError_pct.mean(),
            "Median_MAE_pct": subset.AbsError_pct.median(),
            "SD_MAE_pct": subset.AbsError_pct.std(ddof=1),
            "Var_MAE_pct": subset.AbsError_pct.var(ddof=1),
            "Q1_MAE_pct": subset.AbsError_pct.quantile(0.25),
            "Q3_MAE_pct": subset.AbsError_pct.quantile(0.75),
            "IQR_MAE_pct": subset.AbsError_pct.quantile(0.75) - subset.AbsError_pct.quantile(0.25),
            
            "MeanOvershoot_pct": subset.MaxOvershoot_pct.mean(),
            "Median_Overshoot_pct": subset.MaxOvershoot_pct.median(),
            "SD_Overshoot_pct": subset.MaxOvershoot_pct.std(ddof=1),
            "Var_Overshoot_pct": subset.MaxOvershoot_pct.var(ddof=1),
            "Q1_Overshoot_pct": subset.MaxOvershoot_pct.quantile(0.25),
            "Q3_Overshoot_pct": subset.MaxOvershoot_pct.quantile(0.75),
            "IQR_Overshoot_pct": subset.MaxOvershoot_pct.quantile(0.75) - subset.MaxOvershoot_pct.quantile(0.25),
            
            "MeanDuration_s": subset.Duration_s.mean(),
            "Median_Duration_s": subset.Duration_s.median(),
            "SD_Duration_s": subset.Duration_s.std(ddof=1),
            "Var_Duration_s": subset.Duration_s.var(ddof=1),
            "Q1_Duration_s": subset.Duration_s.quantile(0.25),
            "Q3_Duration_s": subset.Duration_s.quantile(0.75),
            "IQR_Duration_s": subset.Duration_s.quantile(0.75) - subset.Duration_s.quantile(0.25),
            
            "MeanFinalError_g": subset.FinalError_g.mean(),
            "Median_FinalError_g": subset.FinalError_g.median(),
            "SD_FinalError_g": subset.FinalError_g.std(ddof=1),
            "Var_FinalError_g": subset.FinalError_g.var(ddof=1),
            "Q1_FinalError_g": subset.FinalError_g.quantile(0.25),
            "Q3_FinalError_g": subset.FinalError_g.quantile(0.75),
            "IQR_FinalError_g": subset.FinalError_g.quantile(0.75) - subset.FinalError_g.quantile(0.25),
        })

df_summary = pd.DataFrame(summary_rows)

print(">>> 5. Computing rankings per metric-setpoint")
ranking_rows = []
for sp in SETPOINTS:
    subset = df_summary[df_summary.Setpoint_g == sp].copy()
    subset["Rank_MAE"] = rank_within_group(subset.MAE_pct)
    subset["Rank_Overshoot"] = rank_within_group(subset.MeanOvershoot_pct)
    subset["Rank_Duration"] = rank_within_group(subset.MeanDuration_s)
    subset["Rank_SD"] = rank_within_group(subset.SD_FinalError_g)
    
    for _, row in subset.iterrows():
        ranking_rows.append({
            "Setpoint_g": sp, "Scenario": row.Scenario, "n": row.n,
            "MAE_pct": row.MAE_pct, "Median_MAE_pct": row.Median_MAE_pct, "SD_MAE_pct": row.SD_MAE_pct, 
            "Var_MAE_pct": row.Var_MAE_pct, "Q1_MAE_pct": row.Q1_MAE_pct, "Q3_MAE_pct": row.Q3_MAE_pct, 
            "IQR_MAE_pct": row.IQR_MAE_pct, "Rank_MAE": row.Rank_MAE,
            
            "MeanOvershoot_pct": row.MeanOvershoot_pct, "Median_Overshoot_pct": row.Median_Overshoot_pct, 
            "SD_Overshoot_pct": row.SD_Overshoot_pct, "Var_Overshoot_pct": row.Var_Overshoot_pct, 
            "Q1_Overshoot_pct": row.Q1_Overshoot_pct, "Q3_Overshoot_pct": row.Q3_Overshoot_pct, 
            "IQR_Overshoot_pct": row.IQR_Overshoot_pct, "Rank_Overshoot": row.Rank_Overshoot,
            
            "MeanDuration_s": row.MeanDuration_s, "Median_Duration_s": row.Median_Duration_s, 
            "SD_Duration_s": row.SD_Duration_s, "Var_Duration_s": row.Var_Duration_s, 
            "Q1_Duration_s": row.Q1_Duration_s, "Q3_Duration_s": row.Q3_Duration_s, 
            "IQR_Duration_s": row.IQR_Duration_s, "Rank_Duration": row.Rank_Duration,
            
            "MeanFinalError_g": row.MeanFinalError_g, "Median_FinalError_g": row.Median_FinalError_g,
            "SD_FinalError_g": row.SD_FinalError_g, "Var_FinalError_g": row.Var_FinalError_g, 
            "Q1_FinalError_g": row.Q1_FinalError_g, "Q3_FinalError_g": row.Q3_FinalError_g, 
            "IQR_FinalError_g": row.IQR_FinalError_g, "Rank_SD": row.Rank_SD
        })

df_ranking = pd.DataFrame(ranking_rows)

print(">>> 6. Computing additional and conditional profiles")
# RiseTime_10_90_s
risetime_rows = []
for scenario in SCENARIOS:
    for sp in SETPOINTS:
        subset = df_master[(df_master.Scenario == scenario) & (df_master.Setpoint_g == sp)]
        risetime_rows.append({
            "Scenario": scenario, "Setpoint_g": sp, "RiseTime_role": "Tambahan",
            "RiseTime_n": len(subset),
            "RiseTime_mean": subset.RiseTime_10_90_s.mean(),
            "RiseTime_median": subset.RiseTime_10_90_s.median(),
            "RiseTime_SD": subset.RiseTime_10_90_s.std(ddof=1),
            "RiseTime_Q1": subset.RiseTime_10_90_s.quantile(0.25),
            "RiseTime_Q3": subset.RiseTime_10_90_s.quantile(0.75),
            "RiseTime_IQR": subset.RiseTime_10_90_s.quantile(0.75) - subset.RiseTime_10_90_s.quantile(0.25),
        })
df_risetime = pd.DataFrame(risetime_rows)

# WithinTolerance and SettlingTime_s
tolerance_rows = []
for scenario in SCENARIOS:
    for sp in SETPOINTS:
        subset = df_master[(df_master.Scenario == scenario) & (df_master.Setpoint_g == sp)]
        n_within = subset.WithinTolerance.sum()
        settling_subset = subset[subset.WithinTolerance == 1]
        
        tolerance_rows.append({
            "Scenario": scenario, "Setpoint_g": sp, "Within_role": "Tambahan",
            "Within_total_n": len(subset), "Within_n": n_within, "Within_prop": n_within / len(subset),
            "Settling_role": "Kondisional", "Settling_subset_n": len(settling_subset), 
            "Settling_subset_prop": len(settling_subset) / len(subset),
            "Settling_median": settling_subset.SettlingTime_s.median() if len(settling_subset) > 0 else np.nan,
            "Settling_Q1": settling_subset.SettlingTime_s.quantile(0.25) if len(settling_subset) > 0 else np.nan,
            "Settling_Q3": settling_subset.SettlingTime_s.quantile(0.75) if len(settling_subset) > 0 else np.nan,
            "Settling_IQR": (settling_subset.SettlingTime_s.quantile(0.75) - settling_subset.SettlingTime_s.quantile(0.25)) if len(settling_subset) > 0 else np.nan,
        })
df_tolerance = pd.DataFrame(tolerance_rows)

# Bridging
df_bridging_renamed = df_bridging.rename(columns={
    "n": "Bridging_n", "Total_events": "Bridging_total", "Median": "Bridging_median",
    "IQR_lo": "Bridging_Q1", "IQR_hi": "Bridging_Q3", "Min": "Bridging_min", "Max": "Bridging_max",
    "Prop_nonzero": "Bridging_prop_nonzero"
})
df_bridging_renamed["Bridging_IQR"] = df_bridging_renamed["Bridging_Q3"] - df_bridging_renamed["Bridging_Q1"]
df_bridging_renamed["Bridging_role"] = "Pendukung"

df_additional = df_risetime.merge(df_tolerance, on=["Scenario", "Setpoint_g"])
df_additional = df_additional.merge(df_bridging_renamed, on=["Scenario", "Setpoint_g"], how="left")

# Anotasi inferensial Tahap 3 melalui join berdasarkan metrik dan setpoint.
rise_source = df_omnibus[df_omnibus.Metric == "RiseTime_10_90_s"][
    ["Metric", "Setpoint_g", "Test", "p_raw", "p_holm", "Significant_holm"]
].rename(columns={
    "Test": "RiseTime_Test",
    "p_raw": "RiseTime_p_raw",
    "p_holm": "RiseTime_p_holm",
    "Significant_holm": "RiseTime_Significant_holm",
})
rise_source["RiseTime_source_file"] = OMNIBUS_CSV.name
df_additional = df_additional.merge(
    rise_source.drop(columns="Metric"), on="Setpoint_g", validate="many_to_one"
)

within_source = df_tol_omni[
    ["Setpoint_g", "Test", "p_MonteCarlo", "p_holm", "Significant_holm"]
].rename(columns={
    "Test": "Within_Test",
    "p_MonteCarlo": "Within_p_MonteCarlo",
    "p_holm": "Within_p_holm",
    "Significant_holm": "Within_Significant_holm",
})
within_source["Within_source_file"] = TOLERANCE_OMNIBUS_CSV.name
df_additional = df_additional.merge(within_source, on="Setpoint_g", validate="many_to_one")

expected_rise_tests = {15: "Kruskal-Wallis", 20: "Kruskal-Wallis", 25: "Welch ANOVA", 30: "Welch ANOVA"}
assert df_additional.groupby("Setpoint_g").RiseTime_Test.first().to_dict() == expected_rise_tests

# Keterlacakan p-value dan signifikansi memakai kunci baris sumber.
for _, row in df_additional.iterrows():
    source = df_omnibus[
        (df_omnibus.Metric == "RiseTime_10_90_s")
        & (df_omnibus.Setpoint_g == row.Setpoint_g)
        & (df_omnibus.Test == row.RiseTime_Test)
    ]
    assert len(source) == 1
    source = source.iloc[0]
    assert_close(row.RiseTime_p_raw, source.p_raw, "RiseTime p_raw tidak terlacak")
    assert_close(row.RiseTime_p_holm, source.p_holm, "RiseTime p_holm tidak terlacak")
    assert bool(row.RiseTime_Significant_holm) == bool(source.Significant_holm)

    source = df_tol_omni[df_tol_omni.Setpoint_g == row.Setpoint_g]
    assert len(source) == 1
    source = source.iloc[0]
    assert_close(row.Within_p_MonteCarlo, source.p_MonteCarlo, "Within p_MonteCarlo tidak terlacak")
    assert_close(row.Within_p_holm, source.p_holm, "Within p_holm tidak terlacak")
    assert bool(row.Within_Significant_holm) == bool(source.Significant_holm)

print(">>> 7. Exporting canonical CSV files")
csv_primer = OUTPUT / "tahap4_profil_primer.csv"
csv_additional = OUTPUT / "tahap4_profil_tambahan_kondisional.csv"

df_ranking.to_csv(csv_primer, index=False)
df_additional.to_csv(csv_additional, index=False)

# Verify Tahap 3 inputs unchanged
hashes_after = {path.name: compute_sha256(path) for path in TAHAP3_FILES}
assert {path.name: tahap3_hashes_before[path] for path in TAHAP3_FILES} == hashes_after
print("  [PASS] Tahap 3 input integrity: UNCHANGED")

# Validate outputs
assert len(pd.read_csv(csv_primer)) == 16, "csv_primer bukan 16 baris"
assert len(pd.read_csv(csv_additional)) == 16, "csv_additional bukan 16 baris"
print("  [PASS] csv_primer: 16 baris")
print("  [PASS] csv_additional: 16 baris")
print()
print("=" * 70)
print("TAHAP 4 SELESAI")
print("=" * 70)

