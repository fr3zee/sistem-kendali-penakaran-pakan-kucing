## 4.1 Gambaran Umum

Pengujian dilaksanakan dengan 160 trial (4 skenario, 4 setpoint, 10 ulangan). Keempat skenario yang dibandingkan adalah Manual Cepat, Manual Presisi, Fixed PID, dan GS PID. Manual Cepat dan Manual Presisi menggunakan bukaan utama servo tetap dengan early stop berbasis massa, shake preventif, dan hammer reaktif. Fixed PID dan GS PID menambahkan umpan balik kontinu dari pembacaan massa. BridgingCount mencatat jumlah aktivasi hammer reaktif saja; shake preventif tidak menambah counter.

## 4.2 Statistik Deskriptif

### Tabel MAPE (%)

*MAPE = rata-rata galat absolut persentase per 10 trial (kolom MAE_pct).*

| Setpoint (g) | Manual Cepat | Manual Presisi | Fixed PID | GS PID |
|---|---|---|---|---|
| 15 | 22.314 | 8.310 | 6.049 | 1.876 |
| 20 | 9.247 | 7.380 | 7.450 | 3.726 |
| 25 | 10.738 | 7.589 | 4.090 | 2.625 |
| 30 | 7.470 | 4.836 | 1.213 | 1.134 |

### Tabel Median Galat Absolut Persentase (%)

*Median_MAE_pct = median AbsError_pct per 10 trial.*

| Setpoint (g) | Manual Cepat | Manual Presisi | Fixed PID | GS PID |
|---|---|---|---|---|
| 15 | 13.690 | 3.845 | 2.670 | 1.385 |
| 20 | 9.320 | 2.405 | 3.125 | 2.720 |
| 25 | 7.000 | 1.125 | 1.930 | 1.935 |
| 30 | 7.795 | 2.610 | 0.975 | 1.010 |

### Tabel Median Overshoot (%)

| Setpoint (g) | Manual Cepat | Manual Presisi | Fixed PID | GS PID |
|---|---|---|---|---|
| 15 | 13.690 | 2.775 | 0.000 | 0.120 |
| 20 | 9.320 | 0.880 | 2.360 | 2.460 |
| 25 | 7.000 | 0.000 | 0.795 | 1.470 |
| 30 | 7.795 | 2.610 | 0.335 | 0.000 |

### Tabel Median Durasi (s)

| Setpoint (g) | Manual Cepat | Manual Presisi | Fixed PID | GS PID |
|---|---|---|---|---|
| 15 | 4.995 | 33.925 | 17.690 | 13.040 |
| 20 | 11.190 | 43.215 | 26.080 | 20.530 |
| 25 | 9.515 | 48.520 | 47.395 | 19.630 |
| 30 | 20.370 | 59.365 | 29.050 | 26.335 |

## 4.3 Pemeriksaan Asumsi Statistik

**Galat absolut persentase per trial (AbsError_pct)**: Shapiro-Wilk: 4/4 setpoint menyimpang dari normalitas. Brown-Forsythe: 1/4 setpoint varians tidak homogen.

**Overshoot maksimum (%)**: Shapiro-Wilk: 4/4 setpoint menyimpang dari normalitas. Brown-Forsythe: 1/4 setpoint varians tidak homogen.

**Durasi (s)**: Shapiro-Wilk: 3/4 setpoint menyimpang dari normalitas. Brown-Forsythe: 1/4 setpoint varians tidak homogen.

**Rise time 10-90% (s)**: Shapiro-Wilk: 2/4 setpoint menyimpang dari normalitas. Brown-Forsythe: 4/4 setpoint varians tidak homogen.

Kruskal-Wallis digunakan ketika terdapat penyimpangan normalitas, sedangkan Welch ANOVA digunakan ketika normalitas tidak ditolak dan tetap dapat mengakomodasi ketidakhomogenan varians. Koreksi Holm diterapkan per metrik dengan empat setpoint sebagai satu keluarga.

## 4.4 Analisis Inferensial Omnibus

### Galat absolut persentase per trial (AbsError_pct)

| SP | Uji | Statistik | df | p_raw | p_holm | Sig | ES |
|---|---|---|---|---|---|---|---|
| SP15 | Kruskal-Wallis | 10.817 | 3/- | 0.0128 | 0.0383 | Ya | ε²=0.277 |
| SP20 | Kruskal-Wallis | 3.650 | 3/- | 0.3019 | 0.4542 | Tidak | ε²=0.094 |
| SP25 | Kruskal-Wallis | 4.339 | 3/- | 0.2271 | 0.4542 | Tidak | ε²=0.111 |
| SP30 | Kruskal-Wallis | 12.089 | 3/- | 0.0071 | 0.0283 | Ya | ε²=0.310 |

Terdapat perbedaan signifikan antarkelompok pada SP15, SP30 (p_holm < 0,05).

### Overshoot maksimum (%)

| SP | Uji | Statistik | df | p_raw | p_holm | Sig | ES |
|---|---|---|---|---|---|---|---|
| SP15 | Kruskal-Wallis | 11.926 | 3/- | 0.0076 | 0.0229 | Ya | ε²=0.306 |
| SP20 | Kruskal-Wallis | 4.079 | 3/- | 0.2531 | 0.2531 | Tidak | ε²=0.105 |
| SP25 | Kruskal-Wallis | 6.000 | 3/- | 0.1116 | 0.2233 | Tidak | ε²=0.154 |
| SP30 | Kruskal-Wallis | 18.411 | 3/- | 0.0004 | 0.0014 | Ya | ε²=0.472 |

Terdapat perbedaan signifikan antarkelompok pada SP15, SP30 (p_holm < 0,05).

### Durasi (s)

| SP | Uji | Statistik | df | p_raw | p_holm | Sig | ES |
|---|---|---|---|---|---|---|---|
| SP15 | Kruskal-Wallis | 22.726 | 3/- | <0.0001 | <0.0001 | Ya | ε²=0.583 |
| SP20 | Kruskal-Wallis | 29.283 | 3/- | <0.0001 | <0.0001 | Ya | ε²=0.751 |
| SP25 | Welch ANOVA | 31.911 | 3/15.9 | <0.0001 | <0.0001 | Ya | ηp²=0.597 |
| SP30 | Kruskal-Wallis | 25.280 | 3/- | <0.0001 | <0.0001 | Ya | ε²=0.648 |

Terdapat perbedaan signifikan antarkelompok pada SP15, SP20, SP25, SP30 (p_holm < 0,05).

### Rise time 10-90% (s)

| SP | Uji | Statistik | df | p_raw | p_holm | Sig | ES |
|---|---|---|---|---|---|---|---|
| SP15 | Kruskal-Wallis | 15.056 | 3/- | 0.0018 | 0.0018 | Ya | ε²=0.386 |
| SP20 | Kruskal-Wallis | 22.841 | 3/- | <0.0001 | 0.0001 | Ya | ε²=0.586 |
| SP25 | Welch ANOVA | 27.168 | 3/17.3 | <0.0001 | <0.0001 | Ya | ηp²=0.643 |
| SP30 | Welch ANOVA | 10.288 | 3/19.3 | 0.0003 | 0.0006 | Ya | ηp²=0.659 |

Terdapat perbedaan signifikan antarkelompok pada SP15, SP20, SP25, SP30 (p_holm < 0,05).

## 4.5 Analisis Post-hoc

### Galat absolut persentase per trial (AbsError_pct)

| SP | A | B | p_adjusted | ES | Arah |
|---|---|---|---|---|---|
| SP15 | Manual Cepat | GS PID | 0.0109 | Cliff_delta=0.710 CI[0.31,1.00] | Manual Cepat > GS PID |
| SP30 | Manual Cepat | GS PID | 0.0128 | Cliff_delta=0.820 CI[0.52,1.00] | Manual Cepat > GS PID |
| SP30 | Manual Cepat | Fixed PID | 0.0182 | Cliff_delta=0.780 CI[0.44,1.00] | Manual Cepat > Fixed PID |

### Overshoot maksimum (%)

| SP | A | B | p_adjusted | ES | Arah |
|---|---|---|---|---|---|
| SP15 | Manual Cepat | GS PID | 0.0078 | Cliff_delta=0.840 CI[0.52,1.00] | Manual Cepat > GS PID |
| SP15 | Manual Cepat | Fixed PID | 0.0370 | Cliff_delta=0.640 CI[0.20,0.94] | Manual Cepat > Fixed PID |
| SP30 | Manual Cepat | GS PID | 0.0005 | Cliff_delta=0.900 CI[0.68,1.00] | Manual Cepat > GS PID |
| SP30 | Manual Cepat | Fixed PID | 0.0088 | Cliff_delta=0.880 CI[0.60,1.00] | Manual Cepat > Fixed PID |

### Durasi (s)

| SP | A | B | p_adjusted | ES | Arah |
|---|---|---|---|---|---|
| SP15 | Manual Cepat | Manual Presisi | <0.0001 | Cliff_delta=-0.920 CI[-1.00,-0.72] | Manual Presisi >= Manual Cepat |
| SP15 | Manual Cepat | Fixed PID | 0.0032 | Cliff_delta=-0.900 CI[-1.00,-0.64] | Fixed PID >= Manual Cepat |
| SP15 | Manual Presisi | GS PID | 0.0449 | Cliff_delta=0.660 CI[0.20,1.00] | Manual Presisi > GS PID |
| SP20 | Manual Cepat | Manual Presisi | <0.0001 | Cliff_delta=-1.000 CI[-1.00,-1.00] | Manual Presisi >= Manual Cepat |
| SP20 | Manual Cepat | Fixed PID | 0.0013 | Cliff_delta=-0.980 CI[-1.00,-0.88] | Fixed PID >= Manual Cepat |
| SP20 | Manual Presisi | GS PID | 0.0051 | Cliff_delta=0.920 CI[0.70,1.00] | Manual Presisi > GS PID |
| SP25 | Manual Cepat | Fixed PID | 0.0001 | Hedges_g=-3.263 CI[-4.60,-1.93] | Fixed PID >= Manual Cepat |
| SP25 | Manual Cepat | Manual Presisi | 0.0006 | Hedges_g=-2.707 CI[-3.92,-1.49] | Manual Presisi >= Manual Cepat |
| SP25 | Manual Presisi | GS PID | 0.0157 | Hedges_g=1.482 CI[0.49,2.47] | Manual Presisi > GS PID |
| SP25 | Fixed PID | GS PID | 0.0158 | Hedges_g=1.452 CI[0.47,2.44] | Fixed PID > GS PID |
| SP25 | Manual Cepat | GS PID | 0.0357 | Hedges_g=-1.408 CI[-2.39,-0.43] | GS PID >= Manual Cepat |
| SP30 | Manual Cepat | Manual Presisi | <0.0001 | Cliff_delta=-1.000 CI[-1.00,-1.00] | Manual Presisi >= Manual Cepat |
| SP30 | Manual Presisi | GS PID | 0.0050 | Cliff_delta=1.000 CI[1.00,1.00] | Manual Presisi > GS PID |
| SP30 | Manual Presisi | Fixed PID | 0.0332 | Cliff_delta=0.840 CI[0.46,1.00] | Manual Presisi > Fixed PID |

### Rise time 10-90% (s)

| SP | A | B | p_adjusted | ES | Arah |
|---|---|---|---|---|---|
| SP15 | Manual Cepat | Manual Presisi | 0.0011 | Cliff_delta=-0.740 CI[-1.00,-0.34] | Manual Presisi >= Manual Cepat |
| SP15 | Manual Cepat | Fixed PID | 0.0339 | Cliff_delta=-0.820 CI[-1.00,-0.46] | Fixed PID >= Manual Cepat |
| SP20 | Manual Cepat | Manual Presisi | <0.0001 | Cliff_delta=-0.960 CI[-1.00,-0.82] | Manual Presisi >= Manual Cepat |
| SP20 | Manual Cepat | Fixed PID | 0.0037 | Cliff_delta=-0.880 CI[-1.00,-0.64] | Fixed PID >= Manual Cepat |
| SP20 | Manual Presisi | GS PID | 0.0150 | Cliff_delta=0.800 CI[0.44,1.00] | Manual Presisi > GS PID |
| SP25 | Manual Cepat | Manual Presisi | 0.0002 | Hedges_g=-3.001 CI[-4.28,-1.72] | Manual Presisi >= Manual Cepat |
| SP25 | Manual Cepat | Fixed PID | 0.0005 | Hedges_g=-2.663 CI[-3.87,-1.46] | Fixed PID >= Manual Cepat |
| SP25 | Manual Presisi | GS PID | 0.0013 | Hedges_g=2.122 CI[1.03,3.22] | Manual Presisi > GS PID |
| SP25 | Fixed PID | GS PID | 0.0041 | Hedges_g=1.861 CI[0.81,2.91] | Fixed PID > GS PID |
| SP25 | Manual Cepat | GS PID | 0.0354 | Hedges_g=-1.343 CI[-2.31,-0.37] | GS PID >= Manual Cepat |
| SP30 | Manual Cepat | Manual Presisi | 0.0007 | Hedges_g=-2.315 CI[-3.45,-1.18] | Manual Presisi >= Manual Cepat |
| SP30 | Manual Presisi | GS PID | 0.0009 | Hedges_g=2.397 CI[1.25,3.55] | Manual Presisi > GS PID |
| SP30 | Manual Presisi | Fixed PID | 0.0022 | Hedges_g=2.110 CI[1.02,3.20] | Manual Presisi > Fixed PID |

> GS PID memiliki durasi lebih rendah secara deskriptif pada seluruh setpoint, tetapi perbedaan langsung Fixed PID vs GS PID hanya signifikan pada SP25.

## 4.6 Proporsi Trial dalam Toleransi (WithinTolerance)

| SP | chi-sq | p_MC | p_holm | Sig | V Cramer | MC% | MP% | Fixed% | GS% |
|---|---|---|---|---|---|---|---|---|---|
| SP15 | 8.000 | 0.0573 | 0.1146 | Tidak | 0.447 | 30% | 60% | 70% | 90% |
| SP20 | 4.835 | 0.2346 | 0.2346 | Tidak | 0.348 | 40% | 60% | 80% | 80% |
| SP25 | 11.282 | 0.0101 | 0.0302 | Ya | 0.531 | 30% | 60% | 90% | 90% |
| SP30 | 14.194 | 0.0021 | 0.0085 | Ya | 0.596 | 40% | 70% | 100% | 100% |

Uji Pearson chi-square dengan p Monte Carlo (N=100.000, seed=42) menunjukkan proporsi berbeda signifikan pada SP25, SP30.

Post-hoc Fisher: tidak ada pasangan signifikan setelah koreksi Holm.

## 4.7 Konsistensi Galat Akhir (FinalError_g)

| SP | BF-stat | p_raw | p_holm | Sig | SD MC | SD MP | SD Fixed | SD GS | SD min |
|---|---|---|---|---|---|---|---|---|---|
| SP15 | 5.584 | 0.0030 | 0.0120 | Ya | 3.2880 | 1.9402 | 1.4902 | 0.4109 | GS PID |
| SP20 | 0.549 | 0.6522 | 0.6596 | Tidak | 1.2991 | 2.0576 | 2.8293 | 0.8346 | GS PID |
| SP25 | 1.183 | 0.3298 | 0.6596 | Tidak | 2.6617 | 2.7797 | 1.9755 | 0.7875 | GS PID |
| SP30 | 3.136 | 0.0372 | 0.1117 | Tidak | 1.6564 | 2.2264 | 0.4840 | 0.4288 | GS PID |

GS PID memiliki SD FinalError_g terendah secara deskriptif pada 4/4 setpoint. Perbedaan varians signifikan pada SP15 (Brown-Forsythe, Holm).

## 4.8 Settling Time (Kondisional)

*SettlingTime dihitung hanya pada trial yang memenuhi definisi settling.*

| SP | Skenario | n tersedia | Median (s) | Q1 (s) | Q3 (s) |
|---|---|---|---|---|---|
| SP15 | Fixed PID | 7/10 | 23.20 | 15.45 | 25.39 |
| SP15 | GS PID | 9/10 | 11.06 | 10.55 | 14.68 |
| SP15 | Manual Cepat | 3/10 | 2.80 | 2.80 | 3.70 |
| SP15 | Manual Presisi | 6/10 | 33.80 | 33.60 | 50.65 |
| SP20 | Fixed PID | 8/10 | 24.49 | 20.81 | 30.36 |
| SP20 | GS PID | 8/10 | 15.97 | 12.29 | 17.58 |
| SP20 | Manual Cepat | 4/10 | 8.22 | 5.00 | 12.87 |
| SP20 | Manual Presisi | 6/10 | 40.89 | 38.25 | 41.80 |
| SP25 | Fixed PID | 9/10 | 41.80 | 29.66 | 47.99 |
| SP25 | GS PID | 9/10 | 19.07 | 14.94 | 29.40 |
| SP25 | Manual Cepat | 3/10 | 9.52 | 8.61 | 10.16 |
| SP25 | Manual Presisi | 6/10 | 60.53 | 49.55 | 75.97 |
| SP30 | Fixed PID | 10/10 | 24.75 | 19.97 | 31.01 |
| SP30 | GS PID | 10/10 | 22.94 | 20.22 | 24.87 |
| SP30 | Manual Cepat | 4/10 | 21.66 | 18.11 | 23.60 |
| SP30 | Manual Presisi | 7/10 | 51.36 | 45.94 | 55.49 |

## 4.9 Rise Time 10-90%

*RiseTime tersedia untuk seluruh 10 trial per kelompok dan dianalisis inferensial.*

| SP | Skenario | Mean (s) | Median (s) | SD |
|---|---|---|---|---|
| SP15 | Manual Cepat | 5.29 | 3.62 | 4.88 |
| SP15 | Manual Presisi | 23.43 | 25.31 | 14.65 |
| SP15 | Fixed PID | 13.89 | 11.36 | 4.95 |
| SP15 | GS PID | 11.54 | 10.07 | 6.96 |
| SP20 | Manual Cepat | 8.29 | 8.65 | 4.45 |
| SP20 | Manual Presisi | 33.71 | 32.02 | 16.49 |
| SP20 | Fixed PID | 22.98 | 21.17 | 11.18 |
| SP20 | GS PID | 13.61 | 14.33 | 4.42 |
| SP25 | Manual Cepat | 8.58 | 8.52 | 2.77 |
| SP25 | Manual Presisi | 36.19 | 37.45 | 12.15 |
| SP25 | Fixed PID | 34.50 | 34.09 | 12.89 |
| SP25 | GS PID | 15.03 | 13.04 | 5.89 |
| SP30 | Manual Cepat | 16.84 | 17.96 | 7.22 |
| SP30 | Manual Presisi | 48.04 | 45.20 | 16.77 |
| SP30 | Fixed PID | 20.50 | 18.85 | 5.61 |
| SP30 | GS PID | 17.01 | 16.65 | 5.11 |

## 4.10 Aktivasi Hammer Reaktif (BridgingCount)

*BridgingCount = jumlah aktivasi hammer reaktif saja; shake preventif tidak menambah counter.*

| SP | Skenario | n total | Median | Min | Max | Prop>0 |
|---|---|---|---|---|---|---|
| SP15 | Fixed PID | 10 | 1.0 | 0 | 3 | 0.70 |
| SP15 | GS PID | 10 | 0.0 | 0 | 1 | 0.30 |
| SP15 | Manual Cepat | 10 | 0.0 | 0 | 2 | 0.20 |
| SP15 | Manual Presisi | 10 | 3.0 | 1 | 6 | 1.00 |
| SP20 | Fixed PID | 10 | 1.0 | 0 | 5 | 0.60 |
| SP20 | GS PID | 10 | 1.0 | 0 | 1 | 0.70 |
| SP20 | Manual Cepat | 10 | 0.0 | 0 | 1 | 0.20 |
| SP20 | Manual Presisi | 10 | 3.0 | 1 | 14 | 1.00 |
| SP25 | Fixed PID | 10 | 4.0 | 0 | 10 | 0.80 |
| SP25 | GS PID | 10 | 0.0 | 0 | 1 | 0.40 |
| SP25 | Manual Cepat | 10 | 0.0 | 0 | 0 | 0.00 |
| SP25 | Manual Presisi | 10 | 6.0 | 3 | 10 | 1.00 |
| SP30 | Fixed PID | 10 | 1.0 | 0 | 4 | 0.90 |
| SP30 | GS PID | 10 | 1.0 | 0 | 2 | 0.60 |
| SP30 | Manual Cepat | 10 | 0.0 | 0 | 2 | 0.40 |
| SP30 | Manual Presisi | 10 | 7.5 | 4 | 16 | 1.00 |

## 4.11 Sintesis Profil Primer

**SP15**: MAPE terendah = GS PID (1.876%). Durasi median terendah = Manual Cepat (5.00 s). SD FinalError terendah = GS PID (0.4109 g).
**SP20**: MAPE terendah = GS PID (3.726%). Durasi median terendah = Manual Cepat (11.19 s). SD FinalError terendah = GS PID (0.8346 g).
**SP25**: MAPE terendah = GS PID (2.625%). Durasi median terendah = Manual Cepat (9.52 s). SD FinalError terendah = GS PID (0.7875 g).
**SP30**: MAPE terendah = GS PID (1.134%). Durasi median terendah = Manual Cepat (20.37 s). SD FinalError terendah = GS PID (0.4288 g).
