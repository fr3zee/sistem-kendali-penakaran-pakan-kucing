# finalisasi

## Tujuan
Generate visualisasi hasil Bab IV dari output pipeline sebelumnya.

## Input
`hasil/analisis_inferensial/`, `hasil/sintesis_hasil/`, `hasil/pemeriksaan_asumsi/`

## Skrip
- `tahap5_visualisasi_bab4.py` — Gambar 4.1, 4.2, 4.3 (PNG + SVG)

## Output
`hasil/finalisasi/`

## Cara Menjalankan
```powershell
$env:PIPELINE_OUTPUT_DIR = "hasil\finalisasi"
python code/finalisasi/tahap5_visualisasi_bab4.py
```

## Generator DOCX dan Narasi
Generator narasi Bab IV tidak disertakan dalam repositori publik.
Generator DOCX kanonis belum tersedia. Skrip versi lama dipindahkan ke `archive/legacy_finalisasi/`.

## Hubungan dengan Skripsi
Dokumen final Bab IV.
