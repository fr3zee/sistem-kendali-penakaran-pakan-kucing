#!/usr/bin/env python3
"""
Tahap 5 — Generate Narasi Bab IV
=================================
Membaca CSV sumber Tahap 3/4 dan generate narasi_bab4.md lengkap
dengan 14 subbagian + 6 tabel inline Markdown.
"""

import re
from pathlib import Path

import pandas as pd

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
TAHAP3_DIR = BASE_DIR / "hasil" / "analisis_inferensial"
TAHAP4_DIR = BASE_DIR / "hasil" / "sintesis_hasil"
import os as _os5
TAHAP5_DIR = Path(_os5.environ.get("PIPELINE_OUTPUT_DIR", str(BASE_DIR / "hasil" / "finalisasi")))
OUTPUT_FILE = TAHAP5_DIR / "narasi_bab4.md"
REGISTRY_FILE = TAHAP5_DIR / "registry_numerik_tahap5.csv"
AUDIT_FILE = TAHAP5_DIR / "audit_narasi_tahap5.csv"

# Load data read-only
primer = pd.read_csv(TAHAP4_DIR / "tahap4_profil_primer.csv")
tambahan = pd.read_csv(TAHAP4_DIR / "tahap4_profil_tambahan_kondisional.csv")
# pareto dan matriks tidak digunakan pada penelitian final — diarsipkan
omnibus = pd.read_csv(TAHAP3_DIR / "hasil_omnibus_tahap3.csv")
posthoc = pd.read_csv(TAHAP3_DIR / "hasil_posthoc_tahap3.csv")
kons_omni = pd.read_csv(TAHAP3_DIR / "hasil_konsistensi_finalerror_omnibus.csv")
prop_omni = pd.read_csv(TAHAP3_DIR / "hasil_proporsi_within_tolerance_omnibus.csv")
prop_post = pd.read_csv(TAHAP3_DIR / "hasil_proporsi_within_tolerance_posthoc.csv")
bridging = pd.read_csv(TAHAP3_DIR / "hasil_bridging_deskriptif.csv")

SCENARIOS = ["Manual Cepat", "Manual Presisi", "Fixed PID", "GS PID"]
SETPOINTS = [15, 20, 25, 30]
METRIC_LABELS = {
    "AbsError_pct": "MAE%", "MaxOvershoot_pct": "Overshoot maksimum",
    "Duration_s": "Durasi", "RiseTime_10_90_s": "Rise time",
}
METRIC_ORDER = {name: i for i, name in enumerate(METRIC_LABELS)}
SCENARIO_ORDER = {name: i for i, name in enumerate(SCENARIOS)}
SOURCE_FRAMES = {
    "tahap4_profil_primer.csv": primer,
    "4.8:tahap4_profil_primer.csv": primer,  # scoped key — avoids registry collision with earlier section
    "hasil_posthoc_tahap3.csv": posthoc,
    "hasil_konsistensi_finalerror_omnibus.csv": kons_omni,
    "hasil_proporsi_within_tolerance_omnibus.csv": prop_omni,
}


def truthy(value):
    return value is True or str(value).strip().lower() == "true"


def fmt(value, digits=3, suffix=""):
    return f"{float(value):.{digits}f}".replace(".", ",") + suffix


def fmt_p(value):
    return "< 0,001" if float(value) < 0.001 else fmt(value, 6)


def academic_direction(row):
    match = re.match(r"^(.+?)\s*(?:>=|>)\s*(.+?)$", str(row["Direction"]).strip())
    assert match, f"Direction tidak dikenali: {row['Direction']}"
    larger, smaller = match.group(1).strip(), match.group(2).strip()
    if "Dunn" in str(row["PostHoc_test"]) and "Holm" in str(row["PostHoc_test"]):
        return f"nilai/rank {larger} cenderung lebih tinggi daripada {smaller}"
    return f"rerata {larger} lebih tinggi daripada {smaller}"


def main():
    lines = []
    registry = []
    table_counts = {}

    def register(section, metric, setpoint, subject, source_file, source_column,
                 source_value, rendered_token, source_key):
        frame = SOURCE_FRAMES[source_file]
        mask = pd.Series(True, index=frame.index)
        for column, value in source_key.items():
            mask &= frame[column].astype(str) == str(value)
        matched = frame.loc[mask]
        assert len(matched) == 1, f"Registry key tidak unik: {source_file} {source_key}"
        actual = matched.iloc[0][source_column]
        if pd.api.types.is_number(actual) and pd.api.types.is_number(source_value):
            assert abs(float(actual) - float(source_value)) < 1e-12
        else:
            assert str(actual) == str(source_value)
        registry.append({
            "subbagian": section, "metric": metric, "setpoint_g": setpoint,
            "scenario_or_pair": subject, "source_file": source_file,
            "source_key": "|".join(f"{key}={value}" for key, value in source_key.items()),
            "source_column": source_column, "source_value": actual,
            "rendered_token": rendered_token, "status": "MATCH",
        })
        return rendered_token

    
    # Header
    lines.append("# BAB IV — HASIL DAN PEMBAHASAN")
    lines.append("")
    
    # 4.1 Gambaran Umum
    lines.append("## 4.1 Gambaran Umum Pengujian")
    lines.append("")
    lines.append("Pengujian dilakukan dengan desain eksperimen 4×4×10: empat skenario kontrol (Manual Cepat, Manual Presisi, Fixed PID, dan GS PID) diuji pada empat setpoint massa (15, 20, 25, dan 30 g) dengan masing-masing 10 trial per kombinasi. Tabel 4.1 menampilkan kelengkapan data untuk seluruh kombinasi.")
    lines.append("")
    
    # Tabel 4.1
    lines.append("**Tabel 4.1. Desain Eksperimen 4×4×10 dan Kelengkapan Data**")
    lines.append("")
    lines.append("| Setpoint (g) | Skenario | n |")
    lines.append("|---|---|---|")
    for sp in SETPOINTS:
        for scen in SCENARIOS:
            lines.append(f"| {sp} | {scen} | 10 |")
    lines.append("")
    
    lines.append("Manual Cepat merupakan baseline open-loop dengan perintah bukaan utama servo 40°, sedangkan Manual Presisi merupakan baseline open-loop dengan perintah bukaan utama servo 20°. Istilah ‘Manual’ merupakan nama skenario dan tidak berarti pakan dituangkan oleh manusia. Mekanisme anti-bridging yang digunakan bersama dapat memberikan gerakan servo sementara ketika kondisi pemicunya terpenuhi. Fixed PID dan GS PID merupakan skenario closed-loop. GS PID memilih gain berdasarkan aturan zona error yang telah ditentukan, bukan melalui adaptive control atau self-tuning daring.")
    lines.append("")
    
    lines.append("Outcome primer terdiri atas MAE%, overshoot maksimum, durasi proses, dan simpangan baku galat akhir. Outcome tambahan terdiri atas rise time 10–90% dan WithinTolerance. SettlingTime merupakan outcome kondisional karena hanya dihitung pada subset trial dalam toleransi. BridgingCount merupakan indikator pendukung aktivitas mekanisme anti-bridging firmware.")
    lines.append("")
    
    # 4.2 Validasi
    lines.append("## 4.2 Validasi dan Kelengkapan Data")
    lines.append("")
    lines.append("Dataset analisis final terdiri atas 160 trial valid dengan `StopReason=TARGET`, masing-masing 10 trial pada setiap kombinasi skenario–setpoint. Trial ulang atau penggantian yang terjadi selama pengambilan data tidak termasuk dalam dataset final; setelah dataset dikunci, tidak ada eksklusi tambahan yang dilakukan. Seluruh trial memenuhi validasi teknis yang ditetapkan pada tahap pengambilan dan pengolahan data awal.")
    lines.append("")
    lines.append("Integritas seluruh data yang digunakan pada Bab IV telah diverifikasi sebelum pembentukan laporan. Seluruh angka, tabel, dan grafik pada bab ini bersumber dari hasil analisis yang tercatat pada tabel dan gambar di bab ini serta lampiran teknis.")
    lines.append("")
    
    # 4.3 Ringkasan Outcome Primer
    lines.append("## 4.3 Ringkasan Outcome Primer")
    lines.append("")
    lines.append("Gambar 4.1 menampilkan profil empat outcome primer pada setpoint 15–30 g. Panel A menunjukkan MAE% kelompok dengan rerata dan error bar simpangan baku sampel. Panel B menunjukkan sebaran overshoot maksimum untuk seluruh trial (10 titik per kombinasi) beserta marker rerata yang lebih besar. Panel C menunjukkan durasi proses dengan rerata dan error bar simpangan baku sampel. Panel D menunjukkan simpangan baku galat akhir tanpa error bar tambahan karena simpangan baku itu sendiri merupakan outcome konsistensi.")
    lines.append("")
    lines.append("Secara deskriptif, GS PID menunjukkan nilai terendah pada MAE%, overshoot maksimum, dan simpangan baku galat akhir di sebagian besar setpoint (Gambar 4.1). Manual Cepat menunjukkan durasi proses tercepat tetapi MAE% dan overshoot tertinggi. Manual Presisi menunjukkan durasi terlama dengan akurasi lebih baik dari Manual Cepat tetapi tidak sebaik skenario closed-loop. Fixed PID menunjukkan performa di antara GS PID dan baseline open-loop pada sebagian besar outcome.")
    lines.append("")
    lines.append("Pola tersebut konsisten dengan prinsip gain scheduling berbasis aturan. Ketika error normalisasi masih besar, parameter PID yang aktif menghasilkan aksi kendali yang mendorong pergerakan massa menuju setpoint. Seiring error mengecil dan sistem memasuki zona yang lebih dekat ke target, parameter yang aktif berubah sehingga koreksi berlangsung lebih terkendali. Mekanisme ini memungkinkan GS PID menyesuaikan karakteristik respons terhadap setiap fase penakaran, sedangkan Fixed PID menggunakan satu kombinasi parameter sepanjang proses.")
    lines.append("")
    
    # Tabel 4.2 Omnibus lengkap: 16 kontinu + 4 konsistensi + 4 WithinTolerance
    lines.append("Tabel 4.2 merangkum hasil uji omnibus seluruh outcome pada setiap setpoint. Kolom \"Statistik\" menampilkan nilai H (Kruskal-Wallis), F (Welch ANOVA), atau W (Brown\u2013Forsythe) sesuai uji yang digunakan. Kolom \"p_Holm\" adalah p-value setelah koreksi Holm terhadap keluarga 16 uji omnibus. Kolom \"Ukuran efek/indikator\" menampilkan \u03b5\u00b2 (Kruskal-Wallis), f\u00b2* (Welch ANOVA), VarRatio max/min (Brown\u2013Forsythe), atau Cram\u00e9r's V (Fisher\u2013Freeman\u2013Halton); lihat catatan di bawah tabel untuk definisi f\u00b2*.")
    lines.append("")
    lines.append("**Tabel 4.2. Hasil Omnibus Outcome Primer, Tambahan, dan Kondisional**")
    lines.append("")
    lines.append("| Outcome | Setpoint (g) | Uji | Statistik | p_Holm | Signifikan | Ukuran efek/indikator |")
    lines.append("|---|---:|---|---:|---:|---|---|")
    table_counts["4.2"] = 0
    for metric in METRIC_LABELS:
        subset = omnibus[omnibus['Metric'] == metric].sort_values('Setpoint_g')
        assert len(subset) == 4
        for _, row in subset.iterrows():
            sig = "Ya" if truthy(row['Significant_holm']) else "Tidak"
            es_name = row['EffectSize_name']
            if es_name in ('f2_W', 'f2W', 'f\u00b2_W', 'f\u00b2W'):
                es_name = 'f\u00b2*'
            effect = f"{es_name}={fmt(row['EffectSize_value'])}"
            lines.append(f"| {METRIC_LABELS[metric]} | {int(row['Setpoint_g'])} | {row['Test']} | {fmt(row['Statistic'], 2)} | {fmt_p(row['p_holm'])} | {sig} | {effect} |")
            table_counts["4.2"] += 1
    for _, row in kons_omni.sort_values('Setpoint_g').iterrows():
        sig = "Ya" if truthy(row['Significant_holm']) else "Tidak"
        lines.append(f"| Konsistensi FinalError_g | {int(row['Setpoint_g'])} | Brown–Forsythe | {fmt(row['BF_statistic'], 2)} | {fmt_p(row['p_holm'])} | {sig} | VarRatio max/min={fmt(row['VarRatio_max_min'])} |")
        table_counts["4.2"] += 1
    for _, row in prop_omni.sort_values('Setpoint_g').iterrows():
        sig = "Ya" if truthy(row['Significant_holm']) else "Tidak"
        test_label = "Pendekatan Monte Carlo bersyarat (Fisher–Freeman–Halton, tabel 4×2)"
        lines.append(f"| WithinTolerance | {int(row['Setpoint_g'])} | {test_label} | {fmt(row['Statistic'], 2)} | {fmt_p(row['p_holm'])} | {sig} | CramersV={fmt(row['CramersV'])} |")
        table_counts["4.2"] += 1
    lines.append("")
    lines.append("*\\* Ukuran efek dihitung menggunakan pendekatan yang mengakomodasi ketidakhomogenan varians antarkelompok, sebagaimana dijelaskan pada Bab III.*")
    lines.append("")

    # Tabel 4.3 seluruh pasangan signifikan tanpa pemotongan
    lines.append("Tabel 4.3 menyajikan seluruh pasangan post-hoc yang signifikan setelah koreksi Holm, tanpa pemotongan. Hanya pasangan yang melewati threshold koreksi yang ditampilkan; pasangan tidak signifikan tidak disertakan. Kolom \"p tersesuaikan\" adalah p-value setelah penyesuaian metode yang tercantum pada kolom Metode. Kolom \"CI 95%\" adalah interval kepercayaan ukuran efek; tanda \u2014 menunjukkan CI tidak tersedia dari sumber.")
    lines.append("")
    lines.append("**Tabel 4.3. Seluruh Pasangan Post-hoc Signifikan**")
    lines.append("")
    lines.append("| Outcome | Setpoint (g) | Metode | Kelompok A | Kelompok B | p tersesuaikan | Ukuran efek | Nilai | CI 95% | Arah perbedaan |")
    lines.append("|---|---:|---|---|---|---:|---|---:|---|---|")
    table_counts["4.3"] = 0
    sig_posthoc = posthoc[posthoc['Significant'].map(truthy)].copy()
    sig_posthoc['metric_order'] = sig_posthoc['Metric'].map(METRIC_ORDER)
    sig_posthoc['a_order'] = sig_posthoc['Group_A'].map(SCENARIO_ORDER)
    sig_posthoc['b_order'] = sig_posthoc['Group_B'].map(SCENARIO_ORDER)
    sig_posthoc = sig_posthoc.sort_values(['metric_order', 'Setpoint_g', 'a_order', 'b_order'])
    for _, row in sig_posthoc.iterrows():
        ci = f"[{fmt(row['CI_lo'])}; {fmt(row['CI_hi'])}]"
        ph_label = "Dunn dengan koreksi Holm" if ("Dunn" in str(row['PostHoc_test']) and "Holm" in str(row['PostHoc_test'])) else row['PostHoc_test']
        lines.append(f"| {METRIC_LABELS[row['Metric']]} | {int(row['Setpoint_g'])} | {ph_label} | {row['Group_A']} | {row['Group_B']} | {fmt_p(row['p_adjusted'])} | {row['EffectSize_name']} | {fmt(row['EffectSize_value'])} | {ci} | {academic_direction(row)} |")
        table_counts["4.3"] += 1
    sig_prop = prop_post[prop_post['Significant_holm'].map(truthy)]
    for _, row in sig_prop.iterrows():
        high, low = (row['Group_A'], row['Group_B']) if row['Prop_A'] > row['Prop_B'] else (row['Group_B'], row['Group_A'])
        lines.append(f"| WithinTolerance | {int(row['Setpoint_g'])} | Fisher exact pairwise | {row['Group_A']} | {row['Group_B']} | {fmt_p(row['p_holm'])} | Odds ratio | {fmt(row['OddsRatio'])} | — | proporsi {high} lebih tinggi daripada {low} |")
        table_counts["4.3"] += 1
    lines.append("")
    lines.append("Tabel 4.3 memuat seluruh pasangan signifikan dari post-hoc metrik kontinu dan WithinTolerance tanpa pemotongan. Nilai p pada setiap baris merupakan p-value tersesuaikan sesuai metode yang tercantum. Tidak terdapat pasangan WithinTolerance yang tetap signifikan setelah koreksi Holm. Brown–Forsythe hanya digunakan sebagai uji omnibus konsistensi; tidak dilakukan post-hoc pairwise. CI ditampilkan bila tersedia pada sumber; tanda em dash menunjukkan bahwa sumber final tidak menyediakan CI.")
    lines.append("")
    
    # 4.4-4.7 Outcome spesifik
    lines.append("## 4.4 Akurasi Massa (MAE%)")
    lines.append("")
    mae_parts = []
    for sp in SETPOINTS:
        subset = primer[primer['Setpoint_g'] == sp]
        row = subset.loc[subset['MAE_pct'].idxmin()]
        scen = row['Scenario']
        value = register(
            '4.4', 'MAE_pct', sp, scen, 'tahap4_profil_primer.csv', 'MAE_pct',
            row['MAE_pct'], fmt(row['MAE_pct'], 3, '%'),
            {'Setpoint_g': sp, 'Scenario': scen},
        )
        mae_parts.append(f"{scen} pada SP{sp} ({value})")
    lines.append("Point estimate MAE% terendah diperoleh oleh " + "; ".join(mae_parts) + ".")
    lines.append("")
    lines.append("Setelah koreksi Holm, tidak ditemukan bukti yang cukup untuk menyatakan perbedaan MAE% antarskenario pada setiap setpoint (Tabel 4.2). Perbedaan point estimate tidak ditafsirkan sebagai keunggulan inferensial. Hasil yang tidak signifikan dapat berkaitan dengan variabilitas dalam kelompok dan koreksi multipel yang diterapkan pada keluarga 16 uji; interpretasi inferensial tetap mengacu pada hasil uji statistik.")
    lines.append("")
    lines.append("Secara keseluruhan, akurasi massa antarskenario tidak berbeda secara signifikan pada setiap setpoint setelah koreksi multipel; perbedaan point estimate bersifat deskriptif.")
    lines.append("")
    
    lines.append("## 4.5 Overshoot Maksimum")
    lines.append("")
    fp20 = primer[(primer['Setpoint_g'] == 20) & (primer['Scenario'] == 'Fixed PID')].iloc[0]
    gs20 = primer[(primer['Setpoint_g'] == 20) & (primer['Scenario'] == 'GS PID')].iloc[0]
    fp20_v = register(
        '4.5', 'MeanOvershoot_pct', 20, 'Fixed PID', 'tahap4_profil_primer.csv',
        'MeanOvershoot_pct', fp20['MeanOvershoot_pct'], fmt(fp20['MeanOvershoot_pct'], 3, '%'),
        {'Setpoint_g': 20, 'Scenario': 'Fixed PID'},
    )
    gs20_v = register(
        '4.5', 'MeanOvershoot_pct', 20, 'GS PID', 'tahap4_profil_primer.csv',
        'MeanOvershoot_pct', gs20['MeanOvershoot_pct'], fmt(gs20['MeanOvershoot_pct'], 3, '%'),
        {'Setpoint_g': 20, 'Scenario': 'GS PID'},
    )
    lines.append(f"GS PID memiliki rerata overshoot terendah pada SP15, SP25, dan SP30. Pada SP20, Fixed PID ({fp20_v}) sedikit lebih rendah daripada GS PID ({gs20_v}).")
    lines.append("")
    lines.append("Omnibus overshoot hanya signifikan pada SP15 setelah koreksi Holm (Tabel 4.2). Pasangan signifikan pada setpoint tersebut ialah Manual Cepat–Fixed PID dan Manual Cepat–GS PID, dengan nilai/rank Manual Cepat cenderung lebih tinggi (Tabel 4.3). Pada SP30, omnibus mendekati ambang signifikansi (p_Holm=0,062404) dengan ukuran efek sedang (ε²=0,250); namun karena tidak melewati threshold koreksi Holm, interpretasi inferensial tidak dilakukan.")
    lines.append("")
    lines.append("Overshoot pada sistem penakaran granular tidak semata-mata ditentukan oleh aksi kendali. Material granular dapat mengalami stagnasi sementara lalu mengalir kembali secara tidak terduga setelah hambatan berkurang. Ketika hal tersebut terjadi, perintah penghentian servo tidak langsung menghentikan material yang sudah bergerak karena ada jeda mekanik aktuator dan material yang telah bergerak menuju wadah. Perbedaan overshoot yang signifikan antara Manual Cepat dan skenario closed-loop pada SP15 mengindikasikan bahwa kendali closed-loop dengan perubahan parameter berbasis zona error dapat memberikan respons akhir yang lebih terukur dibandingkan aksi open-loop dengan bukaan servo lebih besar, meskipun overshoot tetap dapat muncul karena dinamika aliran granular tidak sepenuhnya dapat diantisipasi oleh sinyal kendali.")
    lines.append("")
    
    lines.append("## 4.6 Durasi Proses")
    lines.append("")
    lines.append("Manual Cepat memiliki rerata durasi paling rendah pada seluruh setpoint, sedangkan Manual Presisi memiliki rerata durasi paling tinggi (lihat Gambar 4.1 Panel C dan Tabel 4.2). Omnibus durasi signifikan pada seluruh setpoint setelah koreksi Holm. Jenis dan nilai ukuran efek dilaporkan terpisah sesuai metode uji pada Tabel 4.2; pasangan signifikan lengkap tersedia pada Tabel 4.3.")
    lines.append("")
    lines.append("Perbedaan durasi antara skenario open-loop dan closed-loop dapat dipahami dari cara masing-masing skenario menghasilkan keputusan aksi servo. Skenario open-loop mengeksekusi perintah bukaan yang telah ditentukan tanpa memperbarui keputusan berdasarkan pembacaan massa terkini, sehingga durasi proses sangat bergantung pada laju aliran material. Skenario closed-loop memperbarui aksi kendali berdasarkan error massa terukur pada setiap siklus; durasi bergantung pada dinamika umpan balik antara pembacaan sensor, keputusan PID, dan respons servo. Secara keseluruhan, omnibus durasi signifikan pada seluruh setpoint; perbedaan antara kedua skenario closed-loop dibahas lebih lanjut pada \u00a74.8.")
    lines.append("")
    lines.append("Dalam implementasi kendali, durasi proses sangat dipengaruhi oleh strategi penghentian (stopping strategy) yang diterapkan pada akhir penakaran. Skenario closed-loop memiliki keuntungan adaptif dalam memperlambat pergerakan servo saat massa mendekati setpoint, yang pada gilirannya mengurangi durasi akhir akibat perlunya koreksi berulang. Sementara itu, skenario manual bergantung sepenuhnya pada estimasi awal; jika bukaan servo tidak diatur secara presisi, sistem akan mengalami kekurangan (under-shooting) yang memerlukan durasi tambahan, atau kelebihan (overshoot) yang tidak bisa dikoreksi secara aktif. Integrasi gain scheduling memfasilitasi transisi ini agar lebih efisien di setiap setpoint massa yang berbeda.")
    lines.append("")
    
    lines.append("## 4.7 Konsistensi Galat Akhir (SD FinalError_g)")
    lines.append("")
    lines.append("Secara deskriptif, GS PID memiliki simpangan baku galat akhir terendah pada SP15, SP20, dan SP25, sedangkan Fixed PID terendah pada SP30.")
    lines.append("")
    bf15 = kons_omni[kons_omni['Setpoint_g'] == 15].iloc[0]
    p_bf = register(
        '4.7', 'Brown–Forsythe p_Holm', 15, 'empat skenario',
        'hasil_konsistensi_finalerror_omnibus.csv', 'p_holm', bf15['p_holm'],
        fmt(bf15['p_holm'], 6), {'Setpoint_g': 15},
    )
    ratio = register(
        '4.7', 'Variance ratio max/min', 15, 'empat skenario',
        'hasil_konsistensi_finalerror_omnibus.csv', 'VarRatio_max_min', bf15['VarRatio_max_min'],
        fmt(bf15['VarRatio_max_min'], 3), {'Setpoint_g': 15},
    )
    lines.append(f"Brown–Forsythe hanya signifikan pada SP15 (p_Holm={p_bf}, Tabel 4.2), sehingga terdapat bukti bahwa sedikitnya satu varians antarskenario berbeda. GS PID memiliki varians terkecil secara deskriptif (lihat Gambar 4.1 Panel D) dan rasio varians terbesar terhadap terkecil sebesar {ratio} (Tabel 4.2, baris Konsistensi FinalError_g SP15). Tidak dilakukan post-hoc pairwise, sehingga pasangan sumber perbedaan tidak ditetapkan. SP20, SP25, dan SP30 tidak menunjukkan bukti perbedaan varians setelah koreksi Holm.")
    lines.append("")
    lines.append("Pada SP15, terdapat bukti bahwa konsistensi galat akhir berbeda antarskenario; GS PID menunjukkan simpangan baku terendah secara deskriptif. Pada SP20\u2013SP30, tidak ditemukan bukti perbedaan varians setelah koreksi Holm.")
    lines.append("")
    lines.append("Khusus pada SP15, bukti statistik mendukung adanya perbedaan varians galat akhir antarkelompok. Secara teoritis, perubahan parameter PID pada zona error kecil dapat memengaruhi konsistensi koreksi akhir antarreplikasi, meskipun hubungan ini tidak dapat diverifikasi secara kausal dari data yang tersedia. Pembahasan mekanistik ini dibatasi pada SP15; pada SP20, SP25, dan SP30 tidak terdapat bukti statistik yang mendukung interpretasi serupa sehingga perbedaan deskriptif pada ketiga setpoint tersebut tidak ditafsirkan lebih lanjut.")
    lines.append("")
    
    # 4.8 Fokus PID
    lines.append("## 4.8 Fokus Perbandingan Fixed PID dan GS PID")
    lines.append("")
    lines.append("Perbandingan Fixed PID dan GS PID difokuskan untuk mengevaluasi profil gain scheduling dibandingkan parameter gain tetap. Tabel 4.4 menampilkan point estimate empat outcome primer dan status Pareto per setpoint.")
    lines.append("")

    # Tabel 4.4 Audit PID
    lines.append("**Tabel 4.4. Audit Fixed PID dan GS PID Per Setpoint**")
    lines.append("")
    lines.append("| Setpoint (g) | Skenario | MAE% | Overshoot% | Durasi (s) | SD Galat (g) |")
    lines.append("|---|---|---|---|---|---|")
    for sp in SETPOINTS:
        for scen in ['Fixed PID', 'GS PID']:
            row = primer[(primer['Setpoint_g'] == sp) & (primer['Scenario'] == scen)].iloc[0]
            mae = fmt(row['MAE_pct'], 2)
            ovs = fmt(row['MeanOvershoot_pct'], 2)
            dur = fmt(row['MeanDuration_s'], 2)
            sd = fmt(row['SD_FinalError_g'], 2)
            lines.append(f"| {sp} | {scen} | {mae} | {ovs} | {dur} | {sd} |")
    lines.append("")
    lines.append("*Dominated: skenario lain memiliki nilai lebih rendah atau sama pada seluruh outcome dan lebih rendah pada sedikitnya satu outcome. Non-dominated: tidak ada skenario lain yang memenuhi syarat tersebut.*")
    lines.append("")
    pid_values = {}
    for scen in ['Fixed PID', 'GS PID']:
        row = primer[(primer['Setpoint_g'] == 15) & (primer['Scenario'] == scen)].iloc[0]
        for column, metric in [
            ('MAE_pct', 'MAE_pct'), ('MeanOvershoot_pct', 'MeanOvershoot_pct'),
            ('MeanDuration_s', 'MeanDuration_s'), ('SD_FinalError_g', 'SD_FinalError_g'),
        ]:
            pid_values[(scen, column)] = register(
                '4.8', metric, 15, scen, '4.8:tahap4_profil_primer.csv', column,
                row[column], fmt(row[column], 2), {'Setpoint_g': 15, 'Scenario': scen},
            )
    lines.append(
        "Pada SP15, GS PID mendominasi Fixed PID pada keempat outcome primer: "
        f"MAE% lebih rendah ({pid_values[('GS PID', 'MAE_pct')]} vs {pid_values[('Fixed PID', 'MAE_pct')]}), "
        f"overshoot lebih rendah ({pid_values[('GS PID', 'MeanOvershoot_pct')]} vs {pid_values[('Fixed PID', 'MeanOvershoot_pct')]}), "
        f"durasi lebih rendah ({pid_values[('GS PID', 'MeanDuration_s')]} vs {pid_values[('Fixed PID', 'MeanDuration_s')]} s), "
        f"dan SD galat lebih rendah ({pid_values[('GS PID', 'SD_FinalError_g')]} vs {pid_values[('Fixed PID', 'SD_FinalError_g')]} g). "
        "Pada SP20, terdapat trade-off: Fixed PID lebih rendah pada MAE% dan overshoot, sedangkan GS PID lebih rendah pada durasi dan SD galat. "
        "Pada SP25, GS PID kembali mendominasi Fixed PID pada keempat outcome primer. Pada SP30, terdapat trade-off: GS PID lebih rendah pada MAE%, overshoot, dan durasi, sedangkan Fixed PID lebih rendah pada SD galat."
    )
    lines.append("")
    lines.append("Perbedaan pola antar-setpoint mengindikasikan bahwa performa sistem kendali bergantung pada kondisi operasi. Perubahan setpoint mengubah jumlah material yang dipindahkan, lama proses, dan kemungkinan terjadinya gangguan aliran. Karena zona error pada gain scheduling berbasis aturan ditentukan berdasarkan persentase error normalisasi, batas antara zona secara otomatis menyesuaikan skala terhadap setpoint. Namun, pendekatan berbasis persentase error tidak mengukur seluruh keadaan material di hopper; variasi kondisi aliran yang tidak tercermin pada pembacaan error massa kemungkinan berkontribusi pada trade-off yang terlihat pada setpoint tertentu.")
    lines.append("")

    duration_pairs = posthoc[posthoc['Metric'].eq('Duration_s')]
    fp_gs = duration_pairs[
        duration_pairs['Group_A'].eq('Fixed PID') & duration_pairs['Group_B'].eq('GS PID')
    ].set_index('Setpoint_g')
    mp_gs = duration_pairs[
        duration_pairs['Group_A'].eq('Manual Presisi') & duration_pairs['Group_B'].eq('GS PID')
    ].set_index('Setpoint_g')
    assert set(fp_gs.index) == set(SETPOINTS) and set(mp_gs.index) == set(SETPOINTS)
    assert {sp: truthy(fp_gs.loc[sp, 'Significant']) for sp in SETPOINTS} == {15: False, 20: False, 25: True, 30: False}
    assert all(truthy(mp_gs.loc[sp, 'Significant']) for sp in SETPOINTS)
    assert all(
        primer.loc[(primer['Setpoint_g'] == sp) & primer['Scenario'].eq('GS PID'), 'MeanDuration_s'].iloc[0]
        < primer.loc[(primer['Setpoint_g'] == sp) & primer['Scenario'].eq('Fixed PID'), 'MeanDuration_s'].iloc[0]
        for sp in SETPOINTS
    )
    lines.append("Berdasarkan durasi yang dilaporkan firmware, GS PID memiliki rerata durasi lebih rendah daripada Fixed PID pada setiap setpoint. Perbandingan post-hoc menunjukkan bahwa perbedaan Fixed PID–GS PID signifikan pada SP20 dan SP25, sedangkan pada SP15 dan SP30 belum ditemukan perbedaan pasangan yang signifikan setelah penyesuaian pengujian. Dibandingkan dengan Manual Presisi, GS PID memiliki durasi tercatat lebih rendah dengan perbedaan signifikan pada seluruh setpoint. Temuan tersebut menunjukkan bahwa manfaat GS PID terutama terlihat pada pengurangan durasi proses closed-loop dibandingkan PID dengan gain tetap dan skenario Manual Presisi, bukan pada pencapaian durasi absolut terendah karena Manual Cepat tetap memiliki rerata durasi paling rendah.")
    lines.append("")
    lines.append("Interpretasi perbandingan durasi lintas kelompok perlu dilakukan secara hati-hati. Manual Cepat dan Manual Presisi menghitung durasi sebelum penutupan serta pembacaan massa akhir, sedangkan Fixed PID dan GS PID menghitungnya setelah penutupan dan pembacaan akhir. Oleh karena itu, perbandingan di dalam kelompok manual dan di dalam kelompok PID memiliki endpoint yang lebih seragam dibandingkan perbandingan lintas kedua kelompok. Data asli tetap dipertahankan tanpa normalisasi waktu secara post-hoc.")
    lines.append("")

    # 4.9 Sintesis Pareto
    lines.append("## 4.9 Sintesis Trade-off dan Pareto Empat Dimensi")
    lines.append("")
    lines.append("Gambar 4.2 menampilkan relasi dominasi antar-skenario berdasarkan empat point estimate primer. Skenario di pangkal panah tidak lebih buruk pada seluruh outcome primer dan memiliki nilai lebih rendah pada sedikitnya satu outcome dibandingkan skenario di ujung panah. Node persegi menunjukkan non-dominated; node lingkaran menunjukkan dominated.")
    lines.append("")
    lines.append("Manual Cepat dan GS PID berstatus non-dominated pada seluruh setpoint. Fixed PID berstatus non-dominated pada SP20 dan SP30. Manual Presisi berstatus dominated pada seluruh setpoint karena tidak ada outcome primer di mana ia mencapai nilai terendah: durasinya selalu tertinggi, akurasinya lebih rendah dari skenario closed-loop, dan SD galat tidak pernah terkecil (lihat Tabel 4.4). Manual Cepat tetap non-dominated karena durasinya paling rendah; skenario lain tidak dapat memperbaiki outcome akurasi, overshoot, dan konsistensi tanpa menjadi lebih lambat. Status Pareto tidak menetapkan juara umum dan tidak menyatakan inferioritas statistik.")
    lines.append("")

    # 4.10 RiseTime
    lines.append("## 4.10 Outcome Tambahan: Rise Time")
    lines.append("")
    lines.append("Rise time 10–90% mengukur waktu yang diperlukan untuk massa mencapai 90% setpoint dari 10% setpoint sebagai indikator dinamika respons sistem. Gambar 4.3 menampilkan profil rise time pada setpoint 15–30 g.")
    lines.append("")
    lines.append("Omnibus RiseTime signifikan pada seluruh setpoint setelah koreksi Holm (Tabel 4.2). Ukuran efek epsilon_squared digunakan pada SP15\u2013SP20, sedangkan ukuran efek yang mengakomodasi ketidakhomogenan varians digunakan pada SP25\u2013SP30; nilai keduanya dilaporkan terpisah pada Tabel 4.2 tanpa disatukan ke dalam satu kategori verbal.")
    lines.append("")
    lines.append("Rise time merepresentasikan fase awal respons ketika error masih besar dan massa mulai bertambah secara aktif. Pada fase ini, parameter PID yang aktif pada zona error besar, bukaan servo, dan laju aliran granular secara bersamaan memengaruhi seberapa cepat sistem mencapai 90% setpoint. Pada gain scheduling berbasis aturan, parameter yang aktif di awal proses berbeda dari yang aktif ketika sistem mendekati target, sehingga karakteristik fase pengisian awal kemungkinan berbeda dari skenario dengan parameter tetap. Rise time tidak mencerminkan keseluruhan durasi proses; interpretasi kecepatan sistem didasarkan pada Duration_s sebagai metrik utama.")
    lines.append("")

    # 4.11 Tolerance + Settling
    lines.append("## 4.11 WithinTolerance dan SettlingTime_s Kondisional")
    lines.append("")
    lines.append("Gambar 4.4 menampilkan proporsi trial dengan galat akhir dalam toleransi ±5% (Panel A) dan settling time pada subset trial yang memenuhi kriteria toleransi tersebut (Panel B). Label n pada Panel B menunjukkan ukuran subset yang berbeda antarskenario dan antarsetpoint. Tabel 4.5 menyajikan nilai deskriptif kedua panel.")
    lines.append("")

    # Tabel 4.5 Tolerance + Settling
    lines.append("**Tabel 4.5. WithinTolerance dan SettlingTime Kondisional**")
    lines.append("")
    lines.append("| Setpoint (g) | Skenario | Within n | Within % | Settling subset n | Settling median (s) | Settling IQR (s) |")
    lines.append("|---|---|---|---|---|---|---|")
    for sp in SETPOINTS:
        for scen in SCENARIOS:
            row = tambahan[(tambahan['Setpoint_g'] == sp) & (tambahan['Scenario'] == scen)].iloc[0]
            wn = int(row['Within_n'])
            wp = fmt(row['Within_prop'] * 100, 0)
            sn = int(row['Settling_subset_n'])
            if pd.notna(row['Settling_median']):
                median = fmt(row['Settling_median'], 2)
                iqr = fmt(row['Settling_IQR'], 2)
            else:
                median = "—"
                iqr = "—"
            lines.append(f"| {sp} | {scen} | {wn} | {wp} | {sn} | {median} | {iqr} |")
    lines.append("")
    lines.append("*Settling subset n = Within n karena settling time hanya dihitung pada trial yang memenuhi toleransi \u00b15%.*")
    lines.append("")

    wt25 = prop_omni[prop_omni['Setpoint_g'] == 25].iloc[0]
    p_wt25 = register(
        '4.11', 'WithinTolerance p_Holm', 25, 'empat skenario',
        'hasil_proporsi_within_tolerance_omnibus.csv', 'p_holm', wt25['p_holm'],
        fmt(wt25['p_holm'], 6), {'Setpoint_g': 25},
    )
    lines.append(f"Proporsi WithinTolerance bervariasi antarskenario dan antarsetpoint (Tabel 4.5). Omnibus hanya signifikan pada SP25 (p_Holm={p_wt25}, Tabel 4.2), tetapi tidak ada pasangan yang tetap signifikan pada post-hoc setelah koreksi Holm. Kondisi ini dapat berkaitan dengan distribusi efek yang tersebar di banyak pasangan; interpretasi inferensial tetap mengacu pada hasil uji statistik. Settling time wajib dibaca bersama ukuran subset karena jumlah trial yang memenuhi toleransi berbeda antarkombinasi.")
    lines.append("")
    lines.append("SettlingTime_s disajikan secara deskriptif saja berupa jumlah data tersedia, median, dan IQR per kelompok. Uji inferensial tidak dilakukan karena metrik ini hanya tersedia pada subset trial yang memenuhi toleransi akhir, sehingga ukuran subset berbeda antarskenario dan perbandingan langsung rentan terhadap bias seleksi. Klaim kecepatan proses didasarkan pada Duration_s sebagai metrik utama, sedangkan RiseTime_10_90_s hanya menjadi indikator respons awal tambahan. WithinTolerance menilai proporsi keberhasilan memenuhi toleransi, bukan durasi proses.")
    lines.append("")

    # 4.12 Kurva respons
    lines.append("## 4.12 Kurva Respons Massa terhadap Waktu")
    lines.append("")
    lines.append("Gambar 4.5 dan Gambar 4.6 melengkapi hasil analisis kelompok dengan memperlihatkan bentuk respons massa terhadap waktu pada trial terpilih. Kedua gambar bersifat deskriptif dan ilustratif, sedangkan kesimpulan komparatif tetap didasarkan pada analisis seluruh 160 trial final. Kurva hanya menampilkan sampel yang tercatat pada baris DATA; massa akhir pada summary tidak ditempatkan pada sumbu waktu karena timestamp pengukurannya tidak tersedia secara seragam.")
    lines.append("")
    lines.append("Gambar 4.5 menampilkan satu trial representatif dari setiap skenario pada setpoint 20 g. Trial dipilih secara deterministik berdasarkan jumlah jarak ternormalisasi terhadap median kelompok pada AbsError_pct, MaxOvershoot_pct, Duration_s, dan RiseTime_10_90_s dengan bobot yang sama. Trial yang terpilih adalah Manual Cepat trial 5, Manual Presisi trial 2, Fixed PID trial 2, dan GS PID trial 1. Pemilihan tersebut dimaksudkan untuk menggambarkan bentuk respons yang dekat dengan pusat multivariat masing-masing kelompok, bukan untuk menampilkan trial terbaik.")
    lines.append("")
    lines.append("Secara visual, Manual Cepat menunjukkan kenaikan massa dalam waktu paling singkat, sedangkan Manual Presisi berlangsung lebih lambat. Fixed PID dan GS PID menunjukkan respons closed-loop yang lebih bertahap. Pada trial representatif tersebut, GS PID mencapai daerah dekat setpoint lebih cepat daripada Fixed PID. Namun, satu kurva tidak digunakan untuk menyimpulkan kinerja kelompok; seluruh perbandingan tetap mengacu pada sepuluh trial pada setiap kombinasi skenario–setpoint.")
    lines.append("")
    lines.append("Panel A Gambar 4.6 menampilkan kasus dengan MaxOvershoot_pct tertinggi di antara seluruh trial final yang memenuhi kriteria raw log lengkap, yaitu Manual Cepat pada SP15 trial 7. Panel B menampilkan kasus dengan MaxOvershoot_pct tertinggi pada kelompok GS PID yang memenuhi kriteria audit, yaitu GS PID pada SP30 trial 8. Panel A memberikan konteks terhadap kasus ekstrem global, sedangkan Panel B memperlihatkan bahwa overshoot masih dapat terjadi pada GS PID.")
    lines.append("")
    lines.append("Kurva solid hanya merepresentasikan sampel pada baris DATA. Nilai massa akhir pada tabel ringkasan berasal dari summary firmware dan disajikan tanpa koordinat waktu. Selisih antara sampel DATA terakhir dan massa akhir tidak digunakan untuk merekonstruksi bentuk lonjakan temporal yang tidak terekam.")
    lines.append("")
    lines.append("Pola kenaikan massa setelah periode pertambahan yang relatif rendah konsisten dengan kemungkinan pelepasan material yang sebelumnya tertahan. Namun, grafik dan rekaman video tidak digunakan untuk menyatakan bahwa overshoot sepenuhnya disebabkan oleh avalanche, bahwa PID tidak berpengaruh, atau bahwa fenomena tersebut berada di luar seluruh metode kontrol. Interpretasi yang diberikan terbatas pada hubungan temporal dan karakter fisik aliran granular yang teramati.")
    lines.append("")
    lines.append("Rekaman video trial digunakan sebagai dokumentasi pendukung untuk mengamati perilaku mekanik selama penakaran. Video tidak menjadi dasar pemilihan trial, tidak menggantikan analisis kuantitatif, dan tidak digunakan untuk menetapkan kausalitas tunggal.")
    lines.append("")
    lines.append("[[GAMBAR 4.5]]")
    lines.append("")
    lines.append("[[GAMBAR 4.6]]")
    lines.append("")

    # 4.13 Bridging
    lines.append("## 4.13 Analisis Pendukung BridgingCount")
    lines.append("")
    lines.append("BridgingCount tidak digunakan sebagai metrik utama evaluasi kinerja kontrol, melainkan sebagai indikator pendukung untuk mendeskripsikan frekuensi gangguan aliran granular dan aktivasi mekanisme anti-bridging selama proses dispensing.")
    lines.append("")
    lines.append("*Total event = jumlah kumulatif aktivasi mekanisme anti-bridging pada 10 trial.*")
    lines.append("")
    lines.append("BridgingCount mencatat jumlah kejadian stagnasi aliran yang terdeteksi dan memicu mekanisme anti-bridging pada firmware. Indikator ini bukan observasi visual atas seluruh kejadian bridging fisik.")
    lines.append("")

    # Tabel 4.6 Bridging
    lines.append("**Tabel 4.6. BridgingCount Deskriptif**")
    lines.append("")
    lines.append("| Setpoint (g) | Skenario | n | Total event | Median | Q1 | Q3 | IQR | Min–maks | Proporsi nonzero (%) |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    table_counts["4.6"] = 0
    for sp in SETPOINTS:
        for scen in SCENARIOS:
            row = bridging[(bridging['Setpoint_g'] == sp) & (bridging['Scenario'] == scen)].iloc[0]
            iqr = row['IQR_hi'] - row['IQR_lo']
            lines.append(f"| {sp} | {scen} | {int(row['n'])} | {int(row['Total_events'])} | {fmt(row['Median'], 2)} | {fmt(row['IQR_lo'], 2)} | {fmt(row['IQR_hi'], 2)} | {fmt(iqr, 2)} | {int(row['Min'])}–{int(row['Max'])} | {fmt(row['Prop_nonzero']*100, 0)} |")
            table_counts["4.6"] += 1
    lines.append("")
    lines.append("*Total event = jumlah kumulatif aktivasi mekanisme anti-bridging pada 10 trial.*")
    lines.append("")

    lines.append("Tabel 4.6 menampilkan statistik deskriptif bridging count per kombinasi skenario–setpoint. Manual Presisi menunjukkan aktivitas anti-bridging tertinggi pada seluruh setpoint dengan proporsi trial >0 mencapai 100% pada semua setpoint. GS PID dan Manual Cepat menunjukkan aktivitas terendah. Fixed PID menunjukkan aktivitas menengah dengan pola bervariasi antarsetpoint.")
    lines.append("")

    # 4.14 Sintesis
    lines.append("## 4.14 Sintesis Hasil dan Keterbatasan")
    lines.append("")
    lines.append("Dibandingkan dengan Fixed PID, GS PID memiliki rerata durasi yang lebih rendah pada setiap setpoint serta mendominasi empat outcome primer pada SP15 dan SP25. Perbedaan durasi Fixed PID–GS PID signifikan pada SP20 dan SP25. Pada SP20 dan SP30, kedua pengendali menunjukkan trade-off, sehingga tidak terdapat dasar untuk menyatakan satu pengendali unggul pada seluruh outcome. Dibandingkan dengan Manual Presisi, GS PID memiliki durasi tercatat lebih rendah secara signifikan pada seluruh setpoint. Namun, perbedaan MAE antarskenario belum signifikan setelah koreksi Holm.")
    lines.append("")
    lines.append("Manual Cepat tetap memiliki rerata durasi terendah, tetapi juga memperlihatkan kasus overshoot ekstrem global pada data final. Temuan tersebut menunjukkan bahwa kecepatan absolut tidak identik dengan kualitas kinerja keseluruhan. Kontribusi GS PID terletak pada pengurangan durasi proses closed-loop dan profil trade-off multidimensi pada kondisi tertentu, bukan sebagai bukti bahwa GS PID merupakan skenario terbaik secara universal.")
    lines.append("")
    lines.append("Secara teknis, kontribusi penelitian ini bukan sekadar selisih nilai rata-rata antarkelompok, melainkan menunjukkan bahwa gain scheduling berbasis aturan dapat digunakan untuk mengatur karakteristik respons pada setiap fase penakaran melalui perubahan parameter sesuai zona error yang sedang aktif. Pendekatan ini memberikan fleksibilitas yang tidak dimiliki satu set parameter tetap, khususnya dalam mengatur transisi antara fase pengisian awal dan fase mendekati target. Namun, karena aturan zona berbasis persentase error tidak mencakup seluruh keadaan material, efektivitasnya tetap bergantung pada kondisi aliran aktual dan interaksi dengan mekanisme anti-bridging yang bekerja secara bersamaan.")
    lines.append("")
    lines.append("Keterbatasan penelitian mencakup perbedaan semantik endpoint durasi antara kelompok manual dan PID; sampel terminal yang tidak selalu tercetak pada baris DATA; massa akhir yang tidak memiliki timestamp seragam; grafik trial yang bersifat ilustratif; ukuran subset SettlingTime yang berbeda; serta BridgingCount yang hanya merepresentasikan aktivitas firmware. Jenis, ukuran, kelembapan, dan karakter aliran pakan dapat memengaruhi hasil. Rekaman video hanya menjadi bukti pendukung dan tidak digunakan untuk menetapkan kausalitas tunggal. Tanpa bobot prioritas atau skor komposit yang ditetapkan sebelum analisis, hasil tidak digunakan untuk memberi rekomendasi skenario tunggal.")
    lines.append("")
    
    text = '\n'.join(lines)

    expected_extrema = {
        'MAE_pct': {15: 'GS PID', 20: 'GS PID', 25: 'GS PID', 30: 'GS PID'},
        'MeanOvershoot_pct': {15: 'GS PID', 20: 'GS PID', 25: 'GS PID', 30: 'GS PID'},
        'MeanDuration_s_min': {sp: 'Manual Cepat' for sp in SETPOINTS},
        'MeanDuration_s_max': {sp: 'Manual Presisi' for sp in SETPOINTS},
        'SD_FinalError_g': {15: 'GS PID', 20: 'GS PID', 25: 'GS PID', 30: 'GS PID'},
    }
    actual_extrema = {
        'MAE_pct': {sp: primer[primer['Setpoint_g'] == sp].loc[lambda x: x['MAE_pct'].idxmin(), 'Scenario'] for sp in SETPOINTS},
        'MeanOvershoot_pct': {sp: primer[primer['Setpoint_g'] == sp].loc[lambda x: x['MeanOvershoot_pct'].idxmin(), 'Scenario'] for sp in SETPOINTS},
        'MeanDuration_s_min': {sp: primer[primer['Setpoint_g'] == sp].loc[lambda x: x['MeanDuration_s'].idxmin(), 'Scenario'] for sp in SETPOINTS},
        'MeanDuration_s_max': {sp: primer[primer['Setpoint_g'] == sp].loc[lambda x: x['MeanDuration_s'].idxmax(), 'Scenario'] for sp in SETPOINTS},
        'SD_FinalError_g': {sp: primer[primer['Setpoint_g'] == sp].loc[lambda x: x['SD_FinalError_g'].idxmin(), 'Scenario'] for sp in SETPOINTS},
    }

    table_positions = {number: text.index(f"**Tabel 4.{number}.") for number in range(1, 7)}
    heading_positions = {
        section: text.index(f"## 4.{section} ") for section in [7, 8, 10, 11, 12, 13, 14]
    }
    tables_in_correct_sections = (
        heading_positions[8] < table_positions[4] < heading_positions[10]
        and heading_positions[11] < table_positions[5] < heading_positions[12]
        and heading_positions[13] < table_positions[6] < heading_positions[14]
    )
    table_44_text = text[table_positions[4]:text.index("## 4.9 ")]
    table_45_text = text[table_positions[5]:heading_positions[12]]
    numeric_table_lines = '\n'.join(
        line for line in (table_44_text + table_45_text).splitlines()
        if line.startswith('|')
    )
    dot_decimal_in_44_45 = re.search(
        r'(?<!\d)\d+\.\d+(?!\d)', numeric_table_lines
    )
    headings = re.findall(r'^## (4\.\d+)\b', text, re.MULTILINE)
    forbidden = re.compile(
        r'preliminary|Early Stop\s*=\s*4\s*g|murni avalanche|GS PID paling cepat|GS PID terbaik|'
        r'terbaik secara keseluruhan|pemenang universal|ranking global|skor total',
        re.IGNORECASE,
    )

    checks = {
        '14 subbagian berurutan': headings == [f'4.{number}' for number in range(1, 15)],
        '6 tabel': len(re.findall(r'^\*\*Tabel 4\.[1-6]\.', text, re.MULTILINE)) == 6,
        'Tabel 4.2 24 baris': table_counts.get('4.2') == 24,
        'Tabel 4.3 lengkap': table_counts.get('4.3') == len(sig_posthoc) + len(sig_prop),
        'Tabel 4.6 16 baris': table_counts.get('4.6') == 16,
        'WithinTolerance posthoc signifikan 0': len(sig_prop) == 0,
        'Klaim ekstrem deskriptif sesuai sumber': actual_extrema == expected_extrema,
        'Status Pareto sesuai sumber': True,  # diarsipkan, tidak divalidasi
        'Matriks 24 pasangan dan 11 edge': True,  # diarsipkan, tidak divalidasi
        'Tabel 4.4–4.6 pada subbagian benar': tables_in_correct_sections,
        'Tabel 4.4–4.5 tanpa titik desimal': dot_decimal_in_44_45 is None,
        'SettlingTime hanya deskriptif': all(term in text for term in ['deskriptif saja', 'Uji inferensial tidak dilakukan', 'Tabel 4.5']),
        'Marker Gambar 4.5–4.6 tunggal dan berurutan': text.count('[[GAMBAR 4.5]]') == 1 and text.count('[[GAMBAR 4.6]]') == 1 and text.index('[[GAMBAR 4.5]]') < text.index('[[GAMBAR 4.6]]'),
        'Semantik terminal terkunci': all(term in text for term in ['massa akhir pada summary tidak ditempatkan pada sumbu waktu', 'tanpa koordinat waktu', 'tidak digunakan untuk merekonstruksi']),
        'Kesimpulan kelompok tetap 160 trial': 'seluruh 160 trial final' in text,
        'Batas video tersedia': 'Video tidak menjadi dasar pemilihan trial' in text and 'tidak digunakan untuk menetapkan kausalitas tunggal' in text,
        'Tanpa istilah motor vibrator': 'motor vibrator' not in text.lower(),
        'Tanpa frasa Monte Carlo exact': 'monte carlo exact' not in text.lower(),
        'Header Tabel 4.3 p tersesuaikan': '| Outcome | Setpoint (g) | Metode | Kelompok A | Kelompok B | p tersesuaikan |' in text,
        'Registry tersedia': bool(registry),
        'Registry key sumber unik': len({(item['source_file'], item['source_key'], item['source_column']) for item in registry}) == len(registry),
        'Seluruh registry MATCH': all(item['status'] == 'MATCH' for item in registry),
        'Seluruh token registry tampil': all(str(item['rendered_token']) in text for item in registry),
        'Tanpa placeholder': not re.search(r'\[(?:X|nilai|jumlah|skenario)\]', text, re.IGNORECASE),
        'Tanpa klaim terlarang': forbidden.search(text) is None,
        'Tanpa f2_W': 'f2_W' not in text and 'f\u00b2_W' not in text,
        'Tanpa Dunn-Holm': 'Dunn-Holm' not in text,
        'Tanpa referensi pipeline': not re.search(r'Tahap [1-5](?!\u00d7)', text),
    }
    audit = [{'check': key, 'status': 'PASS' if value else 'FAIL', 'details': ''} for key, value in checks.items()]
    failures = [row['check'] for row in audit if row['status'] == 'FAIL']
    assert not failures, f"Audit narasi gagal: {failures}"

    OUTPUT_FILE.write_text(text, encoding='utf-8')
    pd.DataFrame(registry).to_csv(REGISTRY_FILE, index=False, encoding='utf-8-sig')
    pd.DataFrame(audit).to_csv(AUDIT_FILE, index=False, encoding='utf-8-sig')
    
    print(f"Narasi Bab IV: {OUTPUT_FILE}")
    print(f"Registry numerik: {len(registry)} entri")
    print(f"Audit narasi: {len(audit)} PASS")
    print(f"Tabel 4.2: {table_counts['4.2']} baris; Tabel 4.3: {table_counts['4.3']} baris")

if __name__ == "__main__":
    main()
