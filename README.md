# Perancangan dan Implementasi Kontrol PID dengan Gain Scheduling Berbasis Aturan pada Sistem Penakaran Pakan Kucing Otomatis

**Penulis:** Naufal Hilmi Fathul Ihsan
**Program Studi:** Teknik Komputer, UNNES
**Status:** PASS DENGAN CATATAN — skrip audit log↔dataset belum tersedia

---

## Status Pipeline

| Proses | Skrip | Status |
|--------|-------|--------|
| Validasi dataset | tahap0_validasi_master_dataset.py | ✅ |
| Statistik deskriptif | tahap1_statistik_deskriptif.py | ✅ |
| Pemeriksaan asumsi | tahap2_rekonstruksi_dan_verifikasi.py | ✅ (prasyarat: lihat bawah) |
| Analisis inferensial | tahap3_analisis_inferensial.py + tahap3_generate_reports.py | ✅ |
| Sintesis hasil | tahap4_sintesis_multidimensi.py | ✅ |
| Finalisasi Bab IV | tahap5_visualisasi_bab4.py | ✅ |
| Skrip audit log↔dataset | — | ❌ MISSING |

---

## Diagram Pipeline

```
data/identifikasi_plant/          → MATLAB: parameter awal PID
    ↓
data/pilot_early_stop/            → pilot ES: pilih early stop 0,4 g
    ↓
firmware/                         → firmware final 4 skenario
    ↓
data/pengujian_final/log_160_trial/ → 160 trial (4 skenario × 4 SP × 10)
    ↓
data/pengujian_final/master_dataset_160.csv
    ↓
code/validasi_dataset/            → integritas dataset
    ↓
code/sintesis_hasil/ (tahap1)     → statistik deskriptif dasar
    ↓
code/pemeriksaan_asumsi/          → Shapiro-Wilk, Brown-Forsythe, rekomendasi uji
    ↓
code/analisis_inferensial/        → KW, Welch ANOVA, Holm, Dunn, Games-Howell, ES
    ↓
code/sintesis_hasil/ (tahap4)     → profil primer, tambahan kondisional
    ↓
code/finalisasi/                  → visualisasi hasil dan validasi artefak akhir
```

---

## Struktur Folder

```
.
├── firmware/
│   ├── fixed_pid/                # Fixed PID v8
│   ├── gain_scheduling_pid/      # GS PID v3 (3-zona)
│   ├── manual_cepat/             # Manual Cepat (ES berbasis massa)
│   └── manual_presisi/           # Manual Presisi (ES berbasis massa)
├── data/
│   ├── identifikasi_plant/       # 4 step response MATLAB
│   ├── pilot_early_stop/         # pilot ES 0,2/0,3/0,4 g + baseline ES 0 g
│   └── pengujian_final/
│       ├── master_dataset_160.csv
│       └── log_160_trial/        # 160 raw log (.txt)
├── code/
│   ├── eksperimen_awal/          # MATLAB identifikasi plant
│   ├── validasi_dataset/         # tahap0
│   ├── sintesis_hasil/           # tahap1 + tahap4
│   ├── pemeriksaan_asumsi/       # tahap2
│   ├── analisis_inferensial/     # tahap3
│   └── finalisasi/               # tahap5
├── hasil/
│   ├── validasi_dataset/
│   ├── sintesis_hasil/
│   ├── pemeriksaan_asumsi/
│   ├── analisis_inferensial/
│   └── finalisasi/               # gambar Bab IV, narasi, DOCX
├── docs/                         # ALUR_REPRODUKSI.md, MANIFEST_FILE.md, dll.
├── archive/                      # output arsip (Pareto, matriks dominasi)
└── reproducibility/
    ├── README.md
    ├── manifest_sha256.csv
    └── test_run/
```

---

## Cara Menjalankan

```powershell
# Setiap skrip mendukung PIPELINE_OUTPUT_DIR untuk output test
$env:PIPELINE_OUTPUT_DIR = "reproducibility\test_run\validasi_dataset"
python code/validasi_dataset/tahap0_validasi_master_dataset.py

$env:PIPELINE_OUTPUT_DIR = "reproducibility\test_run\sintesis_hasil"
python code/sintesis_hasil/tahap1_statistik_deskriptif.py

# Tahap 2 butuh baseline CSV di hasil/pemeriksaan_asumsi/ — lihat code/pemeriksaan_asumsi/README.md
python code/pemeriksaan_asumsi/tahap2_rekonstruksi_dan_verifikasi.py

$env:PIPELINE_OUTPUT_DIR = "reproducibility\test_run\analisis_inferensial"
python code/analisis_inferensial/tahap3_analisis_inferensial.py
python code/analisis_inferensial/tahap3_generate_reports.py

$env:PIPELINE_OUTPUT_DIR = "reproducibility\test_run\sintesis_hasil"
python code/sintesis_hasil/tahap4_sintesis_multidimensi.py

$env:PIPELINE_OUTPUT_DIR = "reproducibility\test_run\finalisasi"
python code/finalisasi/tahap5_generate_narasi_bab4.py
python code/finalisasi/tahap5_visualisasi_bab4.py
```

---

## Dataset Kanonis

- File: `data/pengujian_final/master_dataset_160.csv`
- SHA-256: `79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C`
- 160 baris, 16 kombinasi (4 skenario × 4 setpoint), 10 trial per kombinasi
- Verifikasi: `python -c "import hashlib; print(hashlib.sha256(open('data/pengujian_final/master_dataset_160.csv','rb').read()).hexdigest().upper())"`

---

## Catatan Reproduksibilitas

- Pengujian reproduksi berhasil pada proses validasi dataset, statistik deskriptif, analisis inferensial, sintesis hasil, dan finalisasi. Pemeriksaan asumsi direproduksi menggunakan keluaran acuan yang telah dibekukan — lihat `code/pemeriksaan_asumsi/README.md`
- Skrip audit log↔dataset: MISSING — dicatat di `docs/MISSING_CORE_FILES.md`
- Pareto dan matriks dominasi diarsipkan di `archive/archived_outputs/` — tidak digunakan dalam analisis final

---

## Lisensi

Hak cipta 2026 Naufal Hilmi. Dibuat untuk tugas akhir (skripsi) di Universitas Negeri Semarang (UNNES). Penggunaan ulang untuk keperluan akademik diperbolehkan dengan atribusi yang sesuai.
