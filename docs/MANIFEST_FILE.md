# Manifest File Inti

## Dataset Kanonis
- `data/pengujian_final/master_dataset_160.csv` — 160 trial, SHA-256 verified

## Log Trial (160 file)
- `data/pengujian_final/log_160_trial/{skenario}/SP{15,20,25,30}/` — 10 trial per SP

## Firmware Final
- `firmware/fixed_pid/` — Fixed PID v8 (Kp=2.50, Ki=0.15, Kd=0.03, ES=0.4g)
- `firmware/gain_scheduling_pid/` — GS PID v3 (3-zona, ES=0.4g)
- `firmware/manual_cepat/` — Manual Cepat (bukaan servo utama tetap dengan early stop berbasis massa)
- `firmware/manual_presisi/` — Manual Presisi (bukaan servo utama tetap dengan early stop berbasis massa)

## Identifikasi Plant
- `data/identifikasi_plant/` — 4 file step response (25/30/35/40 derajat)
- `code/eksperimen_awal/identifikasi_plant/zn_integrating_process.m`

## Pilot Early Stop
- `data/pilot_early_stop/baseline_es0/` — baseline ES=0g (agregat, raw_log_partial)
- `data/pilot_early_stop/kandidat_es/` — pilot ES 0.2/0.3/0.4g (74 trial, 4 skrip)

## Output Pipeline
- `hasil/pemeriksaan_asumsi/` — Shapiro, BF, rekomendasi uji
- `hasil/analisis_inferensial/` — omnibus, posthoc, within-tolerance
- `hasil/sintesis_hasil/` — deskriptif, profil primer/tambahan
- `hasil/finalisasi/` — gambar Bab IV, narasi, DOCX (dihasilkan oleh tahap5; jalankan script untuk mengisi)

## Reproduksibilitas
- `reproducibility/manifest_sha256.csv` — SHA-256 dataset kanonis
- `reproducibility/README.md` — status reproduksibilitas
- `archive/legacy_reproducibility/` — audit artefak lama (bukan audit dataset kanonis)
