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
data/pengujian_final/master_dataset_160.csv  (SHA-256 lihat bawah)
    ↓
code/validasi_dataset/            → integritas dataset
    ↓
code/sintesis_hasil/ (tahap1)     → statistik deskriptif dasar
    ↓
code/pemeriksaan_asumsi/          → Shapiro-Wilk, Brown-Forsythe, rekomendasi uji
    ↓
code/analisis_inferensial/        → KW, Welch ANOVA, Holm, Dunn, Games-Howell, ES
    ↓
code/sintesis_hasil/ (tahap4)     → profil primer, tambahan kondisional, dominasi
    ↓
code/finalisasi/                  → narasi Bab IV, gambar, DOCX
```

## Tabel Proses

| Proses | Input | Skrip | Output |
|--------|-------|-------|--------|
| Validasi dataset | master_dataset_160.csv | tahap0_validasi_master_dataset.py | laporan_validasi_dataset.txt |
| Statistik deskriptif | master_dataset_160.csv | tahap1_statistik_deskriptif.py | hasil_statistik_deskriptif_tahap1.csv |
| Pemeriksaan asumsi | master_dataset_160.csv | tahap2_rekonstruksi_dan_verifikasi.py | hasil_shapiro_residual_per_setpoint.csv, hasil_brown_forsythe_per_setpoint.csv, rekomendasi_uji_tahap3.csv |
| Analisis inferensial | master_dataset_160.csv + rekomendasi_uji | tahap3_analisis_inferensial.py + tahap3_generate_reports.py | hasil_omnibus_tahap3.csv, hasil_posthoc_tahap3.csv |
| Sintesis hasil | master_dataset_160.csv + tahap3 outputs | tahap4_sintesis_multidimensi.py | tahap4_profil_primer.csv, tahap4_profil_tambahan_kondisional.csv |
| Finalisasi | tahap3+tahap4 outputs | tahap5_*.py | narasi_bab4.md, gambar, DOCX |

## Dataset Kanonis

- File: `data/pengujian_final/master_dataset_160.csv`
- SHA-256: `79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C`
- 160 baris, 16 kombinasi (4 skenario × 4 setpoint), 10 trial per kombinasi

> Artefak audit tersedia di `reproducibility/audit.json` dan `reproducibility/walkthrough.md`.
> Tahap audit log–dataset belum dapat direproduksi; proses analisis lainnya tersedia.
