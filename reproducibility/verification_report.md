# Verification Report

## Status: PASS

## Script Runs

| Proses | Skrip | Status |
|--------|-------|--------|
| Analisis inferensial | `code/analisis_inferensial/tahap3_analisis_inferensial.py` | ✅ |
| Sintesis hasil | `code/sintesis_hasil/tahap4_sintesis_multidimensi.py` | ✅ |
| Visualisasi | `code/finalisasi/tahap5_visualisasi_bab4.py` | ✅ |

## Output Kanonis

`hasil/analisis_inferensial/` — 5 CSV inferensial:
- `hasil_omnibus_tahap3.csv`
- `hasil_posthoc_tahap3.csv`
- `hasil_konsistensi_finalerror_omnibus.csv`
- `hasil_proporsi_within_tolerance_omnibus.csv`
- `hasil_proporsi_within_tolerance_posthoc.csv`

`hasil/sintesis_hasil/` — 4 CSV (2 deskriptif + 2 profil):
- `hasil_settlingtime_deskriptif.csv`
- `hasil_bridging_deskriptif.csv`
- `tahap4_profil_primer.csv`
- `tahap4_profil_tambahan_kondisional.csv`

`hasil/finalisasi/` — 3 PNG, 3 SVG, 1 audit CSV.

## Dataset Hash

`master_dataset_160.csv` SHA-256: `79443B3F08AD6D42AA2FA6AF0A903CDB319D1CA32DE2FD0ACD37BFE76F99F31C`

## Tidak Tersedia

Skrip audit langsung antara 160 log firmware dan dataset kanonis tidak ditemukan.
Tahap audit log–dataset belum dapat direproduksi.
