# Perancangan dan Implementasi Kontrol PID dengan Gain Scheduling Berbasis Aturan pada Sistem Pakan Kucing Otomatis Terintegrasi IoT

**Penulis:** Naufal Hilmi  
**Program Studi:** Teknik Komputer, UNNES  
**Repository Version:** v1.0  
**Release Date:** 2026-07-27  
**Status:** Final

---

## Status Pipeline

| Tahap | Deskripsi | Status |
|---|---|---|
| Tahap 1 | Integrasi, Validasi, dan Pembentukan Master Dataset | ✅ |
| Tahap 2 | Uji Asumsi Statistik + Verifikasi Reproduksibilitas | ✅ |
| Tahap 3 | Analisis Inferensial | ✅ |
| Tahap 4 | Sintesis Multidimensi & Pareto | ✅ |
| Tahap 5 | Generator Bab IV DOCX | ✅ |
| Audit DOCX | 17/17 check PASS | ✅ |
| Repositori | https://github.com/fr3zee/sistem-kendali-penakaran-pakan-kucing | ✅ |

---

## 1. Tujuan Repositori

Repositori ini memuat seluruh artefak penelitian skripsi: firmware ESP32, dataset hasil pengujian, script analisis Python, dan output Bab IV. Disusun untuk mendukung keterlacakan data dan kemudahan reproduksi penelitian (*reproducibility*).

---

## 2. Diagram Pipeline

```
Raw Logs (160 file .txt)
          │
          ▼
       Tahap 1
  (Integrasi & Validasi)
          │
          ▼
  master_dataset_160.csv
          │
          ▼
       Tahap 2
  (Uji Asumsi Statistik)
          │
          ▼
       Tahap 3
  (Analisis Inferensial)
          │
          ▼
       Tahap 4
  (Sintesis & Pareto)
          │
          ▼
       Tahap 5
  (Generator DOCX)
          │
          ▼
  bab4_hasil_dan_pembahasan_revisi_terbatas.docx
```

---

## 3. Struktur Folder

```
.
├── 4. Arduino/                     # Firmware ESP32 (Fixed PID & GS PID)
├── 3. dok trial hasil/
│   └── Pengambilan Data/
│       ├── Fixed PID/SP_XX/        # 40 log trial Fixed PID (.txt)
│       ├── GS PID/SP_XX/           # 40 log trial GS PID (.txt)
│       ├── Manual Cepat/SP_XX/     # 40 log trial Manual Cepat (.txt)
│       ├── Manual Presisi/SP_XX/   # 40 log trial Manual Presisi (.txt)
│       └── rekap data/
│           ├── master_dataset_160.csv
│           └── Laporan/
│               ├── Tahap2/
│               ├── Tahap3/
│               ├── Tahap4/
│               └── Tahap5/
├── README.md
└── requirements.txt
```

---

## 4. Environment

| Komponen | Versi |
|---|---|
| Python | 3.12.7 (Anaconda) |
| OS | Windows 11 |
| scipy | 1.13.1 |
| pandas | 2.2.2 |
| numpy | 1.26.4 |
| statsmodels | 0.14.2 |

---

## 5. Dependensi

```
pip install -r requirements.txt
```

Lihat `requirements.txt` untuk daftar lengkap versi yang di-pin.

> `pywin32` hanya dibutuhkan Tahap 5 (Windows only — ekspor DOCX ke PDF via `win32com.client`).

---

## 6. Pipeline Analisis

### Tahap 1 — Integrasi, Validasi, dan Pembentukan Master Dataset
- **Input:** 160 log trial raw (.txt)
- **Output:** `master_dataset_160.csv`
- **Kriteria:** `Valid=TRUE`, `StopReason=TARGET`, 160 baris, desain seimbang 4×4×10

### Tahap 2 — Uji Asumsi Statistik
- **Script:** `Tahap2/tahap2_rekonstruksi_dan_verifikasi.py`
- **Input:** `master_dataset_160.csv`
- **Output:** Shapiro-Wilk, Brown-Forsythe, rekomendasi uji per setpoint
- **Catatan:** Script ini adalah tool verifikasi reproduksibilitas terhadap artefak baseline dan tidak menggantikan hasil penelitian yang digunakan pada Tahap 3.
- **Bukti:** `reproduksi_verifikasi/audit.json` → `OVERALL=PASS`, `mismatch_count=0`

### Tahap 3 — Analisis Inferensial
- **Script:** `Tahap3/tahap3_analisis_inferensial.py`
- **Input:** `master_dataset_160.csv` + `rekomendasi_uji_tahap3.csv`
- **Output:** Omnibus (Welch ANOVA / Kruskal-Wallis / Brown-Forsythe / FFH Exact), post-hoc (Games-Howell / Dunn-Holm), ukuran efek

### Tahap 4 — Sintesis Multidimensi & Pareto
- **Script:** `Tahap4/tahap4_sintesis_multidimensi.py`
- **Input:** Output Tahap 3 (6 CSV)
- **Output:** Profil primer, profil tambahan, matriks dominasi, status Pareto per setpoint

### Tahap 5 — Generator Bab IV
- **Script:** `Tahap5/tahap5_generate_docx_bab4_revisi_terbatas.py`
- **Input:** Output Tahap 3–4 + `narasi_bab4.md` + grafik
- **Output:** `bab4_hasil_dan_pembahasan_revisi_terbatas.docx`
- **Audit:** `audit_docx_bab4_revisi_terbatas.json` → 17/17 check PASS

---

## 7. Cara Reproduksi

```bash
# 1. Clone repository
git clone <url-repository>
cd <nama-folder>

# 2. Install dependensi
pip install -r requirements.txt

# 3. Masuk ke folder pipeline
cd "3. dok trial hasil/Pengambilan Data/rekap data/Laporan"

# 4. Jalankan pipeline
python Tahap2/tahap2_rekonstruksi_dan_verifikasi.py
python Tahap3/tahap3_analisis_inferensial.py
python Tahap4/tahap4_sintesis_multidimensi.py
python Tahap5/tahap5_generate_docx_bab4_revisi_terbatas.py
```

Tahap 2 hanya menjalankan verifikasi reproduksibilitas. Baseline tidak diubah.

---

## 8. Peta Bab IV ke Artefak

| Subbab Bab IV | Artefak Sumber |
|---|---|
| Desain Eksperimen | `master_dataset_160.csv` |
| Profil Outcome Primer | `tahap4_profil_primer.csv` |
| Outcome Tambahan & Kondisional | `tahap4_profil_tambahan_kondisional.csv` |
| Uji Omnibus | `hasil_omnibus_tahap3.csv` |
| Uji Post-hoc | `hasil_posthoc_tahap3.csv` |
| Konsistensi FinalError | `hasil_konsistensi_finalerror_omnibus.csv` |
| Within Tolerance | `hasil_proporsi_within_tolerance_omnibus.csv` |
| Fixed PID vs GS PID (Pareto) | `tahap4_pareto_per_setpoint.csv` + `tahap4_matriks_dominasi.csv` |
| Diagnostik Zona GS PID | `extract_zone_stats.py` (Tahap3) |
| Kurva Respons | `tahap5_generate_gambar_4_5.py` |
| Keterlacakan angka kunci | `registry_numerik_tahap5.csv` |

> `registry_numerik_tahap5.csv` memetakan nilai numerik kunci narasi Bab IV ke file sumber, kunci baris, dan kolom. Saat ini mencakup nilai-nilai terpilih, bukan seluruh angka Bab IV.

---

## 9. Artefak Reproduksibilitas

| Artefak | Lokasi | Fungsi |
|---|---|---|
| `audit.json` | `Tahap2/reproduksi_verifikasi/` | Bukti OVERALL=PASS verifikasi Tahap 2 |
| `manifest.csv` | `Tahap2/reproduksi_verifikasi/` | Manifest file + hash SHA-256 input Tahap 2 |
| `registry_numerik_tahap5.csv` | `Tahap5/` | Peta angka kunci Bab IV ke sumber |
| `audit_docx_bab4_revisi_terbatas.json` | `Tahap5/` | Audit DOCX Bab IV (17/17 check PASS) |
| `walkthrough_verifikasi_revisi_terbatas.md` | `Tahap5/` | Dokumentasi proses verifikasi pipeline |

---

## 10. Catatan Keamanan

Repositori ini tidak memuat:
- SSID / password Wi-Fi
- Token MQTT
- API key
- Kredensial database
- File konfigurasi yang mengandung nilai rahasia

Bila firmware membutuhkan konfigurasi jaringan, gunakan file `.env.example` tanpa nilai rahasia.

---

## 11. Lisensi

Hak cipta 2026 Naufal Hilmi. Seluruh artefak penelitian ini dibuat untuk keperluan tugas akhir (skripsi) di Universitas Negeri Semarang (UNNES). Kecuali dinyatakan lain, kode dan artefak penelitian ini hanya digunakan untuk kepentingan akademik dan penelitian. Penggunaan ulang untuk keperluan akademik diperbolehkan dengan atribusi yang sesuai.
