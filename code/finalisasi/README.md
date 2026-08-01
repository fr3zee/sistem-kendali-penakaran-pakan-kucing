# finalisasi

## Tujuan
Generate narasi, gambar Bab IV dari output pipeline sebelumnya.

## Input
`hasil/analisis_inferensial/`, `hasil/sintesis_hasil/`, `hasil/pemeriksaan_asumsi/`

## Skrip Utama
1. `tahap5_generate_narasi_bab4.py` — narasi_bab4.md (12 input)
2. `tahap5_visualisasi_bab4.py` — Gambar 4.1, 4.2, 4.3

## Output
`hasil/finalisasi/`

## Cara Menjalankan
```powershell
$env:PIPELINE_OUTPUT_DIR = "hasil\finalisasi"
python code/finalisasi/tahap5_generate_narasi_bab4.py
python code/finalisasi/tahap5_visualisasi_bab4.py
```

## Generator DOCX
Generator DOCX kanonis belum tersedia. Skrip versi lama telah dipindahkan ke `archive/legacy_finalisasi/`.

## Hubungan dengan Skripsi
Dokumen final Bab IV.
