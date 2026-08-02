# pemeriksaan_asumsi

## Tujuan
Uji normalitas residual dan homogenitas varians; hasilkan rekomendasi uji inferensial.

## Input
`data/pengujian_final/master_dataset_160.csv`

## Skrip Utama

`tahap2_pemeriksaan_asumsi.py`

Generator mandiri yang membaca dataset kanonis dan menghasilkan tiga CSV pemeriksaan
asumsi. Dapat dijalankan dari fresh clone tanpa baseline.

```
python code/pemeriksaan_asumsi/tahap2_pemeriksaan_asumsi.py
```

## Skrip Verifikasi Opsional

`tahap2_verifikasi_baseline.py`

Membandingkan hasil reproduksi dengan baseline terkunci. Skrip ini bukan bagian wajib
pipeline utama; digunakan untuk audit regresi.

## Output
`hasil/pemeriksaan_asumsi/`:
- `hasil_shapiro_residual_per_setpoint.csv`
- `hasil_brown_forsythe_per_setpoint.csv`
- `rekomendasi_uji_tahap3.csv`

## Hubungan dengan Skripsi
Shapiro-Wilk pada residual gabungan (n=40) per kombinasi metrik×setpoint. Bab III.
