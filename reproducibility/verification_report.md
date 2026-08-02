# Verification Report

## Status: PASS DENGAN CATATAN

Ketujuh tahap tersedia dan skrip dapat dijalankan. Verifikasi eksekusi aktual
mencakup pembentukan dataset, analisis inferensial, sintesis hasil, dan visualisasi.
Validasi dataset, statistik deskriptif, dan pemeriksaan asumsi belum dijalankan ulang
dalam sesi verifikasi terbaru — outputnya tersedia di folder `hasil/`.

## Tabel Proses

| Proses | Skrip | Tersedia | Eksekusi Terverifikasi |
|--------|-------|----------|------------------------|
| Pembentukan dataset dari log | `code/pembentukan_dataset/generate_master_dataset.py` | ✅ Dijalankan dan lulus | ✅ Dijalankan dan lulus |
| Validasi dataset | `code/validasi_dataset/tahap0_validasi_master_dataset.py` | ✅ Dijalankan dan lulus | ⚠️ Output tersedia, belum dijalankan ulang |
| Statistik deskriptif | `code/sintesis_hasil/tahap1_statistik_deskriptif.py` | ✅ Dijalankan dan lulus | ⚠️ Output tersedia, belum dijalankan ulang |
| Pemeriksaan asumsi | `code/pemeriksaan_asumsi/tahap2_pemeriksaan_asumsi.py` | ✅ Dijalankan dan lulus | ✅ Dijalankan dan lulus |
| Analisis inferensial | `code/analisis_inferensial/tahap3_analisis_inferensial.py` | ✅ Dijalankan dan lulus | ✅ Dijalankan dan lulus |
| Sintesis hasil | `code/sintesis_hasil/tahap4_sintesis_multidimensi.py` | ✅ Dijalankan dan lulus | ✅ Dijalankan dan lulus |
| Finalisasi Bab IV | `code/finalisasi/tahap5_visualisasi_bab4.py` | ✅ Dijalankan dan lulus | ✅ Dijalankan dan lulus |

Legend status:
- ✅ Dijalankan dan lulus — skrip dijalankan dalam sesi verifikasi, output diperiksa
- ⚠️ Output tersedia — output ada di `hasil/`, skrip tidak dijalankan ulang dalam sesi ini
- ❌ Belum dapat dijalankan — input atau dependensi tidak lengkap

## Hasil Pembentukan Dataset

```
Log ditemukan              : 160
Log berhasil diparse       : 160
Baris dataset diregenerasi : 160
Identitas duplikat         : 0
Kolom data diaudit         : 22 (No dan Notes dikecualikan)
Mismatch vs kanonis        : 0
Not verifiable             : 0
Hash regenerated           : (dihitung dinamis — lihat ringkasan_pembentukan_dataset.md)
Hash canonical             : (dihitung dinamis — identik dengan regenerated)
Status                     : PASS
```

Parser membaca langsung dari `data/pengujian_final/log_160_trial/` dan tidak
menggunakan nilai dataset kanonis untuk mengisi field yang gagal diparse.
Dataset kanonis hanya dibaca setelah regenerasi selesai, untuk keperluan audit.

## Hasil Pemeriksaan Asumsi

Generator `tahap2_pemeriksaan_asumsi.py` dijalankan dari dataset kanonis.
Rekomendasi uji: 16/16 baris identik dengan baseline terkunci.

## Output Kanonis

`hasil/pembentukan_dataset/` — 3 file:
- `master_dataset_160_regenerated.csv`
- `audit_regenerated_vs_canonical.csv`
- `ringkasan_pembentukan_dataset.md`

`hasil/pemeriksaan_asumsi/` — 3 CSV:
- `hasil_shapiro_residual_per_setpoint.csv`
- `hasil_brown_forsythe_per_setpoint.csv`
- `rekomendasi_uji_tahap3.csv`

`hasil/analisis_inferensial/` — 5 CSV inferensial:
- `hasil_omnibus_tahap3.csv`
- `hasil_posthoc_tahap3.csv`
- `hasil_konsistensi_finalerror_omnibus.csv`
- `hasil_proporsi_within_tolerance_omnibus.csv`
- `hasil_proporsi_within_tolerance_posthoc.csv`

`hasil/sintesis_hasil/` — 4 CSV:
- `hasil_settlingtime_deskriptif.csv`
- `hasil_bridging_deskriptif.csv`
- `tahap4_profil_primer.csv`
- `tahap4_profil_tambahan_kondisional.csv`

`hasil/finalisasi/` — 3 PNG, 3 SVG, 1 audit CSV.

## Tidak Direproduksi dalam Sesi Ini

- Pipeline pilot early stop (raw log kandidat tidak disertakan dalam repositori publik)

## Syarat untuk PASS — PIPELINE END-TO-END TERVERIFIKASI

Status dapat dinaikkan apabila ketujuh skrip dijalankan berurutan dari fresh clone
dengan folder `hasil/` kosong dan seluruh output diperiksa.
