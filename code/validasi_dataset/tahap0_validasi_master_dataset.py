"""
Tahap 0 — Validasi Master Dataset (160 Trial)

CATATAN REPRODUKSIBILITAS:
Script ini merupakan implementasi ulang berdasarkan prosedur yang
didokumentasikan pada laporan_tahap0_validasi_master_dataset_160_trial.docx.
Script ini bukan file asli yang digunakan selama proses penelitian.
Output yang dihasilkan ekuivalen terhadap artefak penelitian.

Input  : data/master_dataset_160.csv
Output : console report + ringkasan validasi
"""

import pathlib
import pandas as pd

# ── paths ──────────────────────────────────────────────────────────────────
import os as _os
ROOT    = pathlib.Path(__file__).resolve().parents[2]   # repo root
DATA    = ROOT / "data" / "pengujian_final" / "master_dataset_160.csv"
OUT_DIR = pathlib.Path(_os.environ.get("PIPELINE_OUTPUT_DIR",
          str(ROOT / "hasil" / "validasi_dataset")))
OUT_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS   = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS   = [15, 20, 25, 30]
N_TRIAL     = 10
TOTAL_TRIAL = 160

REQUIRED_COLS = [
    "Scenario", "Setpoint_g", "TrialNo",
    "FinalMass_g", "AbsError_pct", "MaxOvershoot_pct", "Duration_s",
    "FinalError_g", "Valid", "StopReason",
]


def validate(df: pd.DataFrame) -> dict[str, str]:
    checks: dict[str, str] = {}

    # 1. Total baris
    checks["total_rows_160"]      = "PASS" if len(df) == TOTAL_TRIAL else f"FAIL ({len(df)})"

    # 2. Distribusi per skenario = 40
    for sc in SCENARIOS:
        n = (df["Scenario"] == sc).sum()
        checks[f"scenario_{sc.replace(' ','_')}"] = "PASS" if n == 40 else f"FAIL ({n})"

    # 3. Semua 16 kombinasi lengkap (masing-masing 10 trial)
    combo = df.groupby(["Scenario", "Setpoint_g"]).size()
    checks["all_16_combos_n10"] = (
        "PASS" if len(combo) == 16 and (combo == N_TRIAL).all()
        else f"FAIL ({combo.to_dict()})"
    )

    # 4. Tidak ada duplikat TrialNo dalam kombinasi
    dup = df.groupby(["Scenario", "Setpoint_g"])["TrialNo"].apply(lambda x: x.duplicated().any())
    checks["no_duplicate_trialno"] = "PASS" if not dup.any() else f"FAIL ({dup[dup].index.tolist()})"

    # 5. Valid semuanya TRUE
    invalid = (df["Valid"] != True).sum()  # noqa: E712
    checks["all_valid_true"] = "PASS" if invalid == 0 else f"FAIL ({invalid} rows)"

    # 6. StopReason semuanya TARGET
    wrong_stop = (df["StopReason"] != "TARGET").sum()
    checks["all_stopreason_target"] = "PASS" if wrong_stop == 0 else f"FAIL ({wrong_stop} rows)"

    # 7. Tidak ada missing value pada kolom penting
    missing = df[REQUIRED_COLS].isnull().any()
    checks["no_missing_required_cols"] = (
        "PASS" if not missing.any()
        else f"FAIL ({missing[missing].index.tolist()})"
    )

    # 8. Kolom wajib ada
    missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
    checks["required_cols_exist"] = "PASS" if not missing_cols else f"FAIL missing: {missing_cols}"

    return checks


def main() -> None:
    assert DATA.exists(), f"Dataset tidak ditemukan: {DATA}"
    df = pd.read_csv(DATA)

    checks = validate(df)
    all_pass = all(v == "PASS" for v in checks.values())

    print("=" * 55)
    print("TAHAP 0 — VALIDASI MASTER DATASET")
    print("=" * 55)
    for k, v in checks.items():
        icon = "OK  " if v == "PASS" else "FAIL"
        print(f"  {icon}  {k:<40} {v}")
    print("-" * 55)
    print(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"  Total trial terbaca: {len(df)}")
    print("=" * 55)

    assert all_pass, "Validasi GAGAL. Periksa output di atas."

    # Save report to file
    report_lines = ["TAHAP 0 — VALIDASI MASTER DATASET\n"]
    for k, v in checks.items():
        icon = "OK  " if v == "PASS" else "FAIL"
        report_lines.append(f"  {icon}  {k:<40} {v}\n")
    report_lines.append(f"  OVERALL: {'PASS' if all_pass else 'FAIL'}\n")
    report_lines.append(f"  Total trial terbaca: {len(df)}\n")
    out_file = OUT_DIR / "laporan_validasi_dataset.txt"
    out_file.write_text("".join(report_lines), encoding="utf-8")
    print(f"  Laporan disimpan: {out_file}")


if __name__ == "__main__":
    main()
