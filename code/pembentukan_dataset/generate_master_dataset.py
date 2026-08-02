#!/usr/bin/env python3
"""
generate_master_dataset.py
Membaca 160 log trial dari data/pengujian_final/log_160_trial/,
mengekstrak SUMMARY + deret DATA, menghitung kolom turunan,
dan menghasilkan master_dataset_160_regenerated.csv beserta laporan audit.
"""

import csv
import hashlib
import math
import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = REPO_ROOT / "data" / "pengujian_final" / "log_160_trial"
CANONICAL = REPO_ROOT / "data" / "pengujian_final" / "master_dataset_160.csv"
OUT_DIR = REPO_ROOT / "hasil" / "pembentukan_dataset"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Urutan skenario kanonis
SCENARIO_ORDER = ["Fixed PID", "GS PID", "Manual Cepat", "Manual Presisi"]
SETPOINT_ORDER = [15, 20, 25, 30]

# Folder sumber per skenario (nama persis di LOG_ROOT)
FOLDER_MAP = {
    "Fixed PID":    "fixed_pid",
    "GS PID":       "gs_pid",
    "Manual Cepat": "manual_cepat",
    "Manual Presisi": "manual_presisi",
}

# Kolom Controller untuk dataset (GS PID berbeda)
CONTROLLER_MAP = {
    "Fixed PID":    "Fixed PID",
    "GS PID":       "Gain Scheduling PID",
    "Manual Cepat": "Manual Cepat",
    "Manual Presisi": "Manual Presisi",
}

# Toleransi audit numerik
NUMERIC_TOL = {
    "FinalMass_g":      0.005,
    "FinalError_g":     0.005,
    "FinalError_pct":   0.005,
    "AbsError_g":       0.005,
    "AbsError_pct":     0.005,
    "MaxOvershoot_g":   0.005,
    "MaxOvershoot_pct": 0.005,
    "Duration_s":       0.001,
    "TimeTo90_s":       0.001,
    "RiseTime_10_90_s": 0.001,
    "SettlingTime_s":   0.005,
    "EarlyStop_g":      0.001,
}

EXACT_COLS = ["Scenario", "Controller", "TrialNo", "FileName",
              "Status", "StopReason", "Valid", "WithinTolerance",
              "BridgingCount", "Setpoint_g"]

COLUMNS_OUT = [
    "No", "Scenario", "Controller", "Setpoint_g", "TrialNo", "FileName",
    "FinalMass_g", "FinalError_g", "FinalError_pct",
    "AbsError_g", "AbsError_pct",
    "MaxOvershoot_g", "MaxOvershoot_pct",
    "Duration_s", "TimeTo90_s", "RiseTime_10_90_s", "SettlingTime_s",
    "BridgingCount", "Status", "Valid", "StopReason",
    "EarlyStop_g", "Notes", "WithinTolerance",
]

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _float(val, fallback=float("nan")):
    try:
        v = float(str(val).strip())
        return fallback if math.isnan(v) else v
    except (ValueError, TypeError):
        return fallback


def parse_log(path: Path) -> dict:
    """Parse SUMMARY (primary) + DATA (verification/fallback)."""
    text = path.read_text(encoding="utf-8", errors="ignore")

    # --- SUMMARY ---
    s_start = text.find("=== SUMMARY TRIAL ===")
    s_end   = text.find("=== TRIAL END ===")
    summary = {}
    if s_start != -1 and s_end != -1:
        for line in text[s_start:s_end].splitlines():
            if line.startswith("==="):
                continue
            # Support both "Key: Value" and "Key Value" (tab or space separated)
            if ":" in line:
                k, _, v = line.partition(":")
                summary[k.strip()] = v.strip()
            else:
                # Space-delimited: first token = key, rest = value
                parts = line.split(None, 1)
                if len(parts) == 2:
                    summary[parts[0].strip()] = parts[1].strip()

    # --- DATA rows ---
    d_start = text.find("=== DATA START ===")
    d_end   = text.find("=== SUMMARY TRIAL ===")
    if d_end == -1:
        d_end = len(text)
    data_rows = []
    if d_start != -1:
        for line in text[d_start:d_end].splitlines():
            if line.startswith("DATA,"):
                parts = line.split(",")
                try:
                    t_ms = float(parts[1])
                    m_g  = float(parts[2])
                    data_rows.append((t_ms, m_g))
                except (IndexError, ValueError):
                    pass

    # --- Identity from folder/filename ---
    # path = .../log_160_trial/<scenario_folder>/SP<nn>/Filename.txt
    sp_folder   = path.parent.name          # e.g. SP15
    scen_folder = path.parent.parent.name   # e.g. fixed_pid

    scenario = next(
        (sc for sc, fo in FOLDER_MAP.items() if fo == scen_folder),
        scen_folder
    )
    sp_match = re.search(r"(\d+)", sp_folder)
    setpoint = float(sp_match.group(1)) if sp_match else float("nan")

    trial_match = re.search(r"trial(\d+)", path.name, re.IGNORECASE)
    trial_no = int(trial_match.group(1)) if trial_match else -1

    # --- Metrik dari SUMMARY (sumber utama) ---
    def s(key, fb=float("nan")):
        return _float(summary.get(key, fb))

    final_mass       = s("FinalMass_g")
    final_error_g    = s("FinalError_g")
    final_error_pct  = s("FinalError_pct")
    max_os_g         = s("MaxOvershoot_g")
    max_os_pct       = s("MaxOvershoot_pct")
    duration_s       = s("Duration_s", s("Duration_ms", float("nan")) / 1000)
    time_to_90_ms    = s("TimeTo90_ms")
    time_to_90_s     = time_to_90_ms / 1000 if not math.isnan(time_to_90_ms) else float("nan")
    rt_ms            = s("RiseTime_10_90_ms")
    rt_s             = rt_ms / 1000 if not math.isnan(rt_ms) else float("nan")
    settling_ms      = s("SettlingTime_ms")
    settling_s       = float("nan") if math.isnan(settling_ms) or settling_ms < 0 \
                       else settling_ms / 1000
    bridging         = int(s("BridgingCount", 0))
    early_stop       = s("EarlyStop_g")
    status           = summary.get("Status", "")
    valid_str        = summary.get("Valid", "TRUE").upper()
    valid            = True if valid_str in ("TRUE", "1") else False
    stop_reason      = summary.get("StopReason", "")

    # Fallback dari DATA jika SUMMARY tidak ada field
    if data_rows:
        masses = [m for _, m in data_rows]
        times  = [t for t, _ in data_rows]

        if math.isnan(final_mass) and masses:
            final_mass = masses[-1]

        if math.isnan(rt_s):
            tgt10 = 0.10 * setpoint
            tgt90 = 0.90 * setpoint
            t10 = next((t for t, m in data_rows if m >= tgt10), None)
            t90 = next((t for t, m in data_rows if m >= tgt90), None)
            if t10 is not None and t90 is not None:
                rt_s = (t90 - t10) / 1000

        if math.isnan(settling_s) and settling_ms == -1:
            pass  # NaN intentional: tidak pernah settle

        if math.isnan(max_os_pct) and masses and not math.isnan(setpoint):
            mx = max(masses)
            max_os_g   = max(0.0, mx - setpoint)
            max_os_pct = (max_os_g / setpoint * 100) if setpoint else 0.0

        # DATA vs SUMMARY cross-check (untuk laporan, tidak mengganti nilai)
        # (disimpan ke audit_data_vs_summary nanti)

    # Kolom turunan
    abs_error_g   = abs(final_error_g) if not math.isnan(final_error_g) else float("nan")
    abs_error_pct = abs(final_error_pct) if not math.isnan(final_error_pct) else float("nan")
    within_tol    = 1 if (not math.isnan(abs_error_pct) and abs_error_pct <= 5.0) else 0

    return {
        "Scenario":        scenario,
        "Controller":      CONTROLLER_MAP.get(scenario, scenario),
        "Setpoint_g":      setpoint,
        "TrialNo":         trial_no,
        "FileName":        path.name,
        "FinalMass_g":     final_mass,
        "FinalError_g":    final_error_g,
        "FinalError_pct":  final_error_pct,
        "AbsError_g":      abs_error_g,
        "AbsError_pct":    abs_error_pct,
        "MaxOvershoot_g":  max_os_g,
        "MaxOvershoot_pct": max_os_pct,
        "Duration_s":      duration_s,
        "TimeTo90_s":      time_to_90_s,
        "RiseTime_10_90_s": rt_s,
        "SettlingTime_s":  settling_s,
        "BridgingCount":   bridging,
        "Status":          status,
        "Valid":           valid,
        "StopReason":      stop_reason,
        "EarlyStop_g":     early_stop,
        "Notes":           float("nan"),   # selalu NaN
        "WithinTolerance": within_tol,
        # internal
        "_summary": summary,
        "_data_rows": data_rows,
    }


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

def scan_logs() -> list[dict]:
    rows = []
    for scenario in SCENARIO_ORDER:
        folder = LOG_ROOT / FOLDER_MAP[scenario]
        for sp in SETPOINT_ORDER:
            sp_folder = folder / f"SP{sp}"
            if not sp_folder.exists():
                print(f"  WARNING: folder tidak ada: {sp_folder}")
                continue
            txts = sorted(
                [f for f in sp_folder.iterdir() if f.suffix.lower() == ".txt"],
                key=lambda p: int(re.search(r"trial(\d+)", p.name, re.IGNORECASE).group(1))
                if re.search(r"trial(\d+)", p.name, re.IGNORECASE) else 0
            )
            for f in txts:
                rec = parse_log(f)
                rows.append(rec)
    return rows


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def _nan_eq(a, b) -> bool:
    try:
        return math.isnan(float(a)) and math.isnan(float(b))
    except (TypeError, ValueError):
        return False


def audit(regen: pd.DataFrame, canon: pd.DataFrame) -> list[dict]:
    audit_rows = []
    cols_to_check = [c for c in COLUMNS_OUT if c not in ("No", "Notes")]

    for _, rrow in regen.iterrows():
        sc, sp, tr = rrow["Scenario"], rrow["Setpoint_g"], rrow["TrialNo"]
        mask = (
            (canon["Scenario"] == sc) &
            (canon["Setpoint_g"] == sp) &
            (canon["TrialNo"] == tr)
        )
        crow_df = canon[mask]

        if crow_df.empty:
            audit_rows.append({
                "Scenario": sc, "Setpoint_g": sp, "TrialNo": tr,
                "Column": "ALL", "RegeneratedValue": "", "CanonicalValue": "",
                "AbsoluteDifference": "", "Tolerance": "",
                "Status": "NOT_VERIFIABLE", "Notes": "Row not found in canonical"
            })
            continue

        crow = crow_df.iloc[0]

        for col in cols_to_check:
            if col not in rrow.index or col not in crow.index:
                continue
            rv = rrow[col]
            cv = crow[col]

            if col in NUMERIC_TOL:
                tol = NUMERIC_TOL[col]
                if _nan_eq(rv, cv):
                    status, diff, note = "MATCH", 0.0, "Both NaN"
                elif _nan_eq(rv, cv) is False and (
                    (hasattr(rv, '__float__') and math.isnan(float(rv))) or
                    (hasattr(cv, '__float__') and math.isnan(float(cv)))
                ):
                    status, diff, note = "MISMATCH", float("nan"), "One is NaN"
                else:
                    try:
                        diff = abs(float(rv) - float(cv))
                        status = "MATCH" if diff <= tol else "MISMATCH"
                        note = "Within tolerance" if status == "MATCH" else "Outside tolerance"
                    except (TypeError, ValueError):
                        diff, status, note = "", "NOT_VERIFIABLE", "Cannot compare"
            else:
                # Exact
                rv_s = str(rv).strip()
                cv_s = str(cv).strip()
                # Normalise bool
                if rv_s.lower() in ("true", "false"):
                    rv_s = rv_s.capitalize()
                if cv_s.lower() in ("true", "false"):
                    cv_s = cv_s.capitalize()
                diff = ""
                if rv_s == cv_s:
                    status, note = "MATCH", "Exact match"
                else:
                    status, note = "MISMATCH", f"'{rv_s}' != '{cv_s}'"
                tol = "EXACT"

            audit_rows.append({
                "Scenario": sc, "Setpoint_g": sp, "TrialNo": tr,
                "Column": col,
                "RegeneratedValue": rv,
                "CanonicalValue": cv,
                "AbsoluteDifference": diff,
                "Tolerance": tol if col in NUMERIC_TOL else "EXACT",
                "Status": status,
                "Notes": note,
            })

    return audit_rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("generate_master_dataset.py")
    print("=" * 60)

    if not LOG_ROOT.exists():
        raise FileNotFoundError(f"Log root tidak ditemukan: {LOG_ROOT}")

    # 1. Scan
    print("Membaca log...")
    raw = scan_logs()
    print(f"  {len(raw)} log terbaca")

    # 2. Buat DataFrame, tambah No
    internal_keys = {"_summary", "_data_rows"}
    records = [{k: v for k, v in r.items() if k not in internal_keys} for r in raw]
    df = pd.DataFrame(records, columns=COLUMNS_OUT[1:])  # tanpa No dulu
    df.insert(0, "No", range(1, len(df) + 1))

    # 3. Validasi struktur
    expected = 4 * 4 * 10
    assert len(df) == expected, f"Baris terbentuk {len(df)}, expected {expected}"
    dups = df.duplicated(subset=["Scenario", "Setpoint_g", "TrialNo"])
    assert dups.sum() == 0, f"Duplikat ditemukan: {dups.sum()}"
    print(f"  Struktur OK: {len(df)} baris, 0 duplikat")

    # 4. Tulis CSV regenerasi (LF line ending untuk konsistensi lintas platform)
    out_csv = OUT_DIR / "master_dataset_160_regenerated.csv"
    df.to_csv(out_csv, index=False, lineterminator="\n")
    print(f"  Ditulis: {out_csv}")

    # 5. Hash — bandingkan regenerasi vs kanonis secara dinamis (tidak ada konstanta hardcode)
    sha_regen = hashlib.sha256(out_csv.read_bytes()).hexdigest().upper()
    sha_canon = hashlib.sha256(CANONICAL.read_bytes()).hexdigest().upper()
    print(f"  SHA-256 regenerasi : {sha_regen}")
    print(f"  SHA-256 kanonis    : {sha_canon}")
    hash_match = sha_regen == sha_canon

    # 6. Audit vs kanonis
    # Audit memeriksa 22 kolom data; No (nomor urut) dan Notes (semua kosong) dikecualikan.
    print("Audit vs dataset kanonis...")
    assert len(pd.read_csv(CANONICAL)) == 160, "Dataset kanonis bukan 160 baris"
    assert not pd.read_csv(CANONICAL).duplicated(["Scenario","Setpoint_g","TrialNo"]).any(), "Duplikat di kanonis"
    canon = pd.read_csv(CANONICAL)
    audit_rows = audit(df, canon)
    df_audit = pd.DataFrame(audit_rows)
    audit_csv = OUT_DIR / "audit_regenerated_vs_canonical.csv"
    df_audit.to_csv(audit_csv, index=False, lineterminator="\n")

    n_match    = (df_audit["Status"] == "MATCH").sum()
    n_mismatch = (df_audit["Status"] == "MISMATCH").sum()
    n_nv       = (df_audit["Status"] == "NOT_VERIFIABLE").sum()
    print(f"  MATCH: {n_match} | MISMATCH: {n_mismatch} | NOT_VERIFIABLE: {n_nv}")

    # 7. Ringkasan
    mismatch_by_col = {}
    if n_mismatch > 0:
        mismatch_by_col = (
            df_audit[df_audit["Status"] == "MISMATCH"]
            .groupby("Column").size().to_dict()
        )

    summary_lines = [
        "# Ringkasan Pembentukan Dataset",
        "",
        f"## Hasil Scan",
        f"- Log terbaca: {len(raw)}",
        f"- Baris terbentuk: {len(df)}",
        f"- Duplikat identitas: 0",
        "",
        f"## Hash SHA-256",
        f"- Regenerasi : `{sha_regen}`",
        f"- Kanonis    : `{sha_canon}`",
        f"- Cocok: {'✅ YA' if hash_match else '⚠️ TIDAK — nilai tetap diaudit per-sel'}",
        "",
        f"## Audit vs Kanonis",
        f"- MATCH: {n_match}",
        f"- MISMATCH: {n_mismatch}",
        f"- NOT_VERIFIABLE: {n_nv}",
    ]
    if mismatch_by_col:
        summary_lines += ["", "### MISMATCH per Kolom"]
        for col, cnt in sorted(mismatch_by_col.items(), key=lambda x: -x[1]):
            summary_lines.append(f"- {col}: {cnt}")

    summary_lines += [
        "",
        "## Status",
    ]
    if n_mismatch == 0 and n_nv == 0:
        summary_lines.append(
            "✅ Seluruh 160 baris dan 22 kolom data cocok dengan dataset kanonis "
            "(No dan Notes dikecualikan dari audit)."
        )
    else:
        summary_lines.append(
            f"⚠️ Ditemukan {n_mismatch} MISMATCH dan {n_nv} NOT_VERIFIABLE. "
            "Periksa audit_regenerated_vs_canonical.csv."
        )

    (OUT_DIR / "ringkasan_pembentukan_dataset.md").write_text(
        "\n".join(summary_lines), encoding="utf-8"
    )

    print(f"  Ringkasan ditulis.")
    print("=" * 60)
    if n_mismatch == 0 and n_nv == 0:
        print("SUKSES: 0 mismatch, 0 not-verifiable.")
    else:
        print(f"PERIKSA: {n_mismatch} mismatch, {n_nv} not-verifiable.")
    print("=" * 60)

    # Exit dengan kode berbeda agar pipeline CI dapat membedakan jenis kegagalan
    if n_mismatch > 0 or n_nv > 0:
        raise SystemExit(
            f"Audit data gagal: {n_mismatch} mismatch, {n_nv} not-verifiable."
        )
    if not hash_match:
        raise SystemExit(
            "Audit nilai cocok, tetapi serialisasi file tidak identik "
            "(hash berbeda — kemungkinan perbedaan line ending atau format float)."
        )


if __name__ == "__main__":
    main()
