# analisis_inferensial

## Tujuan
Kruskal-Wallis / Welch ANOVA, koreksi Holm, post-hoc Dunn/Games-Howell, ukuran efek.

## Input
`data/pengujian_final/master_dataset_160.csv`, `hasil/pemeriksaan_asumsi/rekomendasi_uji_tahap3.csv`

## Skrip Utama
1. `tahap3_analisis_inferensial.py` — analisis utama
2. `tahap3_generate_reports.py` — generate laporan CSV

## Output
`hasil/analisis_inferensial/`: hasil_omnibus_tahap3.csv, hasil_posthoc_tahap3.csv, hasil_proporsi_within_tolerance_*.csv

## Cara Menjalankan
```
python code/analisis_inferensial/tahap3_analisis_inferensial.py
python code/analisis_inferensial/tahap3_generate_reports.py
```

## Hubungan dengan Skripsi
Keputusan uji dibekukan di `keputusan_analisis_statistik_final.md`. Bab IV tabel utama.
