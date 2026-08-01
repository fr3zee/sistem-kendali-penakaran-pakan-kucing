# Pemetaan Restrukturisasi

Branch asal: `restructure-repository-canonical` → di-merge ke `master` (ca731b1)

| Lokasi Lama | Lokasi Baru | Keterangan |
|-------------|-------------|-----------|
| code/tahap0/tahap0_validasi_master_dataset.py | code/validasi_dataset/ | Validasi integritas dataset |
| code/tahap1/tahap1_statistik_deskriptif.py | code/sintesis_hasil/ | Deskriptif dasar |
| code/tahap1/hasil_statistik_deskriptif_tahap1.csv | hasil/sintesis_hasil/ | Output deskriptif |
| code/tahap1/hasil_statistik_deskriptif_agregat_tahap1.csv | hasil/sintesis_hasil/ | Output deskriptif agregat |
| code/tahap2/tahap2_rekonstruksi_dan_verifikasi.py | code/pemeriksaan_asumsi/ | Shapiro, BF, rekomendasi uji |
| code/tahap3/tahap3_analisis_inferensial.py | code/analisis_inferensial/ | Inferensial |
| code/tahap3/tahap3_generate_reports.py | code/analisis_inferensial/ | Generate laporan inferensial |
| code/tahap4/tahap4_sintesis_multidimensi.py | code/sintesis_hasil/ | Profil primer/tambahan |
| code/tahap5/tahap5_generate_narasi_bab4.py | code/finalisasi/ | Narasi Bab IV |
| code/tahap5/tahap5_generate_docx_bab4_revisi_terbatas.py | code/finalisasi/ | DOCX Bab IV |
| code/tahap5/tahap5_visualisasi_bab4.py | code/finalisasi/ | Gambar Bab IV |
| data/master_dataset_160.csv | data/pengujian_final/master_dataset_160.csv | Satu lokasi kanonis |
| code/tahap4/tahap4_sintesis_multidimensi_backup.py | archive/legacy_tahap_structure/tahap4/ | Arsip |
| code/tahap5/tahap5_generate_docx_bab4.py | archive/legacy_tahap_structure/tahap5/ | Arsip (versi lama) |
| code/tahap5/tmp_broken.py | archive/legacy_tahap_structure/tahap5/ | Arsip |
| MATLAB/zn_integrating_process copy.m | archive/legacy_tahap_structure/matlab/ | Arsip duplikat |
