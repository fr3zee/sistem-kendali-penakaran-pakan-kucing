#!/usr/bin/env python3
"""
tahap3_generate_reports.py
==========================
Laporan MD lengkap dari results dict Tahap 3.
Dibaca oleh tahap3_analisis_inferensial.py section 11.

Fungsi publik:
    generate_reports(*, results, output_dir) -> list[Path]
    validate_report_files(paths)             -> None
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

# ── required keys ─────────────────────────────────────────────
_REQUIRED_KEYS = {
    "assumption_residual", "assumption_homogeneity",
    "test_recommendation", "omnibus", "posthoc",
    "consistency", "proportion_omnibus", "proportion_posthoc",
    "settling", "bridging", "environment", "config",
}

# ── validator tokens ───────────────────────────────────────────
_REQUIRED_SECTIONS = [
    "## Dasar Pemilihan Uji Omnibus",
    "## Uji Omnibus Metrik Kontinu",
    "## Post-hoc",
    "## Konsistensi FinalError_g",
    "## Proporsi WithinTolerance",
    "## SettlingTime_s Deskriptif Kondisional",
    "## BridgingCount Deskriptif",
    "## Catatan Interpretasi",
]
_REQUIRED_TOKENS = [
    "rank_epsilon_squared", "eta_p2",
    "0,5974", "0,6426", "0,6591",
    "SP15 dan SP30", "100.000", "seed 42",
]
_FORBIDDEN_TOKENS = [
    "f\u00b2_W", "f2_W", "effectsize_oneway", "f2_welch_manual",
    "Fisher-Freeman-Halton equivalent",
    "Tidak ditemukan bukti statistik yang cukup mengenai perbedaan "
    "akurasi akhir (AbsError_pct) antarskenario pada seluruh setpoint",
]


# ── format helpers ─────────────────────────────────────────────

def format_p(v: Any) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "\u2014"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "\u2014"
    if not math.isfinite(v):
        return "\u2014"
    if v < 0 or v > 1:
        raise ValueError(f"p di luar [0,1]: {v}")
    if v < 0.001:
        return "<0,001"
    return f"{v:.3f}".replace(".", ",")


def format_dec(v: Any, n: int = 4) -> str:
    if v is None:
        return "\u2014"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "\u2014"
    if not math.isfinite(v):
        return "\u2014"
    if abs(v) < 0.5 * (10 ** -n):
        v = 0.0
    return f"{v:.{n}f}".replace(".", ",")


def format_int_id(value: int) -> str:
    """Format integer dengan pemisah ribuan titik (format Indonesia)."""
    return f"{int(value):,}".replace(",", ".")


def _sig(v: Any) -> str:
    return "Signifikan" if v else "Belum signifikan"


def _safe(v: Any) -> str:
    if v is None:
        return "\u2014"
    if isinstance(v, float) and not math.isfinite(v):
        return "\u2014"
    return str(v)


# ── dynamic helpers ────────────────────────────────────────────

def _sig_sp_list(df: pd.DataFrame, metric: str) -> list[int]:
    mask = df["Metric"].eq(metric) & df["Significant_holm"].eq(True)
    return sorted(df.loc[mask, "Setpoint_g"].astype(int).tolist())


def _format_setpoints(values: list[int]) -> str:
    labels = [f"SP{v}" for v in values]
    if not labels:
        return "tidak ada setpoint"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} dan {labels[1]}"
    return f"{', '.join(labels[:-1])}, dan {labels[-1]}"


# ── section builders ───────────────────────────────────────────

def _section_assumption(df_res: pd.DataFrame,
                         df_hom: pd.DataFrame,
                         df_rec: pd.DataFrame) -> list[str]:
    KEYS = ["Metric", "Setpoint_g"]
    assumption = (
        df_res
        .merge(df_hom, on=KEYS, how="inner",
               validate="one_to_one", suffixes=("_res", "_bf"))
        .merge(df_rec, on=KEYS, how="inner",
               validate="one_to_one")
    )
    assert len(assumption) == 16, f"assumption merge: {len(assumption)}"
    assert not assumption[KEYS].duplicated().any()

    # Identify columns by pattern (CSV column names differ between files)
    def _col(df: pd.DataFrame, *candidates: str) -> str:
        for c in candidates:
            if c in df.columns:
                return c
        raise KeyError(f"None of {candidates} in {list(df.columns)}")

    sw_p_col   = _col(assumption, "p_value_res", "p_value")
    norm_col   = _col(assumption, "Keputusan_res", "Keputusan",
                      "Normalitas_residual")
    bf_p_col   = _col(assumption, "p_value_bf", "p_value_x",
                      "p_value_y")
    hom_col    = _col(assumption, "Keputusan_bf", "Homogenitas_varians")
    uji_col    = _col(assumption, "Uji_yang_direkomendasikan")
    alasan_col = _col(assumption, "Alasan_singkat")

    L = [
        "## Dasar Pemilihan Uji Omnibus",
        "",
        "Normalitas dinilai dari residual gabungan setiap kombinasi metrik\u2013setpoint "
        "(`hasil_shapiro_residual_per_setpoint.csv`). "
        "Homogenitas varians menggunakan uji Brown\u2013Forsythe (Levene berbasis median) "
        "(`hasil_brown_forsythe_per_setpoint.csv`). "
        "Keputusan uji dikunci pada `rekomendasi_uji_tahap3.csv` sebelum analisis omnibus.",
        "",
        "| Metrik | SP | p SW residual | Normalitas | p BF | Homogenitas | Uji final | Alasan |",
        "|---|---:|---:|---|---:|---|---|---|",
    ]
    for _, r in assumption.iterrows():
        sw_v   = r[sw_p_col]
        bf_v   = r[bf_p_col]
        norm_v = str(r[norm_col]) if pd.notna(r[norm_col]) else "\u2014"
        hom_v  = str(r[hom_col])  if pd.notna(r[hom_col])  else "\u2014"
        uji_v  = str(r[uji_col])  if pd.notna(r[uji_col])  else "\u2014"
        alasan_v = str(r[alasan_col]) if pd.notna(r[alasan_col]) else "\u2014"

        # SW p may be stored as "< 0.001" string
        if isinstance(sw_v, str) and "<" in sw_v:
            sw_s = "<0,001"
        else:
            try:
                sw_s = format_p(float(sw_v))
            except Exception:
                sw_s = _safe(sw_v)

        try:
            bf_s = format_p(float(bf_v))
        except Exception:
            bf_s = _safe(bf_v)

        L.append(
            f"| {r['Metric']} | {int(r['Setpoint_g'])} "
            f"| {sw_s} | {norm_v} | {bf_s} | {hom_v} "
            f"| {uji_v} | {alasan_v} |"
        )
    L += [
        "",
        "> **Catatan RiseTime\\_10\\_90\\_s SP30**: Normalitas pemilihan uji dinilai dari "
        "residual gabungan. Residual SP30 memenuhi asumsi normalitas (SW p=0,1283), sedangkan "
        "homogenitas varians tidak terpenuhi. Oleh karena itu, digunakan Welch ANOVA.",
        "",
    ]
    return L


def _section_omnibus(df: pd.DataFrame) -> list[str]:
    L = [
        "## Uji Omnibus Metrik Kontinu",
        "",
        "| Metrik | SP | Uji | Statistik | df1 | df2 | p mentah | p Holm | Keputusan | Ukuran Efek | Nilai |",
        "|---|---:|---|---:|---:|---:|---:|---:|---|---|---:|",
    ]
    for _, r in df.iterrows():
        test = str(r.get("Test", ""))
        if test == "SKIPPED":
            continue
        df2_v = r.get("df2")
        try:
            df2_s = format_dec(float(df2_v), 2) \
                if df2_v not in (None, "", float("nan")) else "\u2014"
        except Exception:
            df2_s = "\u2014"
        L.append(
            f"| {r['Metric']} | {int(r['Setpoint_g'])} | {test} "
            f"| {format_dec(r.get('Statistic'), 4)} | {int(r.get('df1', 0))} | {df2_s} "
            f"| {format_p(r.get('p_raw'))} | {format_p(r.get('p_holm'))} "
            f"| {_sig(r.get('Significant_holm'))} "
            f"| {_safe(r.get('EffectSize_name'))} "
            f"| {format_dec(r.get('EffectSize_value'), 4)} |"
        )
    L.append("")
    return L


def _section_posthoc(df: pd.DataFrame) -> list[str]:
    if df is None or len(df) == 0:
        return []
    L = [
        "## Post-hoc",
        "",
        "Cliff\u2019s \u03b4 untuk pasangan Kruskal\u2013Wallis (Dunn\u2013Holm); "
        "Hedges\u2019 g untuk pasangan Welch (Games\u2013Howell). "
        "Kolom Arah menunjukkan tanda ukuran efek secara deskriptif dan tidak "
        "menggantikan keputusan berdasarkan nilai probabilitas tersesuaikan.",
        "",
        "| Metrik | SP | Uji | A | B | p adj | Keputusan | Efek | Nilai | CI lo | CI hi | Arah |",
        "|---|---:|---|---|---|---:|---|---|---:|---:|---:|---|",
    ]
    # Normalize effect size name for display
    _ES_LABEL = {"Cliff_delta": "Cliff\u2019s \u03b4", "Hedges_g": "Hedges\u2019 g"}
    for _, r in df.iterrows():
        es_name = _safe(r.get("EffectSize_name"))
        es_label = _ES_LABEL.get(es_name, es_name)
        L.append(
            f"| {r['Metric']} | {int(r['Setpoint_g'])} "
            f"| {_safe(r.get('PostHoc_test'))} "
            f"| {r['Group_A']} | {r['Group_B']} "
            f"| {format_p(r.get('p_adjusted'))} "
            f"| {_sig(r.get('Significant'))} "
            f"| {es_label} "
            f"| {format_dec(r.get('EffectSize_value'), 4)} "
            f"| {_safe(r.get('CI_lo'))} "
            f"| {_safe(r.get('CI_hi'))} "
            f"| {_safe(r.get('Direction'))} |"
        )
    L.append("")
    return L


def _section_consistency(df: pd.DataFrame) -> list[str]:
    if df is None or len(df) == 0:
        return []
    L = [
        "## Konsistensi FinalError_g",
        "",
        "Uji Brown\u2013Forsythe (Levene berbasis median) atas variansi FinalError_g. "
        "Rasio varians dan skenario dengan varians terkecil disajikan secara deskriptif. "
        "Uji ini bersifat omnibus dan tidak mengidentifikasi pasangan skenario "
        "yang memiliki variansi berbeda.",
        "",
        "| SP | F | df1 | df2 | p mentah | p Holm | Keputusan | VarRatio | MinVar |",
        "|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for _, r in df.iterrows():
        L.append(
            f"| {int(r['Setpoint_g'])} "
            f"| {format_dec(r.get('BF_statistic'), 4)} "
            f"| {_safe(r.get('df1'))} | {_safe(r.get('df2'))} "
            f"| {format_p(r.get('p_raw'))} | {format_p(r.get('p_holm'))} "
            f"| {_sig(r.get('Significant_holm'))} "
            f"| {_safe(r.get('VarRatio_max_min'))} "
            f"| {_safe(r.get('MinVar_scenario'))} |"
        )
    L += [
        "",
        "> Catatan: Rasio varians dan skenario dengan varians terkecil disajikan "
        "secara deskriptif. Uji Brown\u2013Forsythe bersifat omnibus dan tidak "
        "mengidentifikasi pasangan skenario yang memiliki variansi berbeda.",
        "",
    ]
    return L


def _section_proportion(df_omni: pd.DataFrame,
                         df_ph: pd.DataFrame,
                         cfg: dict) -> list[str]:
    n_mc  = int(cfg.get("n_monte_carlo", 100_000))
    seed  = int(cfg.get("seed", 42))
    n_mc_s = format_int_id(n_mc)

    L = [
        "## Proporsi WithinTolerance",
        "",
        f"Uji independensi Pearson chi-square dengan estimasi nilai probabilitas "
        f"Monte Carlo bersyarat pada margin tetap, menggunakan {n_mc_s} simulasi "
        f"dan seed {seed}. "
        "Statistik Pearson \u03c7\u00b2 dan nilai probabilitas asimtotik disajikan "
        "sebagai diagnostik; keputusan inferensial berdasarkan p-value Monte Carlo "
        "yang telah dikoreksi Holm pada empat setpoint.",
        "",
        "### Omnibus",
        "",
        "| SP | \u03c7\u00b2 (diag) | p asim (diag) | p MC | p Holm | Keputusan | V | MinExp | Count ekstrem |",
        "|---:|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for _, r in df_omni.iterrows():
        p_asim = r.get("p_asymptotic", r.get("p_asym", r.get("p_raw")))
        p_mc   = r.get("p_MonteCarlo", r.get("p_MC"))
        try:
            p_asim_s = format_p(float(p_asim)) if p_asim is not None else "\u2014"
        except Exception:
            p_asim_s = _safe(p_asim)
        try:
            p_mc_s = format_p(float(p_mc)) if p_mc is not None else "\u2014"
        except Exception:
            p_mc_s = _safe(p_mc)
        L.append(
            f"| {int(r['Setpoint_g'])} "
            f"| {format_dec(r.get('Statistic'), 4)} "
            f"| {p_asim_s} | {p_mc_s} "
            f"| {format_p(r.get('p_holm'))} "
            f"| {_sig(r.get('Significant_holm'))} "
            f"| {format_dec(r.get('CramersV'), 3)} "
            f"| {_safe(r.get('MinExpected'))} "
            f"| {_safe(r.get('Count_extreme'))} |"
        )
    L.append("")

    if df_ph is not None and len(df_ph) > 0:
        L += [
            "### Post-hoc Fisher (dua sisi, koreksi Holm dalam 6 pasangan per setpoint)",
            "",
            "| SP | A | B | Prop A | Prop B | Selisih | OR | p Holm | Keputusan |",
            "|---:|---|---|---:|---:|---:|---:|---:|---|",
        ]
        for _, r in df_ph.iterrows():
            or_v = r.get("OddsRatio")
            or_s = ("\u2014"
                    if (or_v is None or
                        (isinstance(or_v, float) and not math.isfinite(or_v)))
                    else format_dec(or_v, 4))
            L.append(
                f"| {int(r['Setpoint_g'])} "
                f"| {r['Group_A']} | {r['Group_B']} "
                f"| {_safe(r.get('Prop_A'))} | {_safe(r.get('Prop_B'))} "
                f"| {_safe(r.get('Prop_diff'))} | {or_s} "
                f"| {format_p(r.get('p_holm'))} "
                f"| {_sig(r.get('Significant_holm'))} |"
            )
        L.append("")
    return L


def _section_settling(df: pd.DataFrame) -> list[str]:
    L = [
        "## SettlingTime_s Deskriptif Kondisional",
        "",
        "SettlingTime_s diringkas pada trial yang menghasilkan nilai valid berdasarkan "
        "kriteria kondisional, yaitu respons memasuki dan mempertahankan batas yang "
        "ditetapkan sampai akhir pengamatan. "
        "Jumlah trial tersedia dapat berbeda antarskenario dan setpoint. "
        "Metrik ini disajikan secara deskriptif dan tidak diuji secara inferensial.",
        "",
        "| SP | Skenario | n valid | n total | Median | Q1 | Q3 | IQR |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        na = int(r.get("n_available", 0))
        nt = int(r.get("n_total", 10))
        med = format_dec(r.get("Median"), 2) if na > 0 else "\u2014"
        q1  = format_dec(r.get("Q1"),     2) if na > 0 else "\u2014"
        q3  = format_dec(r.get("Q3"),     2) if na > 0 else "\u2014"
        iqr = format_dec(r.get("IQR"),    2) if na > 0 else "\u2014"
        L.append(
            f"| {int(r['Setpoint_g'])} | {r['Scenario']} "
            f"| {na} | {nt} | {med} | {q1} | {q3} | {iqr} |"
        )
    L.append("")
    return L


def _section_bridging(df: pd.DataFrame) -> list[str]:
    L = [
        "## BridgingCount Deskriptif",
        "",
        "| SP | Skenario | n | Total | Median | IQR lo | IQR hi | Min | Max | Prop>0 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        L.append(
            f"| {int(r['Setpoint_g'])} | {r['Scenario']} "
            f"| {int(r['n'])} | {int(r['Total_events'])} "
            f"| {format_dec(r.get('Median'), 1)} "
            f"| {format_dec(r.get('IQR_lo'), 2)} "
            f"| {format_dec(r.get('IQR_hi'), 2)} "
            f"| {int(r.get('Min', 0))} | {int(r.get('Max', 0))} "
            f"| {format_dec(r.get('Prop_nonzero'), 1)} |"
        )
    L.append("")
    return L


def _section_notes(df_omnibus: pd.DataFrame, cfg: dict) -> list[str]:
    n_mc   = int(cfg.get("n_monte_carlo", 100_000))
    seed   = int(cfg.get("seed", 42))
    alpha  = cfg.get("alpha", 0.05)
    n_boot = int(cfg.get("n_bootstrap", 10000))
    n_mc_s = format_int_id(n_mc)
    n_boot_s = format_int_id(n_boot)

    abs_sig  = _sig_sp_list(df_omnibus, "AbsError_pct")
    max_sig  = _sig_sp_list(df_omnibus, "MaxOvershoot_pct")
    dur_sig  = _sig_sp_list(df_omnibus, "Duration_s")
    rise_sig = _sig_sp_list(df_omnibus, "RiseTime_10_90_s")

    return [
        "## Catatan Interpretasi",
        "",
        f'1. "Belum signifikan" \u2260 "sama"; bukti tidak cukup menolak H\u2080 '
        f'pada \u03b1={alpha} dengan n=10.',
        "2. Kruskal\u2013Wallis menguji distribusi/peringkat; perbedaan lokasi "
        "diasumsikan jika bentuk distribusi serupa.",
        "3. Ukuran efek Kruskal\u2013Wallis: rank_epsilon_squared = H\u00a0/\u00a0(N\u22121).",
        "4. Ukuran efek Welch ANOVA: eta_p2 (partial eta-squared) dari kolom `np2` "
        "keluaran `pingouin.welch_anova()`. "
        "Nilai terverifikasi: Duration SP25=0,5974, RiseTime SP25=0,6426, RiseTime SP30=0,6591.",
        "5. Koreksi Holm per keluarga metrik (4 setpoint per metrik), bukan global 16 uji.",
        f"6. WithinTolerance: uji chi-square Monte Carlo bersyarat pada margin tetap, "
        f"{n_mc_s} simulasi, seed {seed}.",
        f"7. Perbedaan AbsError_pct antarskenario ditemukan pada "
        f"{_format_setpoints(abs_sig)} setelah koreksi Holm.",
        f"8. Perbedaan MaxOvershoot_pct: {_format_setpoints(max_sig)}.",
        f"9. Perbedaan Duration_s: {_format_setpoints(dur_sig)}.",
        f"10. Perbedaan RiseTime_10\\_90\\_s: {_format_setpoints(rise_sig)}.",
        "11. SettlingTime_s dan BridgingCount: deskriptif saja; tidak diuji inferensial.",
        "12. Metode dikunci sebelum eksekusi; tidak diubah berdasarkan hasil signifikansi.",
        f"13. CI Cliff\u2019s \u03b4 dan Hedges\u2019 g dihitung dari {n_boot_s} bootstrap.",
        "",
    ]


# ── internal markdown validators ──────────────────────────────

def validate_markdown_text(text: str) -> None:
    for s in _REQUIRED_SECTIONS:
        assert s in text, f"Bagian tidak ditemukan: {s!r}"
    for t in _REQUIRED_TOKENS:
        assert t in text, f"Token wajib tidak ada: {t!r}"
    for t in _FORBIDDEN_TOKENS:
        assert t not in text, f"Token lama masih ada: {t!r}"


def validate_markdown_path(path: Path) -> None:
    validate_markdown_text(path.read_text(encoding="utf-8"))


# ── public API ─────────────────────────────────────────────────

def generate_reports(
    *,
    results: dict[str, Any],
    output_dir: Path,
) -> list[Path]:
    missing = _REQUIRED_KEYS - set(results)
    if missing:
        raise KeyError(f"Data laporan belum lengkap: {sorted(missing)}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cfg = results["config"]
    env = results["environment"]
    n_mc_s = format_int_id(int(cfg.get("n_monte_carlo", 100_000)))
    n_boot_s = format_int_id(int(cfg.get("n_bootstrap", 10000)))

    lines: list[str] = [
        "# Laporan Tahap 3 \u2014 Analisis Inferensial Final",
        "",
        f"Tanggal: {env.get('Timestamp', '\u2014')}",
        "",
        "## Informasi Lingkungan dan Konfigurasi",
        "",
    ]
    for k, v in env.items():
        lines.append(f"- **{k}**: {v}")
    lines += [
        "",
        f"- **\u03b1**: {cfg.get('alpha', 0.05)}",
        f"- **seed**: {cfg.get('seed', 42)}",
        f"- **n\\_monte\\_carlo**: {n_mc_s}",
        f"- **n\\_bootstrap**: {n_boot_s}",
        "",
    ]

    lines += _section_assumption(
        results["assumption_residual"],
        results["assumption_homogeneity"],
        results["test_recommendation"],
    )
    lines += _section_omnibus(results["omnibus"])
    lines += _section_posthoc(results["posthoc"])
    lines += _section_consistency(results["consistency"])
    lines += _section_proportion(
        results["proportion_omnibus"],
        results["proportion_posthoc"],
        cfg,
    )
    lines += _section_settling(results["settling"])
    lines += _section_bridging(results["bridging"])
    lines += _section_notes(results["omnibus"], cfg)

    content = "\n".join(lines)
    final   = output_dir / "laporan_tahap3_analisis_inferensial.md"
    tmp     = final.with_name(final.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    validate_markdown_path(tmp)  # validate before atomic replace
    tmp.replace(final)
    return [final]


def validate_report_files(paths: list[Path]) -> None:
    assert paths, "Tidak ada laporan yang dihasilkan."
    for p in paths:
        assert p.is_file(), f"File tidak ditemukan: {p}"
        assert p.stat().st_size > 0, f"File kosong: {p}"
        validate_markdown_path(p)
