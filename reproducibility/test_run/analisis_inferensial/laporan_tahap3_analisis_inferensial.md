# Laporan Tahap 3 — Analisis Inferensial Final

Tanggal: 2026-08-02T03:40:47.474624

## Informasi Lingkungan dan Konfigurasi

- **Python**: 3.12.7 | packaged by Anaconda, Inc. | (main, Oct  4 2024, 13:17:27) [MSC v.1929 64 bit (AMD64)]
- **pandas**: 2.2.2
- **numpy**: 1.26.4
- **scipy**: 1.13.1
- **statsmodels**: 0.14.2
- **pingouin**: 0.6.1
- **scikit_posthocs**: 0.14.0
- **openpyxl**: 3.1.5
- **python-docx**: 1.2.0
- **OS**: Windows-11-10.0.26200-SP0
- **Timestamp**: 2026-08-02T03:40:47.474624
- **Seed**: 42
- **N_Bootstrap**: 10000

- **α**: 0.05
- **seed**: 42
- **n\_monte\_carlo**: 100.000
- **n\_bootstrap**: 10.000

## Dasar Pemilihan Uji Omnibus

Normalitas dinilai dari residual gabungan setiap kombinasi metrik–setpoint (`hasil_shapiro_residual_per_setpoint.csv`). Homogenitas varians menggunakan uji Brown–Forsythe (Levene berbasis median) (`hasil_brown_forsythe_per_setpoint.csv`). Keputusan uji dikunci pada `rekomendasi_uji_tahap3.csv` sebelum analisis omnibus.

| Metrik | SP | p SW residual | Normalitas | p BF | Homogenitas | Uji final | Alasan |
|---|---:|---:|---|---:|---|---|---|
| AbsError_pct | 15 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,001 | Varians tidak homogen | Kruskal-Wallis | Residual tidak normal dan varians tidak homogen |
| AbsError_pct | 20 | 0,006 | Terdapat bukti penyimpangan dari distribusi normal | 0,103 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Residual tidak normal dengan skewness sedang-berat |
| AbsError_pct | 25 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,203 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Distribusi sangat menceng dan residual tidak normal |
| AbsError_pct | 30 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,543 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Distribusi sangat menceng dan residual tidak normal |
| MaxOvershoot_pct | 15 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,003 | Varians tidak homogen | Kruskal-Wallis | Residual tidak normal dan varians tidak homogen |
| MaxOvershoot_pct | 20 | 0,007 | Terdapat bukti penyimpangan dari distribusi normal | 0,190 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Residual tidak normal, terdapat proporsi nilai nol yang cukup tinggi, dan distribusi beberapa kelompok menceng |
| MaxOvershoot_pct | 25 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,267 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Residual tidak normal dengan skewness sedang-berat |
| MaxOvershoot_pct | 30 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,568 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Distribusi sangat menceng dan residual tidak normal |
| Duration_s | 15 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,060 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Residual tidak normal (SW p<0.001); skewness GS PID 2.16 pada n=10 tidak memenuhi syarat robustness ANOVA |
| Duration_s | 20 | <0,001 | Terdapat bukti penyimpangan dari distribusi normal | 0,205 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Residual tidak normal dengan skewness sedang-berat |
| Duration_s | 25 | 0,389 | Tidak terdapat bukti signifikan untuk menolak asumsi normalitas | 0,006 | Varians tidak homogen | Welch ANOVA | Residual cukup layak tetapi varians tidak homogen |
| Duration_s | 30 | 0,028 | Terdapat bukti penyimpangan dari distribusi normal | 0,131 | Tidak terdapat bukti signifikan perbedaan varians | Kruskal-Wallis | Residual tidak normal (SW p=0.028); skewness GS PID 2.48 pada n=10 tidak memenuhi syarat robustness ANOVA |
| RiseTime_10_90_s | 15 | 0,003 | Terdapat bukti penyimpangan dari distribusi normal | 0,037 | Varians tidak homogen | Kruskal-Wallis | Residual tidak normal dan varians tidak homogen |
| RiseTime_10_90_s | 20 | 0,009 | Terdapat bukti penyimpangan dari distribusi normal | 0,003 | Varians tidak homogen | Kruskal-Wallis | Residual tidak normal dan varians tidak homogen |
| RiseTime_10_90_s | 25 | 0,593 | Tidak terdapat bukti signifikan untuk menolak asumsi normalitas | 0,005 | Varians tidak homogen | Welch ANOVA | Residual cukup layak tetapi varians tidak homogen |
| RiseTime_10_90_s | 30 | 0,128 | Tidak terdapat bukti signifikan untuk menolak asumsi normalitas | 0,017 | Varians tidak homogen | Welch ANOVA | Residual cukup layak tetapi varians tidak homogen |

> **Catatan RiseTime\_10\_90\_s SP30**: Normalitas pemilihan uji dinilai dari residual gabungan. Residual SP30 memenuhi asumsi normalitas (SW p=0,1283), sedangkan homogenitas varians tidak terpenuhi. Oleh karena itu, digunakan Welch ANOVA.

## Uji Omnibus Metrik Kontinu

| Metrik | SP | Uji | Statistik | df1 | df2 | p mentah | p Holm | Keputusan | Ukuran Efek | Nilai |
|---|---:|---|---:|---:|---:|---:|---:|---|---|---:|
| AbsError_pct | 15 | Kruskal-Wallis | 10,8174 | 3 | — | 0,013 | 0,038 | Signifikan | rank_epsilon_squared | 0,2774 |
| AbsError_pct | 20 | Kruskal-Wallis | 3,6497 | 3 | — | 0,302 | 0,454 | Belum signifikan | rank_epsilon_squared | 0,0936 |
| AbsError_pct | 25 | Kruskal-Wallis | 4,3390 | 3 | — | 0,227 | 0,454 | Belum signifikan | rank_epsilon_squared | 0,1113 |
| AbsError_pct | 30 | Kruskal-Wallis | 12,0893 | 3 | — | 0,007 | 0,028 | Signifikan | rank_epsilon_squared | 0,3100 |
| MaxOvershoot_pct | 15 | Kruskal-Wallis | 11,9262 | 3 | — | 0,008 | 0,023 | Signifikan | rank_epsilon_squared | 0,3058 |
| MaxOvershoot_pct | 20 | Kruskal-Wallis | 4,0786 | 3 | — | 0,253 | 0,253 | Belum signifikan | rank_epsilon_squared | 0,1046 |
| MaxOvershoot_pct | 25 | Kruskal-Wallis | 5,9996 | 3 | — | 0,112 | 0,223 | Belum signifikan | rank_epsilon_squared | 0,1538 |
| MaxOvershoot_pct | 30 | Kruskal-Wallis | 18,4112 | 3 | — | <0,001 | 0,001 | Signifikan | rank_epsilon_squared | 0,4721 |
| Duration_s | 15 | Kruskal-Wallis | 22,7258 | 3 | — | <0,001 | <0,001 | Signifikan | rank_epsilon_squared | 0,5827 |
| Duration_s | 20 | Kruskal-Wallis | 29,2829 | 3 | — | <0,001 | <0,001 | Signifikan | rank_epsilon_squared | 0,7508 |
| Duration_s | 25 | Welch ANOVA | 31,9113 | 3 | 15,87 | <0,001 | <0,001 | Signifikan | eta_p2 | 0,5974 |
| Duration_s | 30 | Kruskal-Wallis | 25,2797 | 3 | — | <0,001 | <0,001 | Signifikan | rank_epsilon_squared | 0,6482 |
| RiseTime_10_90_s | 15 | Kruskal-Wallis | 15,0556 | 3 | — | 0,002 | 0,002 | Signifikan | rank_epsilon_squared | 0,3860 |
| RiseTime_10_90_s | 20 | Kruskal-Wallis | 22,8406 | 3 | — | <0,001 | <0,001 | Signifikan | rank_epsilon_squared | 0,5857 |
| RiseTime_10_90_s | 25 | Welch ANOVA | 27,1682 | 3 | 17,27 | <0,001 | <0,001 | Signifikan | eta_p2 | 0,6426 |
| RiseTime_10_90_s | 30 | Welch ANOVA | 10,2884 | 3 | 19,30 | <0,001 | <0,001 | Signifikan | eta_p2 | 0,6591 |

## Post-hoc

Cliff’s δ untuk pasangan Kruskal–Wallis (Dunn–Holm); Hedges’ g untuk pasangan Welch (Games–Howell). Kolom Arah menunjukkan tanda ukuran efek secara deskriptif dan tidak menggantikan keputusan berdasarkan nilai probabilitas tersesuaikan.

| Metrik | SP | Uji | A | B | p adj | Keputusan | Efek | Nilai | CI lo | CI hi | Arah |
|---|---:|---|---|---|---:|---|---|---:|---:|---:|---|
| AbsError_pct | 15 | Dunn-Holm | Manual Cepat | Manual Presisi | 0,659 | Belum signifikan | Cliff’s δ | 0,3000 | -0.24 | 0.8 | Manual Cepat > Manual Presisi |
| AbsError_pct | 15 | Dunn-Holm | Manual Cepat | Fixed PID | 0,301 | Belum signifikan | Cliff’s δ | 0,4800 | -0.02 | 0.88 | Manual Cepat > Fixed PID |
| AbsError_pct | 15 | Dunn-Holm | Manual Cepat | GS PID | 0,011 | Signifikan | Cliff’s δ | 0,7100 | 0.31 | 1.0 | Manual Cepat > GS PID |
| AbsError_pct | 15 | Dunn-Holm | Manual Presisi | Fixed PID | 0,659 | Belum signifikan | Cliff’s δ | 0,2500 | -0.28 | 0.71 | Manual Presisi > Fixed PID |
| AbsError_pct | 15 | Dunn-Holm | Manual Presisi | GS PID | 0,103 | Belum signifikan | Cliff’s δ | 0,7000 | 0.28 | 1.0 | Manual Presisi > GS PID |
| AbsError_pct | 15 | Dunn-Holm | Fixed PID | GS PID | 0,542 | Belum signifikan | Cliff’s δ | 0,3600 | -0.1605 | 0.8 | Fixed PID > GS PID |
| AbsError_pct | 30 | Dunn-Holm | Manual Cepat | Manual Presisi | 0,377 | Belum signifikan | Cliff’s δ | 0,4000 | -0.12 | 0.84 | Manual Cepat > Manual Presisi |
| AbsError_pct | 30 | Dunn-Holm | Manual Cepat | Fixed PID | 0,018 | Signifikan | Cliff’s δ | 0,7800 | 0.44 | 1.0 | Manual Cepat > Fixed PID |
| AbsError_pct | 30 | Dunn-Holm | Manual Cepat | GS PID | 0,013 | Signifikan | Cliff’s δ | 0,8200 | 0.52 | 1.0 | Manual Cepat > GS PID |
| AbsError_pct | 30 | Dunn-Holm | Manual Presisi | Fixed PID | 0,488 | Belum signifikan | Cliff’s δ | 0,3000 | -0.24 | 0.78 | Manual Presisi > Fixed PID |
| AbsError_pct | 30 | Dunn-Holm | Manual Presisi | GS PID | 0,488 | Belum signifikan | Cliff’s δ | 0,3500 | -0.2 | 0.84 | Manual Presisi > GS PID |
| AbsError_pct | 30 | Dunn-Holm | Fixed PID | GS PID | 0,871 | Belum signifikan | Cliff’s δ | 0,0400 | -0.48 | 0.56 | GS PID >= Fixed PID |
| MaxOvershoot_pct | 15 | Dunn-Holm | Manual Cepat | Manual Presisi | 0,307 | Belum signifikan | Cliff’s δ | 0,4800 | -0.02 | 0.86 | Manual Cepat > Manual Presisi |
| MaxOvershoot_pct | 15 | Dunn-Holm | Manual Cepat | Fixed PID | 0,037 | Signifikan | Cliff’s δ | 0,6400 | 0.2 | 0.94 | Manual Cepat > Fixed PID |
| MaxOvershoot_pct | 15 | Dunn-Holm | Manual Cepat | GS PID | 0,008 | Signifikan | Cliff’s δ | 0,8400 | 0.52 | 1.0 | Manual Cepat > GS PID |
| MaxOvershoot_pct | 15 | Dunn-Holm | Manual Presisi | Fixed PID | 0,727 | Belum signifikan | Cliff’s δ | 0,2000 | -0.3002 | 0.66 | Manual Presisi > Fixed PID |
| MaxOvershoot_pct | 15 | Dunn-Holm | Manual Presisi | GS PID | 0,444 | Belum signifikan | Cliff’s δ | 0,4300 | -0.05 | 0.85 | Manual Presisi > GS PID |
| MaxOvershoot_pct | 15 | Dunn-Holm | Fixed PID | GS PID | 0,727 | Belum signifikan | Cliff’s δ | 0,0600 | -0.44 | 0.54 | GS PID >= Fixed PID |
| MaxOvershoot_pct | 30 | Dunn-Holm | Manual Cepat | Manual Presisi | 0,327 | Belum signifikan | Cliff’s δ | 0,4200 | -0.1 | 0.84 | Manual Cepat > Manual Presisi |
| MaxOvershoot_pct | 30 | Dunn-Holm | Manual Cepat | Fixed PID | 0,009 | Signifikan | Cliff’s δ | 0,8800 | 0.6 | 1.0 | Manual Cepat > Fixed PID |
| MaxOvershoot_pct | 30 | Dunn-Holm | Manual Cepat | GS PID | <0,001 | Signifikan | Cliff’s δ | 0,9000 | 0.68 | 1.0 | Manual Cepat > GS PID |
| MaxOvershoot_pct | 30 | Dunn-Holm | Manual Presisi | Fixed PID | 0,327 | Belum signifikan | Cliff’s δ | 0,4200 | -0.08 | 0.84 | Manual Presisi > Fixed PID |
| MaxOvershoot_pct | 30 | Dunn-Holm | Manual Presisi | GS PID | 0,061 | Belum signifikan | Cliff’s δ | 0,6400 | 0.25 | 0.94 | Manual Presisi > GS PID |
| MaxOvershoot_pct | 30 | Dunn-Holm | Fixed PID | GS PID | 0,412 | Belum signifikan | Cliff’s δ | 0,3000 | -0.16 | 0.71 | Fixed PID > GS PID |
| Duration_s | 15 | Dunn-Holm | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Cliff’s δ | -0,9200 | -1.0 | -0.72 | Manual Presisi >= Manual Cepat |
| Duration_s | 15 | Dunn-Holm | Manual Cepat | Fixed PID | 0,003 | Signifikan | Cliff’s δ | -0,9000 | -1.0 | -0.64 | Fixed PID >= Manual Cepat |
| Duration_s | 15 | Dunn-Holm | Manual Cepat | GS PID | 0,149 | Belum signifikan | Cliff’s δ | -0,7600 | -1.0 | -0.36 | GS PID >= Manual Cepat |
| Duration_s | 15 | Dunn-Holm | Manual Presisi | Fixed PID | 0,292 | Belum signifikan | Cliff’s δ | 0,5400 | 0.04 | 0.96 | Manual Presisi > Fixed PID |
| Duration_s | 15 | Dunn-Holm | Manual Presisi | GS PID | 0,045 | Signifikan | Cliff’s δ | 0,6600 | 0.2 | 1.0 | Manual Presisi > GS PID |
| Duration_s | 15 | Dunn-Holm | Fixed PID | GS PID | 0,292 | Belum signifikan | Cliff’s δ | 0,6300 | 0.16 | 1.0 | Fixed PID > GS PID |
| Duration_s | 20 | Dunn-Holm | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Cliff’s δ | -1,0000 | -1.0 | -1.0 | Manual Presisi >= Manual Cepat |
| Duration_s | 20 | Dunn-Holm | Manual Cepat | Fixed PID | 0,001 | Signifikan | Cliff’s δ | -0,9800 | -1.0 | -0.88 | Fixed PID >= Manual Cepat |
| Duration_s | 20 | Dunn-Holm | Manual Cepat | GS PID | 0,178 | Belum signifikan | Cliff’s δ | -0,8000 | -1.0 | -0.48 | GS PID >= Manual Cepat |
| Duration_s | 20 | Dunn-Holm | Manual Presisi | Fixed PID | 0,178 | Belum signifikan | Cliff’s δ | 0,6400 | 0.18 | 1.0 | Manual Presisi > Fixed PID |
| Duration_s | 20 | Dunn-Holm | Manual Presisi | GS PID | 0,005 | Signifikan | Cliff’s δ | 0,9200 | 0.7 | 1.0 | Manual Presisi > GS PID |
| Duration_s | 20 | Dunn-Holm | Fixed PID | GS PID | 0,178 | Belum signifikan | Cliff’s δ | 0,6900 | 0.27 | 0.98 | Fixed PID > GS PID |
| Duration_s | 25 | Games-Howell | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Hedges’ g | -2,7071 | -3.9204 | -1.4938 | Manual Presisi >= Manual Cepat |
| Duration_s | 25 | Games-Howell | Manual Cepat | Fixed PID | <0,001 | Signifikan | Hedges’ g | -3,2633 | -4.6016 | -1.925 | Fixed PID >= Manual Cepat |
| Duration_s | 25 | Games-Howell | Manual Cepat | GS PID | 0,036 | Signifikan | Hedges’ g | -1,4084 | -2.3876 | -0.4292 | GS PID >= Manual Cepat |
| Duration_s | 25 | Games-Howell | Manual Presisi | Fixed PID | 0,899 | Belum signifikan | Hedges’ g | 0,2963 | -0.5851 | 1.1776 | Manual Presisi > Fixed PID |
| Duration_s | 25 | Games-Howell | Manual Presisi | GS PID | 0,016 | Signifikan | Hedges’ g | 1,4817 | 0.4921 | 2.4712 | Manual Presisi > GS PID |
| Duration_s | 25 | Games-Howell | Fixed PID | GS PID | 0,016 | Signifikan | Hedges’ g | 1,4522 | 0.4669 | 2.4375 | Fixed PID > GS PID |
| Duration_s | 30 | Dunn-Holm | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Cliff’s δ | -1,0000 | -1.0 | -1.0 | Manual Presisi >= Manual Cepat |
| Duration_s | 30 | Dunn-Holm | Manual Cepat | Fixed PID | 0,065 | Belum signifikan | Cliff’s δ | -0,7400 | -1.0 | -0.36 | Fixed PID >= Manual Cepat |
| Duration_s | 30 | Dunn-Holm | Manual Cepat | GS PID | 0,200 | Belum signifikan | Cliff’s δ | -0,5800 | -0.92 | -0.12 | GS PID >= Manual Cepat |
| Duration_s | 30 | Dunn-Holm | Manual Presisi | Fixed PID | 0,033 | Signifikan | Cliff’s δ | 0,8400 | 0.46 | 1.0 | Manual Presisi > Fixed PID |
| Duration_s | 30 | Dunn-Holm | Manual Presisi | GS PID | 0,005 | Signifikan | Cliff’s δ | 1,0000 | 1.0 | 1.0 | Manual Presisi > GS PID |
| Duration_s | 30 | Dunn-Holm | Fixed PID | GS PID | 0,515 | Belum signifikan | Cliff’s δ | 0,1800 | -0.38 | 0.66 | Fixed PID > GS PID |
| RiseTime_10_90_s | 15 | Dunn-Holm | Manual Cepat | Manual Presisi | 0,001 | Signifikan | Cliff’s δ | -0,7400 | -1.0 | -0.34 | Manual Presisi >= Manual Cepat |
| RiseTime_10_90_s | 15 | Dunn-Holm | Manual Cepat | Fixed PID | 0,034 | Signifikan | Cliff’s δ | -0,8200 | -1.0 | -0.46 | Fixed PID >= Manual Cepat |
| RiseTime_10_90_s | 15 | Dunn-Holm | Manual Cepat | GS PID | 0,238 | Belum signifikan | Cliff’s δ | -0,6100 | -0.98 | -0.16 | GS PID >= Manual Cepat |
| RiseTime_10_90_s | 15 | Dunn-Holm | Manual Presisi | Fixed PID | 0,603 | Belum signifikan | Cliff’s δ | 0,4800 | -0.06 | 0.94 | Manual Presisi > Fixed PID |
| RiseTime_10_90_s | 15 | Dunn-Holm | Manual Presisi | GS PID | 0,238 | Belum signifikan | Cliff’s δ | 0,5200 | -0.02 | 1.0 | Manual Presisi > GS PID |
| RiseTime_10_90_s | 15 | Dunn-Holm | Fixed PID | GS PID | 0,603 | Belum signifikan | Cliff’s δ | 0,3200 | -0.2 | 0.8 | Fixed PID > GS PID |
| RiseTime_10_90_s | 20 | Dunn-Holm | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Cliff’s δ | -0,9600 | -1.0 | -0.82 | Manual Presisi >= Manual Cepat |
| RiseTime_10_90_s | 20 | Dunn-Holm | Manual Cepat | Fixed PID | 0,004 | Signifikan | Cliff’s δ | -0,8800 | -1.0 | -0.64 | Fixed PID >= Manual Cepat |
| RiseTime_10_90_s | 20 | Dunn-Holm | Manual Cepat | GS PID | 0,282 | Belum signifikan | Cliff’s δ | -0,5700 | -0.92 | -0.13 | GS PID >= Manual Cepat |
| RiseTime_10_90_s | 20 | Dunn-Holm | Manual Presisi | Fixed PID | 0,320 | Belum signifikan | Cliff’s δ | 0,4000 | -0.12 | 0.84 | Manual Presisi > Fixed PID |
| RiseTime_10_90_s | 20 | Dunn-Holm | Manual Presisi | GS PID | 0,015 | Signifikan | Cliff’s δ | 0,8000 | 0.44 | 1.0 | Manual Presisi > GS PID |
| RiseTime_10_90_s | 20 | Dunn-Holm | Fixed PID | GS PID | 0,171 | Belum signifikan | Cliff’s δ | 0,6400 | 0.2 | 0.94 | Fixed PID > GS PID |
| RiseTime_10_90_s | 25 | Games-Howell | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Hedges’ g | -3,0007 | -4.2786 | -1.7228 | Manual Presisi >= Manual Cepat |
| RiseTime_10_90_s | 25 | Games-Howell | Manual Cepat | Fixed PID | <0,001 | Signifikan | Hedges’ g | -2,6635 | -3.8676 | -1.4595 | Fixed PID >= Manual Cepat |
| RiseTime_10_90_s | 25 | Games-Howell | Manual Cepat | GS PID | 0,035 | Signifikan | Hedges’ g | -1,3426 | -2.3129 | -0.3723 | GS PID >= Manual Cepat |
| RiseTime_10_90_s | 25 | Games-Howell | Manual Presisi | Fixed PID | 0,990 | Belum signifikan | Hedges’ g | 0,1291 | -0.7484 | 1.0065 | Manual Presisi > Fixed PID |
| RiseTime_10_90_s | 25 | Games-Howell | Manual Presisi | GS PID | 0,001 | Signifikan | Hedges’ g | 2,1218 | 1.026 | 3.2176 | Manual Presisi > GS PID |
| RiseTime_10_90_s | 25 | Games-Howell | Fixed PID | GS PID | 0,004 | Signifikan | Hedges’ g | 1,8607 | 0.8115 | 2.9099 | Fixed PID > GS PID |
| RiseTime_10_90_s | 30 | Games-Howell | Manual Cepat | Manual Presisi | <0,001 | Signifikan | Hedges’ g | -2,3148 | -3.4475 | -1.1822 | Manual Presisi >= Manual Cepat |
| RiseTime_10_90_s | 30 | Games-Howell | Manual Cepat | Fixed PID | 0,596 | Belum signifikan | Hedges’ g | -0,5420 | -1.4345 | 0.3505 | Fixed PID >= Manual Cepat |
| RiseTime_10_90_s | 30 | Games-Howell | Manual Cepat | GS PID | 1,000 | Belum signifikan | Hedges’ g | -0,0257 | -0.9022 | 0.8509 | GS PID >= Manual Cepat |
| RiseTime_10_90_s | 30 | Games-Howell | Manual Presisi | Fixed PID | 0,002 | Signifikan | Hedges’ g | 2,1099 | 1.0164 | 3.2035 | Manual Presisi > Fixed PID |
| RiseTime_10_90_s | 30 | Games-Howell | Manual Presisi | GS PID | <0,001 | Signifikan | Hedges’ g | 2,3975 | 1.2484 | 3.5466 | Manual Presisi > GS PID |
| RiseTime_10_90_s | 30 | Games-Howell | Fixed PID | GS PID | 0,484 | Belum signifikan | Hedges’ g | 0,6227 | -0.2748 | 1.5203 | Fixed PID > GS PID |

## Konsistensi FinalError_g

Uji Brown–Forsythe (Levene berbasis median) atas variansi FinalError_g. Rasio varians dan skenario dengan varians terkecil disajikan secara deskriptif. Uji ini bersifat omnibus dan tidak mengidentifikasi pasangan skenario yang memiliki variansi berbeda.

| SP | F | df1 | df2 | p mentah | p Holm | Keputusan | VarRatio | MinVar |
|---:|---:|---:|---:|---:|---:|---|---:|---|
| 15 | 5,5839 | 3 | 36 | 0,003 | 0,012 | Signifikan | 64.043 | GS PID |
| 20 | 0,5487 | 3 | 36 | 0,652 | 0,660 | Belum signifikan | 11.4928 | GS PID |
| 25 | 1,1831 | 3 | 36 | 0,330 | 0,660 | Belum signifikan | 12.4592 | GS PID |
| 30 | 3,1361 | 3 | 36 | 0,037 | 0,112 | Belum signifikan | 26.9597 | GS PID |

> Catatan: Rasio varians dan skenario dengan varians terkecil disajikan secara deskriptif. Uji Brown–Forsythe bersifat omnibus dan tidak mengidentifikasi pasangan skenario yang memiliki variansi berbeda.

## Proporsi WithinTolerance

Uji independensi Pearson chi-square dengan estimasi nilai probabilitas Monte Carlo bersyarat pada margin tetap, menggunakan 100.000 simulasi dan seed 42. Statistik Pearson χ² dan nilai probabilitas asimtotik disajikan sebagai diagnostik; keputusan inferensial berdasarkan p-value Monte Carlo yang telah dikoreksi Holm pada empat setpoint.

### Omnibus

| SP | χ² (diag) | p asim (diag) | p MC | p Holm | Keputusan | V | MinExp | Count ekstrem |
|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 15 | 8,0000 | 0,046 | 0,057 | 0,115 | Belum signifikan | 0,447 | 3.75 | 5729 |
| 20 | 4,8352 | 0,184 | 0,235 | 0,235 | Belum signifikan | 0,348 | 3.5 | 23457 |
| 25 | 11,2821 | 0,010 | 0,010 | 0,030 | Signifikan | 0,531 | 3.25 | 1007 |
| 30 | 14,1935 | 0,003 | 0,002 | 0,009 | Signifikan | 0,596 | 2.25 | 212 |

### Post-hoc Fisher (dua sisi, koreksi Holm dalam 6 pasangan per setpoint)

| SP | A | B | Prop A | Prop B | Selisih | OR | p Holm | Keputusan |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 25 | Manual Cepat | Manual Presisi | 0.3 | 0.6 | -0.3 | 0,2857 | 1,000 | Belum signifikan |
| 25 | Manual Cepat | Fixed PID | 0.3 | 0.9 | -0.6 | 0,0476 | 0,119 | Belum signifikan |
| 25 | Manual Cepat | GS PID | 0.3 | 0.9 | -0.6 | 0,0476 | 0,119 | Belum signifikan |
| 25 | Manual Presisi | Fixed PID | 0.6 | 0.9 | -0.3 | 0,1667 | 1,000 | Belum signifikan |
| 25 | Manual Presisi | GS PID | 0.6 | 0.9 | -0.3 | 0,1667 | 1,000 | Belum signifikan |
| 25 | Fixed PID | GS PID | 0.9 | 0.9 | 0.0 | 1,0000 | 1,000 | Belum signifikan |
| 30 | Manual Cepat | Manual Presisi | 0.4 | 0.7 | -0.3 | 0,2857 | 0,842 | Belum signifikan |
| 30 | Manual Cepat | Fixed PID | 0.4 | 1.0 | -0.6 | 0,0000 | 0,065 | Belum signifikan |
| 30 | Manual Cepat | GS PID | 0.4 | 1.0 | -0.6 | 0,0000 | 0,065 | Belum signifikan |
| 30 | Manual Presisi | Fixed PID | 0.7 | 1.0 | -0.3 | 0,0000 | 0,842 | Belum signifikan |
| 30 | Manual Presisi | GS PID | 0.7 | 1.0 | -0.3 | 0,0000 | 0,842 | Belum signifikan |
| 30 | Fixed PID | GS PID | 1.0 | 1.0 | 0.0 | — | 1,000 | Belum signifikan |

## SettlingTime_s Deskriptif Kondisional

SettlingTime_s diringkas pada trial yang menghasilkan nilai valid berdasarkan kriteria kondisional, yaitu respons memasuki dan mempertahankan batas yang ditetapkan sampai akhir pengamatan. Jumlah trial tersedia dapat berbeda antarskenario dan setpoint. Metrik ini disajikan secara deskriptif dan tidak diuji secara inferensial.

| SP | Skenario | n valid | n total | Median | Q1 | Q3 | IQR |
|---:|---|---:|---:|---:|---:|---:|---:|
| 15 | Manual Cepat | 3 | 10 | 2,80 | 2,80 | 3,70 | 0,90 |
| 15 | Manual Presisi | 6 | 10 | 33,80 | 33,60 | 50,65 | 17,05 |
| 15 | Fixed PID | 7 | 10 | 23,20 | 15,45 | 25,39 | 9,94 |
| 15 | GS PID | 9 | 10 | 11,06 | 10,55 | 14,68 | 4,13 |
| 20 | Manual Cepat | 4 | 10 | 8,22 | 5,00 | 12,87 | 7,88 |
| 20 | Manual Presisi | 6 | 10 | 40,89 | 38,25 | 41,80 | 3,55 |
| 20 | Fixed PID | 8 | 10 | 24,49 | 20,81 | 30,36 | 9,56 |
| 20 | GS PID | 8 | 10 | 15,97 | 12,29 | 17,58 | 5,29 |
| 25 | Manual Cepat | 3 | 10 | 9,52 | 8,61 | 10,16 | 1,55 |
| 25 | Manual Presisi | 6 | 10 | 60,53 | 49,55 | 75,97 | 26,42 |
| 25 | Fixed PID | 9 | 10 | 41,80 | 29,66 | 47,99 | 18,33 |
| 25 | GS PID | 9 | 10 | 19,07 | 14,94 | 29,40 | 14,46 |
| 30 | Manual Cepat | 4 | 10 | 21,66 | 18,11 | 23,60 | 5,49 |
| 30 | Manual Presisi | 7 | 10 | 51,36 | 45,94 | 55,49 | 9,55 |
| 30 | Fixed PID | 10 | 10 | 24,75 | 19,97 | 31,01 | 11,04 |
| 30 | GS PID | 10 | 10 | 22,94 | 20,22 | 24,87 | 4,65 |

## BridgingCount Deskriptif

| SP | Skenario | n | Total | Median | IQR lo | IQR hi | Min | Max | Prop>0 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | Manual Cepat | 10 | 3 | 0,0 | 0,00 | 0,00 | 0 | 2 | 0,2 |
| 15 | Manual Presisi | 10 | 29 | 3,0 | 1,50 | 3,75 | 1 | 6 | 1,0 |
| 15 | Fixed PID | 10 | 10 | 1,0 | 0,25 | 1,00 | 0 | 3 | 0,7 |
| 15 | GS PID | 10 | 3 | 0,0 | 0,00 | 0,75 | 0 | 1 | 0,3 |
| 20 | Manual Cepat | 10 | 2 | 0,0 | 0,00 | 0,00 | 0 | 1 | 0,2 |
| 20 | Manual Presisi | 10 | 44 | 3,0 | 3,00 | 4,00 | 1 | 14 | 1,0 |
| 20 | Fixed PID | 10 | 15 | 1,0 | 0,00 | 2,00 | 0 | 5 | 0,6 |
| 20 | GS PID | 10 | 7 | 1,0 | 0,25 | 1,00 | 0 | 1 | 0,7 |
| 25 | Manual Cepat | 10 | 0 | 0,0 | 0,00 | 0,00 | 0 | 0 | 0,0 |
| 25 | Manual Presisi | 10 | 61 | 6,0 | 4,25 | 7,50 | 3 | 10 | 1,0 |
| 25 | Fixed PID | 10 | 44 | 4,0 | 1,75 | 6,75 | 0 | 10 | 0,8 |
| 25 | GS PID | 10 | 4 | 0,0 | 0,00 | 1,00 | 0 | 1 | 0,4 |
| 30 | Manual Cepat | 10 | 7 | 0,0 | 0,00 | 1,75 | 0 | 2 | 0,4 |
| 30 | Manual Presisi | 10 | 85 | 7,5 | 5,25 | 11,00 | 4 | 16 | 1,0 |
| 30 | Fixed PID | 10 | 13 | 1,0 | 1,00 | 1,00 | 0 | 4 | 0,9 |
| 30 | GS PID | 10 | 9 | 1,0 | 0,00 | 1,75 | 0 | 2 | 0,6 |

## Catatan Interpretasi

1. "Belum signifikan" ≠ "sama"; bukti tidak cukup menolak H₀ pada α=0.05 dengan n=10.
2. Kruskal–Wallis menguji distribusi/peringkat; perbedaan lokasi diasumsikan jika bentuk distribusi serupa.
3. Ukuran efek Kruskal–Wallis: rank_epsilon_squared = H / (N−1).
4. Ukuran efek Welch ANOVA: eta_p2 (partial eta-squared) dari kolom `np2` keluaran `pingouin.welch_anova()`. Nilai terverifikasi: Duration SP25=0,5974, RiseTime SP25=0,6426, RiseTime SP30=0,6591.
5. Koreksi Holm per keluarga metrik (4 setpoint per metrik), bukan global 16 uji.
6. WithinTolerance: uji chi-square Monte Carlo bersyarat pada margin tetap, 100.000 simulasi, seed 42.
7. Perbedaan AbsError_pct antarskenario ditemukan pada SP15 dan SP30 setelah koreksi Holm.
8. Perbedaan MaxOvershoot_pct: SP15 dan SP30.
9. Perbedaan Duration_s: SP15, SP20, SP25, dan SP30.
10. Perbedaan RiseTime_10\_90\_s: SP15, SP20, SP25, dan SP30.
11. SettlingTime_s dan BridgingCount: deskriptif saja; tidak diuji inferensial.
12. Metode dikunci sebelum eksekusi; tidak diubah berdasarkan hasil signifikansi.
13. CI Cliff’s δ dan Hedges’ g dihitung dari 10.000 bootstrap.
