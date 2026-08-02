# Perancangan dan Implementasi Kontrol PID dengan Gain Scheduling Berbasis Aturan pada Sistem Penakaran Pakan Kucing Otomatis

**Penulis:** Naufal Hilmi Fathul Ihsan
**Program Studi:** Teknik Komputer, UNNES
**Status:** PASS

---

## Status Pipeline

| Proses | Skrip | Status |
|--------|-------|--------|
| Pembentukan dataset dari log | generate_master_dataset.py | ✅ |
| Validasi dataset | tahap0_validasi_master_dataset.py | ✅ |
| Statistik deskriptif | tahap1_statistik_deskriptif.py | ✅ |
| Pemeriksaan asumsi | tahap2_rekonstruksi_dan_verifikasi.py | ✅ (prasyarat: lihat bawah) |
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

# Pemeriksaan asumsi butuh baseline CSV — lihat code/pemeriksaan_asumsi/README.md
python code/pemeriksaan_asumsi/tahap2_rekonstruksi_dan_verifikasi.py

python code/analisis_inferensial/tahap3_analisis_inferensial.py

python code/sintesis_hasil/tahap4_sintesis_multidimensi.py

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

- Pembentukan dataset dari 160 log, analisis inferensial, sintesis hasil,
  dan visualisasi telah dijalankan dan diverifikasi.
- Dataset hasil regenerasi identik dengan dataset kanonis dengan SHA-256:
  `79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C`.
- Rincian proses yang tersedia dan yang telah diverifikasi terdapat pada
  `reproducibility/verification_report.md`.

---

## Lisensi

Hak cipta 2026 Naufal Hilmi. Dibuat untuk tugas akhir (skripsi) di Universitas Negeri Semarang (UNNES). Penggunaan ulang untuk keperluan akademik diperbolehkan dengan atribusi yang sesuai.
