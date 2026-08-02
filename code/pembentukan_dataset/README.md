# pembentukan_dataset

## Tujuan

Membentuk `master_dataset_160.csv` dari 160 log trial mentah.

## Skrip

`generate_master_dataset.py`

Membaca `data/pengujian_final/log_160_trial/` (4 skenario × 4 setpoint × 10 trial),
mengekstrak blok `=== SUMMARY TRIAL ===` sebagai sumber utama metrik,
menggunakan deret `DATA` sebagai fallback dan verifikasi,
menghitung kolom turunan (`AbsError_g`, `AbsError_pct`, `WithinTolerance`),
lalu menulis tiga output ke `hasil/pembentukan_dataset/`.

## Input

```
data/pengujian_final/log_160_trial/
├── fixed_pid/SP{15,20,25,30}/Fixed PID_SP{nn}_trial{01-10}.txt
├── gs_pid/SP{15,20,25,30}/GSPID_SSP{nn}_trial{01-10}.txt
├── manual_cepat/SP{15,20,25,30}/ManualCepat_SP{nn}_trial{01-10}.txt
└── manual_presisi/SP{15,20,25,30}/ManualPresisi_SP{nn}_trial{01-10}.txt
```

## Output

```
hasil/pembentukan_dataset/
├── master_dataset_160_regenerated.csv   # dataset hasil regenerasi (160 baris, 24 kolom)
├── audit_regenerated_vs_canonical.csv   # perbandingan per-sel vs dataset kanonis
└── ringkasan_pembentukan_dataset.md     # ringkasan + hash SHA-256
```

## Cara Menjalankan

```bash
python code/pembentukan_dataset/generate_master_dataset.py
```

Jalankan dari root repositori.

## Verifikasi

SHA-256 hasil regenerasi harus cocok dengan dataset kanonis:

```
79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C
```

## Catatan

Skrip merupakan implementasi kanonis yang direkonstruksi berdasarkan format log,
firmware final, dan definisi operasional penelitian, kemudian diverifikasi terhadap
dataset final. SHA-256 keluaran identik dengan dataset kanonis.
