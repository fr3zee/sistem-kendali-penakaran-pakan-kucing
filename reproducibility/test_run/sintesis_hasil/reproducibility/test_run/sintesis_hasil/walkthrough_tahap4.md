# Walkthrough Tahap 4 — Sintesis Multidimensi

## Status Verifikasi

- `python -m py_compile` / kompilasi skrip: **PASS**.
- Skema dan jumlah baris empat CSV (16 / 16 / 24 / 16): **PASS**.
- Perhitungan primer, rank, Pareto, dan matriks: **PASS**.
- Keterlacakan p-value berdasarkan key baris: **PASS**.
- Pemeriksaan isi DOCX 16 bagian dan tabel fungsional melalui `python-docx`: **PASS**.
- Struktur workbook 15 sheet: **PASS**.
- Seluruh keluaran berukuran nonnol: **PASS**.
- Tidak ada grafik Tahap 4: **PASS**.
- Determinisme semantik dua eksekusi: **PENDING_TWO_RUN_CHECK**.
- File Tahap 3 tidak berubah: **PASS**.

## Struktur Dominasi

- 6 pasangan unik per setpoint.
- 24 pasangan unik untuk seluruh empat setpoint.

## Anotasi Inferensial Tambahan

- RiseTime SP15–SP20: Kruskal–Wallis.
- RiseTime SP25–SP30: Welch ANOVA.
- WithinTolerance: uji Monte Carlo exact pendekatan Fisher–Freeman–Halton dari Tahap 3.

## Audit SHA-256 Input Tahap 3

| File | SHA-256 sebelum | SHA-256 sesudah | Match | Integrity status |
|---|---|---|---|---|
| hasil_omnibus_tahap3.csv | `a4aecde8715a8252ff32133d1c7a06cbdb07028caaa729ce2e5e6fcc0c348337` | `a4aecde8715a8252ff32133d1c7a06cbdb07028caaa729ce2e5e6fcc0c348337` | TRUE | UNCHANGED |
| hasil_posthoc_tahap3.csv | `4ae0f25259791691648e1e62aa0d9c730f4f041e7d5795da5b8c6b511e889aa1` | `4ae0f25259791691648e1e62aa0d9c730f4f041e7d5795da5b8c6b511e889aa1` | TRUE | UNCHANGED |
| hasil_konsistensi_finalerror_omnibus.csv | `519fdf15563fce74d6522caf4a674232fa437928b507859e9ffe2f3e42868250` | `519fdf15563fce74d6522caf4a674232fa437928b507859e9ffe2f3e42868250` | TRUE | UNCHANGED |
| hasil_proporsi_within_tolerance_omnibus.csv | `c4669ac8b6ebd7a8a98e8176460bf97ce2b2a59786bb23064ad5348b51390e55` | `c4669ac8b6ebd7a8a98e8176460bf97ce2b2a59786bb23064ad5348b51390e55` | TRUE | UNCHANGED |
| hasil_proporsi_within_tolerance_posthoc.csv | `2c61d863015a09580492abde5d6a4250f127466dda2d9ed246a9a0029a5aaf23` | `2c61d863015a09580492abde5d6a4250f127466dda2d9ed246a9a0029a5aaf23` | TRUE | UNCHANGED |
| hasil_bridging_deskriptif.csv | `994044b07ca450ed05b176fbaed580073b80826632c1fc6c0be9a59151304ff1` | `994044b07ca450ed05b176fbaed580073b80826632c1fc6c0be9a59151304ff1` | TRUE | UNCHANGED |

Hash cocok menunjukkan file tidak berubah selama pipeline; bukan bukti permission filesystem read-only.

## Keluaran Resmi

| File | Ukuran (byte) |
|---|---:|
| tahap4_profil_primer.csv | 6511 |
| tahap4_pareto_per_setpoint.csv | 5795 |
| tahap4_matriks_dominasi.csv | 6707 |
| tahap4_profil_tambahan_kondisional.csv | 7172 |
| hasil_lengkap_tahap4.xlsx | 42600 |
| laporan_tahap4_sintesis_multidimensi.docx | 47584 |

Workbook berisi 15 sheet. Tidak ada grafik Tahap 4.

## Audit Fixed PID Versus GS PID

- **SP15:** GS PID dominates Fixed PID. GS PID lebih rendah pada MAE%, mean overshoot, durasi, SD FinalError_g.
- **SP20:** GS PID dominates Fixed PID. GS PID lebih rendah pada MAE%, mean overshoot, durasi, SD FinalError_g.
- **SP25:** GS PID dominates Fixed PID. GS PID lebih rendah pada MAE%, mean overshoot, durasi, SD FinalError_g.
- **SP30:** GS PID dominates Fixed PID. GS PID lebih rendah pada MAE%, mean overshoot, durasi, SD FinalError_g.

## Batas Interpretasi

Ranking dan Pareto merupakan sintesis deskriptif. Analisis tidak menetapkan juara umum. Hasil tidak signifikan tidak ditafsirkan sebagai kesamaan. SettlingTime_s tetap kondisional dan BridgingCount tetap pendukung deskriptif.
