# Urutan Pengolahan Data Penelitian

## 1. `pembentukan_dataset/`
160 log mentah → dataset 160 trial.
```
python code/pembentukan_dataset/generate_master_dataset.py
```

## 2. `validasi_dataset/`
Memeriksa struktur, kelengkapan, duplikat, dan konsistensi dataset.
```
python code/validasi_dataset/tahap0_validasi_master_dataset.py
```

## 3. `sintesis_hasil/tahap1_statistik_deskriptif.py`
Statistik deskriptif dasar per skenario dan setpoint.
```
python code/sintesis_hasil/tahap1_statistik_deskriptif.py
```

## 4. `pemeriksaan_asumsi/`
Shapiro–Wilk, Brown–Forsythe, rekomendasi metode uji.
```
python code/pemeriksaan_asumsi/tahap2_pemeriksaan_asumsi.py
```

## 5. `analisis_inferensial/`
Uji omnibus, post-hoc, ukuran efek, koreksi Holm.
```
python code/analisis_inferensial/tahap3_analisis_inferensial.py
```

## 6. `sintesis_hasil/tahap4_sintesis_multidimensi.py`
Profil primer dan tambahan kondisional.
```
python code/sintesis_hasil/tahap4_sintesis_multidimensi.py
```

## 7. `finalisasi/`
Visualisasi Bab IV.
```
python code/finalisasi/tahap5_visualisasi_bab4.py
```
