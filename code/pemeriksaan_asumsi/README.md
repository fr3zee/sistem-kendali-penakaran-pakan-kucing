# pemeriksaan_asumsi

## Tujuan
Uji normalitas residual dan homogenitas varians; hasilkan rekomendasi uji inferensial.

## Input
`data/pengujian_final/master_dataset_160.csv`

## Skrip Utama
`tahap2_rekonstruksi_dan_verifikasi.py`

## Output
`hasil/pemeriksaan_asumsi/`: hasil_shapiro_residual_per_setpoint.csv, hasil_brown_forsythe_per_setpoint.csv, rekomendasi_uji_tahap3.csv

## Cara Menjalankan
```
python code/pemeriksaan_asumsi/tahap2_rekonstruksi_dan_verifikasi.py
```

## Hubungan dengan Skripsi
Shapiro-Wilk pada residual gabungan (n=40) per kombinasi metrik×setpoint. Bab III.
