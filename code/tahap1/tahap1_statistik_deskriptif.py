"""
Tahap 1 — Statistik Deskriptif Dataset 160 Trial

CATATAN REPRODUKSIBILITAS:
Script ini merupakan implementasi ulang berdasarkan prosedur yang
didokumentasikan pada laporan_tahap1_validasi_dan_statistik_deskriptif.docx
dan tahap1_validasi_deskriptif.md.
Script ini bukan file asli yang digunakan selama proses penelitian.
Output yang dihasilkan ekuivalen terhadap artefak penelitian.

Input  : data/master_dataset_160.csv
Output : hasil_statistik_deskriptif_tahap1.csv (per Scenario x Setpoint)
         hasil_statistik_deskriptif_agregat_tahap1.csv (per Scenario)
"""

import pathlib
import pandas as pd

# ── paths ──────────────────────────────────────────────────────────────────
ROOT   = pathlib.Path(__file__).resolve().parents[2]
DATA   = ROOT / "data" / "master_dataset_160.csv"
OUT    = pathlib.Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

METRICS = ["AbsError_pct", "MaxOvershoot_pct", "Duration_s", "BridgingCount"]

METRIC_LABELS = {
    "AbsError_pct":    "AbsError_pct",
    "MaxOvershoot_pct": "MaxOvershoot_pct",
    "Duration_s":      "Duration_s",
    "BridgingCount":   "BridgingCount",
}


def descriptive_stats(group: pd.DataFrame, col: str) -> dict:
    s = group[col]
    return {
        "n":      len(s),
        "mean":   round(s.mean(), 2),
        "median": round(s.median(), 2),
        "sd":     round(s.std(ddof=1), 2),
        "min":    round(s.min(), 2),
        "max":    round(s.max(), 2),
    }


def main() -> None:
    assert DATA.exists(), f"Dataset tidak ditemukan: {DATA}"
    df = pd.read_csv(DATA)

    # ── per Scenario × Setpoint ───────────────────────────────────────────
    rows_combo = []
    for (sc, sp), grp in df.groupby(["Scenario", "Setpoint_g"], sort=False):
        for col in METRICS:
            if col not in df.columns:
                continue
            stats = descriptive_stats(grp, col)
            rows_combo.append({"Scenario": sc, "Setpoint_g": sp,
                               "Metric": METRIC_LABELS[col], **stats})

    df_combo = pd.DataFrame(rows_combo)
    out_combo = OUT / "hasil_statistik_deskriptif_tahap1.csv"
    df_combo.to_csv(out_combo, index=False)
    print(f"Saved: {out_combo}")

    # ── agregat per Scenario ──────────────────────────────────────────────
    rows_agg = []
    for sc, grp in df.groupby("Scenario", sort=False):
        for col in METRICS:
            if col not in df.columns:
                continue
            stats = descriptive_stats(grp, col)
            rows_agg.append({"Scenario": sc,
                             "Metric": METRIC_LABELS[col], **stats})

    df_agg = pd.DataFrame(rows_agg)
    out_agg = OUT / "hasil_statistik_deskriptif_agregat_tahap1.csv"
    df_agg.to_csv(out_agg, index=False)
    print(f"Saved: {out_agg}")

    # ── ringkasan console ─────────────────────────────────────────────────
    print("\n=== Statistik Deskriptif Agregat per Skenario ===")
    for metric in METRIC_LABELS.values():
        sub = df_agg[df_agg["Metric"] == metric][["Scenario", "mean", "sd"]]
        print(f"\n{metric}:")
        print(sub.to_string(index=False))


if __name__ == "__main__":
    main()
