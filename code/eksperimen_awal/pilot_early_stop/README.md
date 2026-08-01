# pilot_early_stop

## Tujuan
Ekstraksi, agregasi, QC, dan rekomendasi dari uji pilot early stop (ES 0.2/0.3/0.4 g).

## Input
`data/pilot_early_stop/kandidat_es/raw_log/` → `pilot_ES_master.csv`

## Skrip (urutan eksekusi)
1. `pilot_ES_parser.py` — baca log → pilot_ES_master.csv (CANONICAL)
2. `pilot_ES_summarize.py` — master → summary_all_valid + balanced_3trial (CANONICAL)
3. `pilot_ES_QC.py` — validasi data → pilot_ES_QC_report.md (SUPPORTING)
4. `pilot_ES_recommend.py` — summary → pilot_ES_rekomendasi.md (CANONICAL)

## Output
`data/pilot_early_stop/kandidat_es/`

## Hubungan dengan Skripsi
ES 0.4g dipilih sebagai konfigurasi final. Bab III + Lampiran 4.
