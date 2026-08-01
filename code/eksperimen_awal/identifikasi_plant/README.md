# identifikasi_plant

## Tujuan
Identifikasi plant (step response) untuk penetapan parameter awal PID via Ziegler-Nichols.

## Input
`data/identifikasi_plant/` (4 file: 25/30/35/40 derajat.txt)

## Skrip Utama
`zn_integrating_process.m` (MATLAB)

## Output
Parameter Kp, Ki, Kd awal per sudut operasi (hasil di console/figure MATLAB)

## Cara Menjalankan
Jalankan `zn_integrating_process.m` dari MATLAB. Path sudah relatif terhadap root repositori.

## Hubungan dengan Skripsi
Baseline awal tuning Fixed PID dan GS PID. Bab III.
