# sintesis_hasil

## Tujuan
Dua skrip dengan fungsi berbeda:

1. `tahap1_statistik_deskriptif.py` — statistik deskriptif dasar per Scenario×Setpoint
2. `tahap4_sintesis_multidimensi.py` — profil primer dan profil tambahan kondisional

## Input
`data/pengujian_final/master_dataset_160.csv` + output analisis_inferensial

## Output
`hasil/sintesis_hasil/`: hasil_statistik_deskriptif_tahap1.csv, tahap4_profil_primer.csv, tahap4_profil_tambahan_kondisional.csv, hasil_settlingtime_deskriptif.csv, hasil_bridging_deskriptif.csv

## Cara Menjalankan
```
python code/sintesis_hasil/tahap1_statistik_deskriptif.py
python code/sintesis_hasil/tahap4_sintesis_multidimensi.py
```

## Hubungan dengan Skripsi
Dasar tabel Bab IV.
