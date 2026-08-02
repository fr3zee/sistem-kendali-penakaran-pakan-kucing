# Perancangan dan Implementasi Kontrol PID dengan Gain Scheduling Berbasis Aturan pada Sistem Penakaran Pakan Kucing Otomatis

**Penulis:** Naufal Hilmi Fathul Ihsan
**Program Studi:** Teknik Komputer, UNNES
**Status:** PASS DENGAN CATATAN

---

## Status Pipeline

| Proses | Skrip | Status |
|--------|-------|--------|
| Pembentukan dataset dari log | generate_master_dataset.py | ✅ |
| Validasi dataset | tahap0_validasi_master_dataset.py | ✅ |
| Statistik deskriptif | tahap1_statistik_deskriptif.py | ✅ |
| Pemeriksaan asumsi | tahap2_pemeriksaan_asumsi.py | ✅ |
| Analisis inferensial | tahap3_analisis_inferensial.py | ✅ |
| Sintesis hasil | tahap4_sintesis_multidimensi.py | ✅ |
| Finalisasi Bab IV | tahap5_visualisasi_bab4.py | ✅ |

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
code/pembentukan_dataset/         → generate_master_dataset.py → master_dataset_160.csv
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
│   ├── pembentukan_dataset/      # generate_master_dataset.py
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
│   └── finalisasi/               # visualisasi hasil Bab IV
├── docs/                         # ALUR_REPRODUKSI.md, MANIFEST_FILE.md, dll.
└── reproducibility/
    ├── README.md
    ├── manifest_sha256.csv
    └── verification_report.md
```

---

## Cara Menjalankan

```powershell
python code/pembentukan_dataset/generate_master_dataset.py

python code/validasi_dataset/tahap0_validasi_master_dataset.py

python code/sintesis_hasil/tahap1_statistik_deskriptif.py

python code/pemeriksaan_asumsi/tahap2_pemeriksaan_asumsi.py

python code/analisis_inferensial/tahap3_analisis_inferensial.py

python code/sintesis_hasil/tahap4_sintesis_multidimensi.py

python code/finalisasi/tahap5_visualisasi_bab4.py
```

---

## Dataset Kanonis

- File: `data/pengujian_final/master_dataset_160.csv`
- SHA-256 (LF, publik): `69D57320EB1F56600CB8172241C0E941C630F2A5E67A2D99F18D01E811C2FFC6`
- 160 baris, 16 kombinasi (4 skenario × 4 setpoint), 10 trial per kombinasi
- Verifikasi: `python -c "import hashlib; print(hashlib.sha256(open('data/pengujian_final/master_dataset_160.csv','rb').read()).hexdigest().upper())"`

---

## Catatan Reproduksibilitas

- Pembentukan dataset dari 160 log, pemeriksaan asumsi, analisis inferensial, sintesis hasil,
  dan visualisasi telah dijalankan dan diverifikasi.
- Dataset hasil regenerasi identik dengan dataset kanonis (SHA-256 LF publik):
  `69D57320EB1F56600CB8172241C0E941C630F2A5E67A2D99F18D01E811C2FFC6`.
- Rincian proses yang tersedia dan yang telah diverifikasi terdapat pada
  `reproducibility/verification_report.md`.

---

## Lisensi

Repositori ini menggunakan MIT License. Penggunaan, modifikasi, dan distribusi mengikuti ketentuan pada file LICENSE.
