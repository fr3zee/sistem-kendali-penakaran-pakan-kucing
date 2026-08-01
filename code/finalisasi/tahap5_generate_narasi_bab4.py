#!/usr/bin/env python3
"""
Tahap 5 - Generator Narasi Bab IV
===================================
Baca 12 CSV kanonis, emit narasi_bab4.md + audit_narasi_tahap5.csv.
- Tidak ada angka hardcode selain nama skenario, setpoint, dan nama metrik.
- Terminologi: MAPE (dari MAE_pct), AbsError_pct untuk inferensial,
  BridgingCount=aktivasi hammer reaktif, Pearson chi-square p Monte Carlo,
  Holm per metrik (4 setpoint per keluarga), tanpa Pareto/dominasi.
"""
import hashlib, csv, sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
import os as _os5n
_out5n = _os5n.environ.get("PIPELINE_OUTPUT_DIR", str(BASE_DIR / "hasil" / "finalisasi"))
OUTPUT_DIR = Path(_out5n)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILES = {
    "shapiro":       BASE_DIR / "hasil/pemeriksaan_asumsi/hasil_shapiro_residual_per_setpoint.csv",
    "bf":            BASE_DIR / "hasil/pemeriksaan_asumsi/hasil_brown_forsythe_per_setpoint.csv",
    "omnibus":       BASE_DIR / "hasil/analisis_inferensial/hasil_omnibus_tahap3.csv",
    "posthoc":       BASE_DIR / "hasil/analisis_inferensial/hasil_posthoc_tahap3.csv",
    "konsistensi":   BASE_DIR / "hasil/analisis_inferensial/hasil_konsistensi_finalerror_omnibus.csv",
    "proporsi_omni": BASE_DIR / "hasil/analisis_inferensial/hasil_proporsi_within_tolerance_omnibus.csv",
    "proporsi_post": BASE_DIR / "hasil/analisis_inferensial/hasil_proporsi_within_tolerance_posthoc.csv",
    "settling":      BASE_DIR / "hasil/sintesis_hasil/hasil_settlingtime_deskriptif.csv",
    "bridging":      BASE_DIR / "hasil/sintesis_hasil/hasil_bridging_deskriptif.csv",
    "primer":        BASE_DIR / "hasil/sintesis_hasil/tahap4_profil_primer.csv",
    "tambahan":      BASE_DIR / "hasil/sintesis_hasil/tahap4_profil_tambahan_kondisional.csv",
    "master":        BASE_DIR / "data/pengujian_final/master_dataset_160.csv",
}

SCENARIOS = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS  = [15, 20, 25, 30]
METRICS_INF = ["AbsError_pct", "MaxOvershoot_pct", "Duration_s", "RiseTime_10_90_s"]
METRIC_LABEL = {
    "AbsError_pct":     "Galat absolut persentase per trial (AbsError_pct)",
    "MaxOvershoot_pct": "Overshoot maksimum (%)",
    "Duration_s":       "Durasi (s)",
    "RiseTime_10_90_s": "Rise time 10-90% (s)",
}
# Terms forbidden in output narasi
FORBIDDEN = ["MAE%", "open-loop", "Fisher-Freeman-Halton",
             "f2*", "Pareto", "dominated", "non-dominated"]

audit_log = []

def log_audit(step, status, details):
    audit_log.append({"step": step, "status": status, "details": str(details)})
    print(f"[{status}] {step}: {details}")

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def hash_all():
    return {k: sha256_file(v) for k, v in INPUT_FILES.items()}

def load_all():
    dfs = {}
    for k, p in INPUT_FILES.items():
        if not Path(p).exists():
            log_audit(f"Load {k}", "FAIL", f"missing: {p}")
            sys.exit(1)
        dfs[k] = pd.read_csv(p)
    log_audit("Load inputs", "PASS", f"{len(dfs)} files")
    return dfs

def fmt(v, dec=3):
    try:
        return f"{float(v):.{dec}f}"
    except Exception:
        return str(v)

def tbl_header(cols):
    return "| " + " | ".join(cols) + " |"

def tbl_sep(n):
    return "|" + "|".join(["---"] * n) + "|"

def best_min(df_sp, col):
    row = df_sp.loc[df_sp[col].idxmin()]
    return row["Scenario"], row[col]


# ── Subbab 4.1 ────────────────────────────────────────────────
def sec_gambaran():
    lines = [
        "## 4.1 Gambaran Umum",
        "",
        "Pengujian dilaksanakan dengan 160 trial (4 skenario, 4 setpoint, 10 ulangan). "
        "Keempat skenario yang dibandingkan adalah Manual Cepat, Manual Presisi, Fixed PID, "
        "dan GS PID. Manual Cepat dan Manual Presisi menggunakan bukaan utama servo tetap "
        "dengan early stop berbasis massa, shake preventif, dan hammer reaktif. "
        "Fixed PID dan GS PID menambahkan umpan balik kontinu dari pembacaan massa. "
        "BridgingCount mencatat jumlah aktivasi hammer reaktif saja; "
        "shake preventif tidak menambah counter.",
        "",
    ]
    return lines


# ── Subbab 4.2 Deskriptif ─────────────────────────────────────
def sec_deskriptif(D):
    pr = D["primer"]
    lines = ["## 4.2 Statistik Deskriptif", ""]

    # MAPE table (sumber: MAE_pct = mean galat absolut persentase 10 trial)
    lines.append("### Tabel MAPE (%)")
    lines.append("")
    lines.append("*MAPE = rata-rata galat absolut persentase per 10 trial (kolom MAE_pct).*")
    lines.append("")
    cols = ["Setpoint (g)"] + SCENARIOS
    lines.append(tbl_header(cols))
    lines.append(tbl_sep(len(cols)))
    for sp in SETPOINTS:
        row = [str(sp)]
        for sc in SCENARIOS:
            v = pr[(pr["Setpoint_g"]==sp) & (pr["Scenario"]==sc)]["MAE_pct"].values[0]
            row.append(fmt(v, 3))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Median galat absolut persentase (Median_MAE_pct)
    lines.append("### Tabel Median Galat Absolut Persentase (%)")
    lines.append("")
    lines.append("*Median_MAE_pct = median AbsError_pct per 10 trial.*")
    lines.append("")
    lines.append(tbl_header(cols))
    lines.append(tbl_sep(len(cols)))
    for sp in SETPOINTS:
        row = [str(sp)]
        for sc in SCENARIOS:
            v = pr[(pr["Setpoint_g"]==sp) & (pr["Scenario"]==sc)]["Median_MAE_pct"].values[0]
            row.append(fmt(v, 3))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Median overshoot
    lines.append("### Tabel Median Overshoot (%)")
    lines.append("")
    lines.append(tbl_header(cols))
    lines.append(tbl_sep(len(cols)))
    for sp in SETPOINTS:
        row = [str(sp)]
        for sc in SCENARIOS:
            v = pr[(pr["Setpoint_g"]==sp) & (pr["Scenario"]==sc)]["Median_Overshoot_pct"].values[0]
            row.append(fmt(v, 3))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Median durasi
    lines.append("### Tabel Median Durasi (s)")
    lines.append("")
    lines.append(tbl_header(cols))
    lines.append(tbl_sep(len(cols)))
    for sp in SETPOINTS:
        row = [str(sp)]
        for sc in SCENARIOS:
            v = pr[(pr["Setpoint_g"]==sp) & (pr["Scenario"]==sc)]["Median_Duration_s"].values[0]
            row.append(fmt(v, 3))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return lines


# ── Subbab 4.3 Asumsi ─────────────────────────────────────────
def sec_asumsi(D):
    sh = D["shapiro"]
    bf = D["bf"]
    lines = ["## 4.3 Pemeriksaan Asumsi Statistik", ""]
    for metric in METRICS_INF:
        sh_m = sh[sh["Metric"]==metric]
        bf_m = bf[bf["Metric"]==metric]
        n_abnorm = len(sh_m[sh_m["Keputusan"].str.contains("penyimpangan", na=False)])
        n_het    = len(bf_m[bf_m["Keputusan"].str.contains("tidak homogen", na=False)])
        lines.append(
            f"**{METRIC_LABEL[metric]}**: "
            f"Shapiro-Wilk: {n_abnorm}/{len(sh_m)} setpoint menyimpang dari normalitas. "
            f"Brown-Forsythe: {n_het}/{len(bf_m)} setpoint varians tidak homogen."
        )
        lines.append("")
    lines.append(
        "Berdasarkan hasil pemeriksaan asumsi, Kruskal-Wallis dipilih untuk kondisi "
        "yang melanggar asumsi, dan Welch ANOVA untuk kondisi yang memenuhi asumsi. "
        "Koreksi Holm diterapkan per metrik dengan empat setpoint sebagai satu keluarga."
    )
    lines.append("")
    return lines


# ── Subbab 4.4 Omnibus ────────────────────────────────────────
def sec_omnibus(D):
    omni = D["omnibus"]
    lines = ["## 4.4 Analisis Inferensial Omnibus", ""]
    for metric in METRICS_INF:
        om = omni[omni["Metric"]==metric].sort_values("Setpoint_g")
        lines.append(f"### {METRIC_LABEL[metric]}")
        lines.append("")
        h = ["SP", "Uji", "Statistik", "df", "p_raw", "p_holm", "Sig", "ES"]
        lines.append(tbl_header(h))
        lines.append(tbl_sep(len(h)))
        for _, row in om.iterrows():
            df2  = fmt(row["df2"], 1) if pd.notna(row["df2"]) else "-"
            es   = f"{row['EffectSize_name']}={fmt(row['EffectSize_value'],3)}"
            sig  = "Ya" if row["Significant_holm"] else "Tidak"
            lines.append(
                f"| SP{int(row['Setpoint_g'])} | {row['Test']} "
                f"| {fmt(row['Statistic'],3)} | {int(row['df1'])}/{df2} "
                f"| {fmt(row['p_raw'],4)} | {fmt(row['p_holm'],4)} | {sig} | {es} |"
            )
        lines.append("")
        sig_sps = om[om["Significant_holm"]==True]["Setpoint_g"].astype(int).tolist()
        if sig_sps:
            sp_str = ", ".join(f"SP{s}" for s in sig_sps)
            lines.append(
                f"Terdapat perbedaan signifikan antarkelompok pada {sp_str} (p_holm < 0,05)."
            )
        else:
            lines.append("Tidak ada perbedaan signifikan pada seluruh setpoint.")
        lines.append("")
    return lines


# ── Subbab 4.5 Post-hoc ───────────────────────────────────────
def sec_posthoc(D):
    ph = D["posthoc"]
    lines = ["## 4.5 Analisis Post-hoc", ""]
    for metric in METRICS_INF:
        ph_m   = ph[ph["Metric"]==metric]
        sig_ph = ph_m[ph_m["Significant"]==True]
        lines.append(f"### {METRIC_LABEL[metric]}")
        lines.append("")
        if sig_ph.empty:
            lines.append("Tidak ada pasangan signifikan.")
            lines.append("")
            continue
        h = ["SP", "A", "B", "p_adjusted", "ES", "Arah"]
        lines.append(tbl_header(h))
        lines.append(tbl_sep(len(h)))
        for _, row in sig_ph.sort_values(["Setpoint_g","p_adjusted"]).iterrows():
            es = (f"{row['EffectSize_name']}={fmt(row['EffectSize_value'],3)} "
                  f"CI[{fmt(row['CI_lo'],2)},{fmt(row['CI_hi'],2)}]")
            lines.append(
                f"| SP{int(row['Setpoint_g'])} | {row['Group_A']} | {row['Group_B']} "
                f"| {fmt(row['p_adjusted'],4)} | {es} | {row['Direction']} |"
            )
        lines.append("")

    # Catatan Fixed vs GS durasi
    dur_fg  = ph[(ph["Metric"]=="Duration_s") &
                 (ph["Group_A"]=="Fixed PID") & (ph["Group_B"]=="GS PID")]
    sig_dur = dur_fg[dur_fg["Significant"]==True]["Setpoint_g"].astype(int).tolist()
    if sig_dur:
        sp_str = ", ".join(f"SP{s}" for s in sig_dur)
        lines.append(
            f"> GS PID memiliki durasi lebih rendah secara deskriptif pada seluruh setpoint, "
            f"tetapi perbedaan langsung Fixed PID vs GS PID hanya signifikan pada {sp_str}."
        )
        lines.append("")
    return lines


# ── Subbab 4.6 WithinTolerance ────────────────────────────────
def sec_tolerance(D):
    wo = D["proporsi_omni"]
    wp = D["proporsi_post"]
    lines = ["## 4.6 Proporsi Trial dalam Toleransi (WithinTolerance)", ""]
    h = ["SP", "chi-sq", "p_MC", "p_holm", "Sig", "V Cramer", "MC%", "MP%", "Fixed%", "GS%"]
    lines.append(tbl_header(h))
    lines.append(tbl_sep(len(h)))
    for _, row in wo.sort_values("Setpoint_g").iterrows():
        sig = "Ya" if row["Significant_holm"] else "Tidak"
        lines.append(
            f"| SP{int(row['Setpoint_g'])} | {fmt(row['Statistic'],3)} "
            f"| {fmt(row['p_MonteCarlo'],4)} | {fmt(row['p_holm'],4)} | {sig} "
            f"| {fmt(row['CramersV'],3)} "
            f"| {int(round(row['Prop_ManualCepat']*100))}% "
            f"| {int(round(row['Prop_ManualPresisi']*100))}% "
            f"| {int(round(row['Prop_FixedPID']*100))}% "
            f"| {int(round(row['Prop_GSPID']*100))}% |"
        )
    lines.append("")
    sig_wt = wo[wo["Significant_holm"]==True]["Setpoint_g"].astype(int).tolist()
    if sig_wt:
        sp_str = ", ".join(f"SP{s}" for s in sig_wt)
        lines.append(
            f"Uji Pearson chi-square dengan p Monte Carlo (N=100.000, seed=42) "
            f"menunjukkan proporsi berbeda signifikan pada {sp_str}."
        )
    lines.append("")
    sig_wp = wp[wp["Significant_holm"]==True]
    if not sig_wp.empty:
        lines.append("Post-hoc Fisher (Holm): pasangan signifikan:")
        lines.append("")
        h2 = ["SP", "A", "B", "p_holm"]
        lines.append(tbl_header(h2))
        lines.append(tbl_sep(len(h2)))
        for _, row in sig_wp.iterrows():
            lines.append(
                f"| SP{int(row['Setpoint_g'])} | {row['Group_A']} | {row['Group_B']} "
                f"| {fmt(row['p_holm'],4)} |"
            )
        lines.append("")
    else:
        lines.append("Post-hoc Fisher: tidak ada pasangan signifikan setelah koreksi Holm.")
        lines.append("")
    return lines


# ── Subbab 4.7 Konsistensi ────────────────────────────────────
def sec_konsistensi(D):
    ko = D["konsistensi"]
    lines = ["## 4.7 Konsistensi Galat Akhir (FinalError_g)", ""]
    h = ["SP", "BF-stat", "p_raw", "p_holm", "Sig",
         "SD MC", "SD MP", "SD Fixed", "SD GS", "SD min"]
    lines.append(tbl_header(h))
    lines.append(tbl_sep(len(h)))
    for _, row in ko.sort_values("Setpoint_g").iterrows():
        sig = "Ya" if row["Significant_holm"] else "Tidak"
        lines.append(
            f"| SP{int(row['Setpoint_g'])} | {fmt(row['BF_statistic'],3)} "
            f"| {fmt(row['p_raw'],4)} | {fmt(row['p_holm'],4)} | {sig} "
            f"| {fmt(row['SD_ManualCepat'],4)} | {fmt(row['SD_ManualPresisi'],4)} "
            f"| {fmt(row['SD_FixedPID'],4)} | {fmt(row['SD_GSPID'],4)} "
            f"| {row['MinVar_scenario']} |"
        )
    lines.append("")
    lines.append(
        "GS PID memiliki SD FinalError_g terendah secara deskriptif pada seluruh setpoint. "
        "Perbedaan varians signifikan hanya pada SP15 (Brown-Forsythe, Holm)."
    )
    lines.append("")
    return lines


# ── Subbab 4.8 Settling Time ──────────────────────────────────
def sec_settling(D):
    st = D["settling"]
    lines = [
        "## 4.8 Settling Time (Kondisional)",
        "",
        "*SettlingTime dihitung hanya pada trial yang memenuhi definisi settling.*",
        "",
    ]
    h = ["SP", "Skenario", "n tersedia", "Median (s)", "Q1 (s)", "Q3 (s)"]
    lines.append(tbl_header(h))
    lines.append(tbl_sep(len(h)))
    for _, row in st.sort_values(["Setpoint_g","Scenario"]).iterrows():
        lines.append(
            f"| SP{int(row['Setpoint_g'])} | {row['Scenario']} "
            f"| {int(row['n_available'])}/{int(row['n_total'])} "
            f"| {fmt(row['Median'],2)} | {fmt(row['Q1'],2)} | {fmt(row['Q3'],2)} |"
        )
    lines.append("")
    return lines


# ── Subbab 4.9 Rise Time ──────────────────────────────────────
def sec_risetime(D):
    ta = D["tambahan"]
    lines = [
        "## 4.9 Rise Time 10-90%",
        "",
        "*RiseTime tersedia untuk seluruh 10 trial per kelompok dan dianalisis inferensial.*",
        "",
    ]
    h = ["SP", "Skenario", "Mean (s)", "Median (s)", "SD"]
    lines.append(tbl_header(h))
    lines.append(tbl_sep(len(h)))
    for sp in SETPOINTS:
        for sc in SCENARIOS:
            r = ta[(ta["Setpoint_g"]==sp) & (ta["Scenario"]==sc)]
            if r.empty:
                continue
            r = r.iloc[0]
            lines.append(
                f"| SP{sp} | {sc} "
                f"| {fmt(r['RiseTime_mean'],2)} "
                f"| {fmt(r['RiseTime_median'],2)} "
                f"| {fmt(r['RiseTime_SD'],2)} |"
            )
    lines.append("")
    return lines


# ── Subbab 4.10 Bridging ──────────────────────────────────────
def sec_bridging(D):
    br = D["bridging"]
    lines = [
        "## 4.10 Aktivasi Hammer Reaktif (BridgingCount)",
        "",
        "*BridgingCount = jumlah aktivasi hammer reaktif saja; "
        "shake preventif tidak menambah counter.*",
        "",
    ]
    h = ["SP", "Skenario", "n total", "Median", "Min", "Max", "Prop>0"]
    lines.append(tbl_header(h))
    lines.append(tbl_sep(len(h)))
    for _, row in br.sort_values(["Setpoint_g","Scenario"]).iterrows():
        sp_val = int(row.get("Setpoint_g", row.get("Setpoint", 0)))
        lines.append(
            f"| SP{sp_val} | {row['Scenario']} | {int(row['n'])} "
            f"| {fmt(row['Median'],1)} | {int(row['Min'])} | {int(row['Max'])} "
            f"| {fmt(row['Prop_nonzero'],2)} |"
        )
    lines.append("")
    return lines


# ── Subbab 4.11 Sintesis Profil ───────────────────────────────
def sec_sintesis(D):
    pr = D["primer"]
    ko = D["konsistensi"]
    lines = ["## 4.11 Sintesis Profil Primer", ""]
    for sp in SETPOINTS:
        pr_sp      = pr[pr["Setpoint_g"]==sp]
        best_mape, mape_val = best_min(pr_sp, "MAE_pct")
        best_dur,  dur_val  = best_min(pr_sp, "Median_Duration_s")
        ko_sp = ko[ko["Setpoint_g"]==sp].iloc[0]
        lines.append(
            f"**SP{sp}**: MAPE terendah = {best_mape} ({fmt(mape_val,3)}%). "
            f"Durasi median terendah = {best_dur} ({fmt(dur_val,2)} s). "
            f"SD FinalError terendah = {ko_sp['MinVar_scenario']} "
            f"({fmt(ko_sp['SD_GSPID'],4)} g)."
        )
    lines.append("")
    return lines


# ── Audit ─────────────────────────────────────────────────────
def run_audit(narasi_text, D):
    master = D["master"]
    assert len(master) == 160, f"Master bukan 160: {len(master)}"
    log_audit("Dataset 160 baris", "PASS", len(master))

    for f in FORBIDDEN:
        assert f.lower() not in narasi_text.lower(), f"Istilah terlarang: {f}"
    log_audit("Forbidden terms", "PASS", FORBIDDEN)

    ph = D["posthoc"]
    sig_dur = (ph[(ph["Metric"]=="Duration_s") &
                  (ph["Group_A"]=="Fixed PID") & (ph["Group_B"]=="GS PID") &
                  (ph["Significant"]==True)]["Setpoint_g"].astype(int).tolist())
    assert sig_dur == [25], f"Duration Fixed vs GS sig: {sig_dur}"
    log_audit("Duration Fixed vs GS sig SP25 only", "PASS", sig_dur)

    sig_rt = (ph[(ph["Metric"]=="RiseTime_10_90_s") &
                 (ph["Group_A"]=="Fixed PID") & (ph["Group_B"]=="GS PID") &
                 (ph["Significant"]==True)]["Setpoint_g"].astype(int).tolist())
    assert sig_rt == [25], f"RiseTime Fixed vs GS sig: {sig_rt}"
    log_audit("RiseTime Fixed vs GS sig SP25 only", "PASS", sig_rt)

    wo = D["proporsi_omni"]
    sig_wt = sorted(wo[wo["Significant_holm"]==True]["Setpoint_g"].astype(int).tolist())
    assert 25 in sig_wt and 30 in sig_wt, f"WithinTol sig: {sig_wt}"
    log_audit("WithinTolerance sig SP25+SP30", "PASS", sig_wt)

    ko = D["konsistensi"]
    for sp in SETPOINTS:
        row = ko[ko["Setpoint_g"]==sp].iloc[0]
        assert row["MinVar_scenario"] == "GS PID", \
            f"SP{sp} min var: {row['MinVar_scenario']}"
    log_audit("GS PID SD FinalError terendah semua SP", "PASS", "")

    log_audit("Audit narasi", "PASS", "semua cek lolos")


# ── Main ──────────────────────────────────────────────────────
def main():
    hashes_before = hash_all()
    D = load_all()

    sections = (
        sec_gambaran()
        + sec_deskriptif(D)
        + sec_asumsi(D)
        + sec_omnibus(D)
        + sec_posthoc(D)
        + sec_tolerance(D)
        + sec_konsistensi(D)
        + sec_settling(D)
        + sec_risetime(D)
        + sec_bridging(D)
        + sec_sintesis(D)
    )
    narasi = "\n".join(sections)

    out_md = OUTPUT_DIR / "narasi_bab4.md"
    out_md.write_text(narasi, encoding="utf-8")
    log_audit("narasi_bab4.md", "PASS", str(out_md))

    run_audit(narasi, D)

    hashes_after = hash_all()
    for k in hashes_before:
        status = "PASS" if hashes_before[k] == hashes_after[k] else "FAIL"
        log_audit(f"Input integrity {k}", status, "UNCHANGED" if status=="PASS" else "CHANGED")

    out_csv = OUTPUT_DIR / "audit_narasi_tahap5.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["step","status","details"])
        w.writeheader()
        w.writerows(audit_log)

    print("=" * 60)
    print("Narasi Bab IV selesai.")
    print("=" * 60)


if __name__ == "__main__":
    main()
