# hasil/finalisasi

Folder ini diisi setelah menjalankan skrip Tahap 5:

```powershell
$env:PIPELINE_OUTPUT_DIR = "hasil\finalisasi"
python code/finalisasi/tahap5_generate_narasi_bab4.py
python code/finalisasi/tahap5_visualisasi_bab4.py
```

Output: `narasi_bab4.md`, `gambar_4_*.png/svg`, DOCX (opsional via `tahap5_generate_docx_bab4_revisi_terbatas.py`).
