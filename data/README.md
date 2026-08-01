# Data

## master_dataset_160.csv

Dataset final penelitian. 1 baris = 1 trial. 160 baris total (4 skenario x 4 setpoint x 10 ulangan).

### Kolom utama

| Kolom | Deskripsi |
|---|---|
| Scenario | Skenario kendali: Manual Cepat, Manual Presisi, Fixed PID, GS PID |
| Setpoint_g | Target massa (g): 15, 20, 25, 30 |
| TrialNo | Nomor ulangan (1-10) |
| FinalMass_g | Massa akhir yang tercapai (g) |
| MAE_pct | Galat absolut persentase per trial terhadap setpoint (1 baris = 1 trial) |
| Overshoot_pct | Overshoot maksimum (%) |
| Duration_s | Durasi proses (s) |
| FinalError_g | Galat akhir (g) |
| RiseTime_10_90_s | Rise time 10-90% (s) |
| WithinTolerance | TRUE jika galat akhir dalam toleransi 5% |
| SettlingTime_s | Settling time (s), hanya untuk trial WithinTolerance=TRUE |
| BridgingCount | Jumlah aktivasi hammer reaktif (anti-bridging) |
| Valid | TRUE jika trial memenuhi kriteria validasi |
| StopReason | Alasan berhenti: TARGET (normal) |

### Catatan

- Raw log 160 trial (.txt) tersedia di `data/pengujian_final/log_160_trial/`.
- Seluruh trial: Valid=TRUE, StopReason=TARGET.
