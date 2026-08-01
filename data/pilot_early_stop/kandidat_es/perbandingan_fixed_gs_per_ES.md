# Per-ES Perbandingan Fixed PID vs Gain Scheduling PID

## Early Stop = 0.2 g

| Controller | n_valid | mean_AbsError_g | MAE% | SD_error_g | mean_Overshoot_g | mean_Duration_s | mean_BridgingCount |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fixed PID | 3 | 1.169 | 4.899 | 1.224 | 0.266 | 40.126 | 2.667 |
| Gain Scheduling PID | 3 | 1.487 | 8.732 | 1.760 | 1.171 | 23.105 | 0.750 |

### Trial-level key data

| FileName | Controller | Setpoint_g | FinalError_g | Duration_s | MaxOvershoot_g | BridgingCount | Status | Valid | QC_Flags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Fixed_0.2_SP15_trial01.txt | Fixed PID | 15.0 | 0.69 | 51.25 | 0.69 | 2.0 | AKURAT | True | nan |
| Fixed_0.2_SP15_trial02.txt | Fixed PID | 15.0 | -0.96 | 51.24 | 0.0 | 1.0 | UNDERSHOOT | True | nan |
| Fixed_0.2_SP15_trial03.txt | Fixed PID | 15.0 | 0.55 | 16.65 | 0.55 | 1.0 | AKURAT | True | nan |
| Fixed_ES0.2_SP20_trial01.txt | Fixed PID | 20.0 | 0.16 | 22.85 | 0.68 | 0.0 | AKURAT | True | nan |
| Fixed_ES0.2_SP20_trial02.txt | Fixed PID | 20.0 | 0.6 | 26.72 | 0.6 | 0.0 | AKURAT | True | nan |
| Fixed_ES0.2_SP20_trial03.txt | Fixed PID | 20.0 | -0.05 | 49.45 | 0.0 | 0.0 | AKURAT | True | nan |
| Fixed_0.2_SP25_trial01.txt | Fixed PID | 25.0 | -3.22 | 51.25 | 0.0 | 8.0 | UNDERSHOOT | True | nan |
| Fixed_0.2_SP25_trial02.txt | Fixed PID | 25.0 | -1.11 | 51.25 | 0.0 | 4.0 | AKURAT | True | nan |
| Fixed_0.2_SP25_trial03.txt | Fixed PID | 25.0 | 0.67 | 20.78 | 0.67 | 0.0 | AKURAT | True | nan |
| Fixed_0.2_SP30_trial01.txt | Fixed PID | 30.0 | -2.63 | 51.25 | 0.0 | 6.0 | UNDERSHOOT | True | nan |
| Fixed_0.2_SP30_trial02.txt | Fixed PID | 30.0 | -0.08 | 37.57 | 0.0 | 4.0 | AKURAT | True | nan |
| Fixed_0.2_SP30_trial03.txt | Fixed PID | 30.0 | -3.31 | 51.25 | 0.0 | 6.0 | UNDERSHOOT | True | nan |
| GS_ES0.2_SP15_trial01.txt | Gain Scheduling PID | 15.0 | -0.26 | 24.92 | 0.0 | 0.0 | AKURAT | True | nan |
| GS_ES0.2_SP15_trial02.txt | Gain Scheduling PID | 15.0 | 8.61 | 9.43 | 8.61 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.2_SP15_trial03.txt | Gain Scheduling PID | 15.0 | 3.46 | 15.37 | 3.46 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.2_SP20_trial01.txt | Gain Scheduling PID | 20.0 | 0.13 | 18.98 | 0.13 | 1.0 | AKURAT | True | nan |
| GS_ES0.2_SP20_trial02.txt | Gain Scheduling PID | 20.0 | 0.12 | 24.66 | 0.18 | 2.0 | AKURAT | True | nan |
| GS_ES0.2_SP20_trial03..txt | Gain Scheduling PID | 20.0 | 1.14 | 14.59 | 1.14 | 0.0 | OVERSHOOT | True | nan |
| GS_ES0.2_SP25_trial01.txt | Gain Scheduling PID | 25.0 | -2.57 | 51.23 | 0.0 | 2.0 | UNDERSHOOT | True | nan |
| GS_ES0.2_SP25_trial02.txt | Gain Scheduling PID | 25.0 | -0.14 | 20.52 | 0.02 | 0.0 | AKURAT | True | nan |
| GS_ES0.2_SP25_trial03.txt | Gain Scheduling PID | 25.0 | -0.15 | 19.23 | 0.0 | 0.0 | AKURAT | True | nan |
| GS_ES0.2_SP30_trial01.txt | Gain Scheduling PID | 30.0 | 0.52 | 33.68 | 0.52 | 0.0 | AKURAT | True | nan |
| GS_ES0.2_SP30_trial02.txt | Gain Scheduling PID | 30.0 | -0.06 | 16.91 | 0.0 | 1.0 | AKURAT | True | nan |
| GS_ES0.2_SP30_trial03.txt | Gain Scheduling PID | 30.0 | -0.68 | 27.74 | 0.0 | 1.0 | AKURAT | True | nan |

---

## Early Stop = 0.3 g

| Controller | n_valid | mean_AbsError_g | MAE% | SD_error_g | mean_Overshoot_g | mean_Duration_s | mean_BridgingCount |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fixed PID | 3 | 1.196 | 4.769 | 1.654 | 0.824 | 39.953 | 2.333 |
| Gain Scheduling PID | 3 | 1.596 | 6.662 | 1.722 | 1.417 | 22.672 | 0.917 |

### Trial-level key data

| FileName | Controller | Setpoint_g | FinalError_g | Duration_s | MaxOvershoot_g | BridgingCount | Status | Valid | QC_Flags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Fixed_0.3_SP15_trial01.txt | Fixed PID | 15.0 | 0.12 | 43.24 | 0.14 | 5.0 | AKURAT | True | nan |
| Fixed_0.3_SP15_trial02.txt | Fixed PID | 15.0 | -0.63 | 48.15 | 0.0 | 2.0 | AKURAT | True | nan |
| Fixed_0.3_SP15_trial03.txt | Fixed PID | 15.0 | -0.55 | 34.98 | 0.0 | 2.0 | AKURAT | True | nan |
| Fixed_ES0.3_SP20_trial01.txt | Fixed PID | 20.0 | 2.16 | 36.79 | 2.16 | 4.0 | OVERSHOOT | True | nan |
| Fixed_ES0.3_SP20_trial02.txt | Fixed PID | 20.0 | -0.27 | 27.24 | 0.0 | 0.0 | AKURAT | True | nan |
| Fixed_ES0.3_SP20_trial03.txt | Fixed PID | 20.0 | 0.13 | 33.18 | 0.13 | 3.0 | AKURAT | True | nan |
| Fixed_0.3_SP25_trial01.txt | Fixed PID | 25.0 | 0.04 | 47.38 | 0.04 | 3.0 | AKURAT | True | nan |
| Fixed_0.3_SP25_trial02.txt | Fixed PID | 25.0 | 0.33 | 41.44 | 0.33 | 2.0 | AKURAT | True | nan |
| Fixed_0.3_SP25_trial03.txt | Fixed PID | 25.0 | 0.82 | 27.75 | 0.82 | 2.0 | AKURAT | True | nan |
| Fixed_0.3_SP30_trial01.txt | Fixed PID | 30.0 | -1.84 | 51.25 | 0.0 | 1.0 | UNDERSHOOT | True | nan |
| Fixed_0.3_SP30_trial02.txt | Fixed PID | 30.0 | -1.19 | 51.25 | 0.0 | 2.0 | AKURAT | True | nan |
| Fixed_0.3_SP30_trial03.txt | Fixed PID | 30.0 | 6.27 | 36.79 | 6.27 | 2.0 | OVERSHOOT | True | nan |
| GS_ES0.3_SP15_trial01.txt | Gain Scheduling PID | 15.0 | 0.77 | 12.26 | 0.77 | 0.0 | OVERSHOOT | True | nan |
| GS_ES0.3_SP15_trial02.txt | Gain Scheduling PID | 15.0 | -0.23 | 8.39 | 0.0 | 0.0 | AKURAT | True | nan |
| GS_ES0.3_SP15_trial03.txt | Gain Scheduling PID | 15.0 | -0.46 | 26.71 | 0.0 | 0.0 | AKURAT | True | nan |
| GS_ES0.3_SP20_trial01.txt | Gain Scheduling PID | 20.0 | 0.87 | 37.05 | 0.87 | 3.0 | AKURAT | True | nan |
| GS_ES0.3_SP20_trial02.txt | Gain Scheduling PID | 20.0 | -0.12 | 14.59 | 0.14 | 0.0 | AKURAT | True | nan |
| GS_ES0.3_SP20_trial03.txt | Gain Scheduling PID | 20.0 | 3.59 | 21.3 | 3.59 | 2.0 | OVERSHOOT | True | nan |
| GS_ES0.3_SP25_trial01.txt | Gain Scheduling PID | 25.0 | -1.91 | 51.23 | 0.0 | 0.0 | UNDERSHOOT | True | nan |
| GS_ES0.3_SP25_trial02.txt | Gain Scheduling PID | 25.0 | 1.96 | 21.55 | 2.39 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.3_SP25_trial03.txt | Gain Scheduling PID | 25.0 | 1.54 | 15.36 | 1.54 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.3_SP25_trial04.txt | Gain Scheduling PID | 25.0 | -0.27 | 24.9 | 0.0 | 1.0 | AKURAT | True | nan |
| GS_ES0.3_SP30_trial01.txt | Gain Scheduling PID | 30.0 | 4.34 | 15.36 | 4.34 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.3_SP30_trial02.txt | Gain Scheduling PID | 30.0 | 0.12 | 20.52 | 0.12 | 0.0 | AKURAT | True | nan |
| GS_ES0.3_SP30_trial03.txt | Gain Scheduling PID | 30.0 | 3.24 | 27.74 | 3.24 | 3.0 | OVERSHOOT | True | nan |

---

## Early Stop = 0.4 g

| Controller | n_valid | mean_AbsError_g | MAE% | SD_error_g | mean_Overshoot_g | mean_Duration_s | mean_BridgingCount |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fixed PID | 3 | 1.563 | 7.370 | 2.439 | 1.260 | 30.830 | 1.667 |
| Gain Scheduling PID | 3 | 1.012 | 5.623 | 1.340 | 0.858 | 20.481 | 0.750 |

### Trial-level key data

| FileName | Controller | Setpoint_g | FinalError_g | Duration_s | MaxOvershoot_g | BridgingCount | Status | Valid | QC_Flags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Fixed_0.4 _SP15_trial01.txt | Fixed PID | 15.0 | -0.18 | 35.49 | 0.0 | 1.0 | AKURAT | True | nan |
| Fixed_0.4 _SP15_trial02.txt | Fixed PID | 15.0 | 4.63 | 27.5 | 4.63 | 2.0 | OVERSHOOT | True | nan |
| Fixed_0.4 _SP15_trial03.txt | Fixed PID | 15.0 | -0.82 | 22.85 | 0.0 | 0.0 | UNDERSHOOT | True | nan |
| Fixed_0.4 _SP20_trial01.txt | Fixed PID | 20.0 | 0.76 | 28.79 | 0.76 | 1.0 | AKURAT | True | nan |
| Fixed_ES0.4_SP20_trial02.txt | Fixed PID | 20.0 | -0.23 | 22.85 | 0.0 | 1.0 | AKURAT | True | nan |
| Fixed_ES0.4_SP20_trial03.txt | Fixed PID | 20.0 | -0.43 | 14.33 | 0.0 | 1.0 | AKURAT | True | nan |
| Fixed_0.4_SP25_trial01.txt | Fixed PID | 25.0 | -1.75 | 51.24 | 0.0 | 3.0 | UNDERSHOOT | True | nan |
| Fixed_0.4_SP25_trial02.txt | Fixed PID | 25.0 | 0.03 | 39.37 | 0.03 | 3.0 | AKURAT | True | nan |
| Fixed_0.4_SP25_trial03.txt | Fixed PID | 25.0 | 5.38 | 46.08 | 5.38 | 5.0 | OVERSHOOT | True | nan |
| Fixed_0.4_SP30_trial01.txt | Fixed PID | 30.0 | 4.16 | 27.5 | 4.16 | 1.0 | OVERSHOOT | True | nan |
| Fixed_0.4_SP30_trial02.txt | Fixed PID | 30.0 | -0.23 | 22.85 | 0.0 | 0.0 | AKURAT | True | nan |
| Fixed_0.4_SP30_trial03.txt | Fixed PID | 30.0 | 0.16 | 31.11 | 0.16 | 2.0 | AKURAT | True | nan |
| GS_ES0.4_SP15_trial01.txt | Gain Scheduling PID | 15.0 | -0.09 | 20.79 | 0.0 | 1.0 | AKURAT | True | nan |
| GS_ES0.4_SP15_trial02.txt | Gain Scheduling PID | 15.0 | 5.72 | 15.11 | 5.72 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.4_SP15_trial03.txt | Gain Scheduling PID | 15.0 | 1.4 | 15.11 | 1.4 | 1.0 | OVERSHOOT | True | nan |
| last.txt | Gain Scheduling PID | 15.0 | 1.4 | 15.11 | 1.4 | 1.0 | OVERSHOOT | True | nan |
| GS_ES0.4_SP20_trial01.txt | Gain Scheduling PID | 20.0 | 0.06 | 14.59 | 0.18 | 0.0 | AKURAT | True | nan |
| GS_ES0.4_SP20_trial02.txt | Gain Scheduling PID | 20.0 | -0.42 | 18.72 | 0.0 | 1.0 | AKURAT | True | nan |
| GS_ES0.4_SP20_trial03.txt | Gain Scheduling PID | 20.0 | 0.41 | 18.46 | 0.41 | 0.0 | AKURAT | True | nan |
| GS_ES0.4_SP25_trial01.txt | Gain Scheduling PID | 25.0 | -0.38 | 24.92 | 0.0 | 2.0 | AKURAT | True | nan |
| GS_ES0.4_SP25_trial02.txt | Gain Scheduling PID | 25.0 | -0.33 | 26.97 | 0.0 | 1.0 | AKURAT | True | nan |
| GS_ES0.4_SP25_trial03 dan 04.txt | Gain Scheduling PID | 25.0 | 1.48 | 12.52 | 1.48 | 0.0 | OVERSHOOT | True | nan |
| GS_ES0.4_SP30_trial01.txt | Gain Scheduling PID | 30.0 | 1.11 | 24.65 | 1.11 | 1.0 | AKURAT | True | nan |
| GS_ES0.4_SP30_trial02.txt | Gain Scheduling PID | 30.0 | -0.48 | 31.35 | 0.0 | 1.0 | AKURAT | True | nan |
| GS_ES0.4_SP30_trial03.txt | Gain Scheduling PID | 30.0 | -0.27 | 22.58 | 0.0 | 0.0 | AKURAT | True | nan |

---

