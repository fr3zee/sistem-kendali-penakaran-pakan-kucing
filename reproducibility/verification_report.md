# Verification Report

## Status: PASS

Verifikasi eksekusi mencakup pembentukan dataset dari log mentah, analisis inferensial,
sintesis hasil, dan visualisasi.

## Tabel Proses

| Proses | Skrip | Tersedia | Eksekusi Terverifikasi |
|--------|-------|----------|------------------------|
| Pembentukan dataset dari log | `code/pembentukan_dataset/generate_master_dataset.py` | ✅ | ✅ |
| Validasi dataset | `code/validasi_dataset/tahap0_validasi_master_dataset.py` | ✅ | output di `hasil/validasi_dataset/` |
| Statistik deskriptif | `code/sintesis_hasil/tahap1_statistik_deskriptif.py` | ✅ | output di `hasil/sintesis_hasil/` |
| Pemeriksaan asumsi | `code/pemeriksaan_asumsi/tahap2_rekonstruksi_dan_verifikasi.py` | ✅ | output di `hasil/pemeriksaan_asumsi/` |
| Analisis inferensial | `code/analisis_inferensial/tahap3_analisis_inferensial.py` | ✅ | ✅ |
| Sintesis hasil | `code/sintesis_hasil/tahap4_sintesis_multidimensi.py` | ✅ | ✅ |
| Finalisasi Bab IV | `code/finalisasi/tahap5_visualisasi_bab4.py` | ✅ | ✅ |

## Hasil Pembentukan Dataset

```
Log ditemukan              : 160
Log berhasil diparse       : 160
Baris dataset diregenerasi : 160
Identitas duplikat         : 0
Mismatch vs kanonis        : 0
Not verifiable             : 0
Hash regenerated           : 79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C
Hash canonical             : 79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C
Status                     : PASS
```

Parser membaca langsung dari `data/pengujian_final/log_160_trial/` dan tidak
menggunakan nilai dataset kanonis untuk mengisi field yang gagal diparse.
Dataset kanonis hanya dibaca setelah regenerasi selesai, untuk keperluan audit.

## Output Kanonis

`hasil/pembentukan_dataset/` — 3 file:
- `master_dataset_160_regenerated.csv`
- `audit_regenerated_vs_canonical.csv`
- `ringkasan_pembentukan_dataset.md`

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

## Dataset Hash

`master_dataset_160.csv` SHA-256: `79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C`

## Tidak Direproduksi dalam Sesi Ini

- Pipeline pilot early stop (raw log kandidat tidak disertakan dalam repositori publik)
