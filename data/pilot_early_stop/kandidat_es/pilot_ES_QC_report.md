# Pilot Early Stop - Quality Control Report

## Executive Summary

- **Total trial setelah update:** 74
- **Successfully parsed:** 74
- **Valid trials (Valid=TRUE):** 74
- **24 kombinasi lengkap:** YA

## Trial Distribution

### Fixed PID

| Setpoint | ES 0.2 | ES 0.3 | ES 0.4 |
|---|---:|---:|---:|
| 15g | 3 | 3 | 3 |
| 20g | 3 | 3 | 3 |
| 25g | 3 | 3 | 3 |
| 30g | 3 | 3 | 3 |
### Gain Scheduling PID

| Setpoint | ES 0.2 | ES 0.3 | ES 0.4 |
|---|---:|---:|---:|
| 15g | 3 | 3 | 4 |
| 20g | 3 | 3 | 3 |
| 25g | 3 | 4 | 3 |
| 30g | 3 | 3 | 3 |

## Kombinasi Kurang dari 3 Trial

Tidak ada.

## Kombinasi Lebih dari 3 Trial

- Gain Scheduling PID, ES=0.3g, SP=25.0g: 4 (extra 1)
- Gain Scheduling PID, ES=0.4g, SP=15.0g: 4 (extra 1)

## File Baru Diparse

- Fixed_0.2_SP25_trial03.txt: SUCCESS, Valid=TRUE
- GS_ES0.3_SP15_trial01.txt: SUCCESS, Valid=TRUE
- GS_ES0.3_SP15_trial02.txt: SUCCESS, Valid=TRUE
- GS_ES0.3_SP15_trial03.txt: SUCCESS, Valid=TRUE

## Mismatch File Baru

Tidak ada.

> [!NOTE]
> Outlier/anomali ditandai, tidak dihapus.
