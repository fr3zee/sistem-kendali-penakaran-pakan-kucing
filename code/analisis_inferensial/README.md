# analisis_inferensial

## Tujuan
Kruskal-Wallis / Welch ANOVA, koreksi Holm, post-hoc Dunn/Games-Howell, ukuran efek.
Uji proporsi 4×2: Pearson chi-square dengan p Monte Carlo; post-hoc 2×2 Fisher exact dengan koreksi Holm.

## Input
`data/pengujian_final/master_dataset_160.csv`, `hasil/pemeriksaan_asumsi/rekomendasi_uji_tahap3.csv`

## Skrip Utama
`tahap3_analisis_inferensial.py` — analisis utama (satu skrip kanonis)

## Output
`hasil/analisis_inferensial/`: hasil_omnibus_tahap3.csv, hasil_posthoc_tahap3.csv, hasil_proporsi_within_tolerance_*.csv, hasil_konsistensi_finalerror_omnibus.csv

`hasil/sintesis_hasil/`: hasil_settlingtime_deskriptif.csv, hasil_bridging_deskriptif.csv

## Cara Menjalankan
```
python code/analisis_inferensial/tahap3_analisis_inferensial.py
```

## Hubungan dengan Skripsi
Keputusan pemilihan uji (KW vs Welch) didasarkan pada hasil pemeriksaan asumsi di `hasil/pemeriksaan_asumsi/`. Bab IV tabel utama.
