# hasil/finalisasi

Folder diisi setelah menjalankan skrip Tahap 5:

```powershell
$env:PIPELINE_OUTPUT_DIR = "hasil\finalisasi"
python code/finalisasi/tahap5_generate_narasi_bab4.py
python code/finalisasi/tahap5_visualisasi_bab4.py
```

Output: `narasi_bab4.md`, `gambar_4_1_outcome_primer.png/svg`, `gambar_4_2_risetime.png/svg`, `gambar_4_3_tolerance_settling.png/svg`.

Generator DOCX kanonis belum tersedia. Skrip versi lama telah dipindahkan ke `archive/legacy_finalisasi/`.
