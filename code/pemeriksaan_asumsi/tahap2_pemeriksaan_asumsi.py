#!/usr/bin/env python3
"""
tahap2_pemeriksaan_asumsi.py
Generator mandiri pemeriksaan asumsi statistik.

Input : data/pengujian_final/master_dataset_160.csv
Output: hasil/pemeriksaan_asumsi/
        ├── hasil_shapiro_residual_per_setpoint.csv
        ├── hasil_brown_forsythe_per_setpoint.csv
        └── rekomendasi_uji_tahap3.csv

Dapat dijalankan dari fresh clone tanpa baseline sebelumnya.
"""
from __future__ import annotations
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "pengujian_final" / "master_dataset_160.csv"
OUT  = Path(os.environ.get("PIPELINE_OUTPUT_DIR",
                            str(ROOT / "hasil" / "pemeriksaan_asumsi")))
OUT.mkdir(parents=True, exist_ok=True)

SCENARIOS  = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS  = [15, 20, 25, 30]
METRICS    = ["AbsError_pct", "MaxOvershoot_pct", "Duration_s", "RiseTime_10_90_s"]
ALPHA      = 0.05


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ptxt(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.4f}"


def _norm_decision(p: float) -> str:
    if p >= ALPHA:
        return "Tidak terdapat bukti signifikan untuk menolak asumsi normalitas"
    return "Terdapat bukti penyimpangan dari distribusi normal"


def _var_decision(p: float) -> str:
    if p >= ALPHA:
        return "Tidak terdapat bukti signifikan perbedaan varians"
    return "Varians tidak homogen"


def _recommend(normal: bool, homogeneous: bool) -> tuple[str, str, str]:
    """Return (omnibus, posthoc, alasan)."""
    if normal and homogeneous:
        return (
            "One-way ANOVA",
            "Tukey HSD",
            "Residual memenuhi normalitas dan homogenitas varians",
        )
    if normal and not homogeneous:
        return (
            "Welch ANOVA",
            "Games-Howell",
            "Residual cukup layak tetapi varians tidak homogen",
        )
    return (
        "Kruskal-Wallis",
        "Dunn dengan koreksi Holm",
        "Residual tidak normal",
    )


# ---------------------------------------------------------------------------
# Shapiro–Wilk pada residual gabungan per metrik × setpoint
# ---------------------------------------------------------------------------

def run_shapiro(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        for sp in SETPOINTS:
            sub = df[df["Setpoint_g"] == sp][metric].dropna()
            # Residual = nilai − rata-rata per skenario
            residuals = []
            for sc in SCENARIOS:
                grp = sub[df.loc[sub.index, "Scenario"] == sc]
                if len(grp) > 0:
                    residuals.extend((grp - grp.mean()).tolist())
            residuals = np.array(residuals)
            n = len(residuals)
            if n < 3:
                continue
            W, p = stats.shapiro(residuals)
            skew = float(stats.skew(residuals))
            rows.append({
                "Metric":                  metric,
                "Setpoint_g":              sp,
                "n_total_available":       n,
                "n_per_scenario":          "/".join(
                    str(len(df[(df["Setpoint_g"] == sp) & (df["Scenario"] == sc)][metric].dropna()))
                    for sc in SCENARIOS
                ),
                "Shapiro_W":               round(W, 4),
                "p_value":                 _ptxt(p),
                "skewness_residual":       round(skew, 4),
                "Keputusan":               _norm_decision(p),
                "Catatan":                 "",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Brown–Forsythe per metrik × setpoint
# ---------------------------------------------------------------------------

def run_brown_forsythe(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        for sp in SETPOINTS:
            groups = [
                df[(df["Setpoint_g"] == sp) & (df["Scenario"] == sc)][metric].dropna().values
                for sc in SCENARIOS
            ]
            groups = [g for g in groups if len(g) > 0]
            if len(groups) < 2:
                continue
            stat, p = stats.levene(*groups, center="median")
            rows.append({
                "Metric":      metric,
                "Setpoint_g":  sp,
                "BF_stat":     round(stat, 4),
                "p_value":     _ptxt(p),
                "Keputusan":   _var_decision(p),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Rekomendasi uji
# ---------------------------------------------------------------------------

def build_rekomendasi(
    df_shapiro: pd.DataFrame,
    df_bf: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        for sp in SETPOINTS:
            sw_row = df_shapiro[
                (df_shapiro["Metric"] == metric) & (df_shapiro["Setpoint_g"] == sp)
            ]
            bf_row = df_bf[
                (df_bf["Metric"] == metric) & (df_bf["Setpoint_g"] == sp)
            ]
            if sw_row.empty or bf_row.empty:
                continue

            sw_p_str = sw_row.iloc[0]["p_value"]
            bf_p_str = bf_row.iloc[0]["p_value"]

            # Parse p-value strings back to float for comparison
            def parse_p(s: str) -> float:
                s = s.strip()
                if s.startswith("<"):
                    return 0.0
                return float(s)

            sw_p = parse_p(sw_p_str)
            bf_p = parse_p(bf_p_str)

            normal      = sw_p >= ALPHA
            homogeneous = bf_p >= ALPHA

            omnibus, posthoc, alasan = _recommend(normal, homogeneous)

            # Augment alasan with Shapiro skewness info if abnormal
            skew = sw_row.iloc[0]["skewness_residual"]
            sw_keputusan = sw_row.iloc[0]["Keputusan"]
            if not normal:
                if abs(float(skew)) > 1.5:
                    alasan = f"Distribusi sangat menceng dan residual tidak normal"
                elif abs(float(skew)) > 0.5:
                    alasan = f"Residual tidak normal dengan skewness sedang-berat"
                else:
                    alasan = f"Residual tidak normal"
                if not homogeneous:
                    alasan = "Residual tidak normal dan varians tidak homogen"

            rows.append({
                "Metric":                        metric,
                "Setpoint_g":                    sp,
                "Normalitas_residual":           "Terpenuhi" if normal else "Tidak terpenuhi",
                "Homogenitas_varians":           "Terpenuhi" if homogeneous else "Tidak terpenuhi",
                "Kondisi_jumlah_sampel":         "Seimbang",
                "Uji_yang_direkomendasikan":     omnibus,
                "Post_hoc_yang_direkomendasikan": posthoc,
                "Alasan_singkat":                alasan,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("tahap2_pemeriksaan_asumsi.py")
    print("=" * 60)

    df = pd.read_csv(DATA)
    assert len(df) == 160, f"Dataset bukan 160 baris: {len(df)}"
    print(f"  Dataset: {len(df)} baris")

    print("  Shapiro–Wilk residual...")
    df_sw = run_shapiro(df)
    out_sw = OUT / "hasil_shapiro_residual_per_setpoint.csv"
    df_sw.to_csv(out_sw, index=False, lineterminator="\n")
    print(f"  Ditulis: {out_sw}")

    print("  Brown–Forsythe...")
    df_bf = run_brown_forsythe(df)
    out_bf = OUT / "hasil_brown_forsythe_per_setpoint.csv"
    df_bf.to_csv(out_bf, index=False, lineterminator="\n")
    print(f"  Ditulis: {out_bf}")

    print("  Rekomendasi uji...")
    df_rek = build_rekomendasi(df_sw, df_bf)
    out_rek = OUT / "rekomendasi_uji_tahap3.csv"
    df_rek.to_csv(out_rek, index=False, lineterminator="\n")
    print(f"  Ditulis: {out_rek}")

    print("=" * 60)
    print(f"  {len(df_sw)} baris Shapiro, {len(df_bf)} baris BF, {len(df_rek)} baris rekomendasi")
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
