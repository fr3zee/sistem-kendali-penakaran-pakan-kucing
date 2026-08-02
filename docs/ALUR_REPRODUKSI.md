# Alur Reproduksi

Repositori ini mendokumentasikan seluruh pipeline penelitian dari data mentah ke hasil akhir Bab IV.

## Pipeline

```
data/identifikasi_plant/          → MATLAB: penetapan parameter awal PID
    ↓
data/pilot_early_stop/            → pilot ES: pemilihan early stop 0,4 g
    ↓
firmware/                         → firmware final 4 skenario
    ↓
data/pengujian_final/log_160_trial/ → 160 trial (4 skenario × 4 SP × 10 trial)
    ↓
code/pembentukan_dataset/generate_master_dataset.py → master_dataset_160.csv
    ↓
data/pengujian_final/master_dataset_160.csv  (SHA-256 lihat bawah)
    ↓
code/validasi_dataset/            → integritas dataset
    ↓
code/sintesis_hasil/            → statistik deskriptif dasar
    ↓
code/pemeriksaan_asumsi/          → Shapiro-Wilk, Brown-Forsythe, rekomendasi uji
    ↓
code/analisis_inferensial/        → KW, Welch ANOVA, Holm, Dunn, Games-Howell, ES
    ↓
code/sintesis_hasil/            → profil primer, tambahan kondisional
    ↓
code/finalisasi/                  → visualisasi hasil dan validasi artefak akhir
```

## Tabel Proses

| Proses | Input | Skrip | Output |
|--------|-------|-------|--------|
| Pembentukan dataset | log_160_trial/ | generate_master_dataset.py | master_dataset_160_regenerated.csv, audit_regenerated_vs_canonical.csv, ringkasan_pembentukan_dataset.md |
| Validasi dataset | master_dataset_160.csv | tahap0_validasi_master_dataset.py | laporan_validasi_dataset.txt |
| Statistik deskriptif | master_dataset_160.csv | tahap1_statistik_deskriptif.py | hasil_statistik_deskriptif_tahap1.csv |
| Pemeriksaan asumsi | master_dataset_160.csv | tahap2_pemeriksaan_asumsi.py | hasil_shapiro_residual_per_setpoint.csv, hasil_brown_forsythe_per_setpoint.csv, rekomendasi_uji_tahap3.csv |
| Analisis inferensial | master_dataset_160.csv + rekomendasi_uji | tahap3_analisis_inferensial.py | hasil_omnibus_tahap3.csv, hasil_posthoc_tahap3.csv, hasil_proporsi_within_tolerance_*.csv |
| Sintesis hasil | master_dataset_160.csv + tahap3 outputs | tahap4_sintesis_multidimensi.py | tahap4_profil_primer.csv, tahap4_profil_tambahan_kondisional.csv |
| Finalisasi | tahap3+tahap4 outputs | tahap5_visualisasi_bab4.py | gambar 4.1–4.3 (PNG/SVG), audit_visual_tahap5.csv |

## Dataset Kanonis

- File: `data/pengujian_final/master_dataset_160.csv`
- SHA-256 (LF, publik): `69D57320EB1F56600CB8172241C0E941C630F2A5E67A2D99F18D01E811C2FFC6`
- 160 baris, 16 kombinasi (4 skenario × 4 setpoint), 10 trial per kombinasi

> Dataset kanonis dibentuk dari 160 log pengujian menggunakan `generate_master_dataset.py`. Skrip membaca deret waktu dan ringkasan setiap trial, menghitung metrik penelitian, dan menghasilkan dataset 160 baris yang diverifikasi identik dengan dataset final.
