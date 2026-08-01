# BAB IV — HASIL DAN PEMBAHASAN

## 4.1 Gambaran Umum Pengujian

Pengujian dilakukan dengan desain eksperimen 4×4×10: empat skenario kontrol (Manual Cepat, Manual Presisi, Fixed PID, dan GS PID) diuji pada empat setpoint massa (15, 20, 25, dan 30 g) dengan masing-masing 10 trial per kombinasi. Tabel 4.1 menampilkan kelengkapan data untuk seluruh kombinasi.

**Tabel 4.1. Desain Eksperimen 4×4×10 dan Kelengkapan Data**

| Setpoint (g) | Skenario | n |
|---|---|---|
| 15 | Manual Cepat | 10 |
| 15 | Manual Presisi | 10 |
| 15 | Fixed PID | 10 |
| 15 | GS PID | 10 |
| 20 | Manual Cepat | 10 |
| 20 | Manual Presisi | 10 |
| 20 | Fixed PID | 10 |
| 20 | GS PID | 10 |
| 25 | Manual Cepat | 10 |
| 25 | Manual Presisi | 10 |
| 25 | Fixed PID | 10 |
| 25 | GS PID | 10 |
| 30 | Manual Cepat | 10 |
| 30 | Manual Presisi | 10 |
| 30 | Fixed PID | 10 |
| 30 | GS PID | 10 |

Manual Cepat merupakan baseline open-loop dengan perintah bukaan utama servo 40°, sedangkan Manual Presisi merupakan baseline open-loop dengan perintah bukaan utama servo 20°. Istilah ‘Manual’ merupakan nama skenario dan tidak berarti pakan dituangkan oleh manusia. Mekanisme anti-bridging yang digunakan bersama dapat memberikan gerakan servo sementara ketika kondisi pemicunya terpenuhi. Fixed PID dan GS PID merupakan skenario closed-loop. GS PID memilih gain berdasarkan aturan zona error yang telah ditentukan, bukan melalui adaptive control atau self-tuning daring.

Outcome primer terdiri atas MAE%, overshoot maksimum, durasi proses, dan simpangan baku galat akhir. Outcome tambahan terdiri atas rise time 10–90% dan WithinTolerance. SettlingTime merupakan outcome kondisional karena hanya dihitung pada subset trial dalam toleransi. BridgingCount merupakan indikator pendukung aktivitas mekanisme anti-bridging firmware.

## 4.2 Validasi dan Kelengkapan Data

Dataset analisis final terdiri atas 160 trial valid dengan `StopReason=TARGET`, masing-masing 10 trial pada setiap kombinasi skenario–setpoint. Trial ulang atau penggantian yang terjadi selama pengambilan data tidak termasuk dalam dataset final; setelah dataset dikunci, tidak ada eksklusi tambahan yang dilakukan. Seluruh trial memenuhi validasi teknis yang ditetapkan pada tahap pengambilan dan pengolahan data awal.

Integritas seluruh data yang digunakan pada Bab IV telah diverifikasi sebelum pembentukan laporan. Seluruh angka, tabel, dan grafik pada bab ini bersumber dari hasil analisis yang tercatat pada tabel dan gambar di bab ini serta lampiran teknis.

## 4.3 Ringkasan Outcome Primer

Gambar 4.1 menampilkan profil empat outcome primer pada setpoint 15–30 g. Panel A menunjukkan MAE% kelompok dengan rerata dan error bar simpangan baku sampel. Panel B menunjukkan sebaran overshoot maksimum untuk seluruh trial (10 titik per kombinasi) beserta marker rerata yang lebih besar. Panel C menunjukkan durasi proses dengan rerata dan error bar simpangan baku sampel. Panel D menunjukkan simpangan baku galat akhir tanpa error bar tambahan karena simpangan baku itu sendiri merupakan outcome konsistensi.

Secara deskriptif, GS PID menunjukkan nilai terendah pada MAE%, overshoot maksimum, dan simpangan baku galat akhir di sebagian besar setpoint (Gambar 4.1). Manual Cepat menunjukkan durasi proses tercepat tetapi MAE% dan overshoot tertinggi. Manual Presisi menunjukkan durasi terlama dengan akurasi lebih baik dari Manual Cepat tetapi tidak sebaik skenario closed-loop. Fixed PID menunjukkan performa di antara GS PID dan baseline open-loop pada sebagian besar outcome.

Pola tersebut konsisten dengan prinsip gain scheduling berbasis aturan. Ketika error normalisasi masih besar, parameter PID yang aktif menghasilkan aksi kendali yang mendorong pergerakan massa menuju setpoint. Seiring error mengecil dan sistem memasuki zona yang lebih dekat ke target, parameter yang aktif berubah sehingga koreksi berlangsung lebih terkendali. Mekanisme ini memungkinkan GS PID menyesuaikan karakteristik respons terhadap setiap fase penakaran, sedangkan Fixed PID menggunakan satu kombinasi parameter sepanjang proses.

Tabel 4.2 merangkum hasil uji omnibus seluruh outcome pada setiap setpoint. Kolom "Statistik" menampilkan nilai H (Kruskal-Wallis), F (Welch ANOVA), atau W (Brown–Forsythe) sesuai uji yang digunakan. Kolom "p_Holm" adalah p-value setelah koreksi Holm terhadap keluarga 16 uji omnibus. Kolom "Ukuran efek/indikator" menampilkan ε² (Kruskal-Wallis), f²* (Welch ANOVA), VarRatio max/min (Brown–Forsythe), atau Cramér's V (Fisher–Freeman–Halton); lihat catatan di bawah tabel untuk definisi f²*.

**Tabel 4.2. Hasil Omnibus Outcome Primer, Tambahan, dan Kondisional**

| Outcome | Setpoint (g) | Uji | Statistik | p_Holm | Signifikan | Ukuran efek/indikator |
|---|---:|---|---:|---:|---|---|
| MAE% | 15 | Kruskal-Wallis | 10,82 | 0,038266 | Ya | rank_epsilon_squared=0,277 |
| MAE% | 20 | Kruskal-Wallis | 3,65 | 0,454213 | Tidak | rank_epsilon_squared=0,094 |
| MAE% | 25 | Kruskal-Wallis | 4,34 | 0,454213 | Tidak | rank_epsilon_squared=0,111 |
| MAE% | 30 | Kruskal-Wallis | 12,09 | 0,028334 | Ya | rank_epsilon_squared=0,310 |
| Overshoot maksimum | 15 | Kruskal-Wallis | 11,93 | 0,022920 | Ya | rank_epsilon_squared=0,306 |
| Overshoot maksimum | 20 | Kruskal-Wallis | 4,08 | 0,253103 | Tidak | rank_epsilon_squared=0,105 |
| Overshoot maksimum | 25 | Kruskal-Wallis | 6,00 | 0,223258 | Tidak | rank_epsilon_squared=0,154 |
| Overshoot maksimum | 30 | Kruskal-Wallis | 18,41 | 0,001447 | Ya | rank_epsilon_squared=0,472 |
| Durasi | 15 | Kruskal-Wallis | 22,73 | < 0,001 | Ya | rank_epsilon_squared=0,583 |
| Durasi | 20 | Kruskal-Wallis | 29,28 | < 0,001 | Ya | rank_epsilon_squared=0,751 |
| Durasi | 25 | Welch ANOVA | 31,91 | < 0,001 | Ya | eta_p2=0,597 |
| Durasi | 30 | Kruskal-Wallis | 25,28 | < 0,001 | Ya | rank_epsilon_squared=0,648 |
| Rise time | 15 | Kruskal-Wallis | 15,06 | 0,001770 | Ya | rank_epsilon_squared=0,386 |
| Rise time | 20 | Kruskal-Wallis | 22,84 | < 0,001 | Ya | rank_epsilon_squared=0,586 |
| Rise time | 25 | Welch ANOVA | 27,17 | < 0,001 | Ya | eta_p2=0,643 |
| Rise time | 30 | Welch ANOVA | 10,29 | < 0,001 | Ya | eta_p2=0,659 |
| Konsistensi FinalError_g | 15 | Brown–Forsythe | 5,58 | 0,011965 | Ya | VarRatio max/min=64,043 |
| Konsistensi FinalError_g | 20 | Brown–Forsythe | 0,55 | 0,659600 | Tidak | VarRatio max/min=11,493 |
| Konsistensi FinalError_g | 25 | Brown–Forsythe | 1,18 | 0,659600 | Tidak | VarRatio max/min=12,459 |
| Konsistensi FinalError_g | 30 | Brown–Forsythe | 3,14 | 0,111657 | Tidak | VarRatio max/min=26,960 |
| WithinTolerance | 15 | Pendekatan Monte Carlo bersyarat (Fisher–Freeman–Halton, tabel 4×2) | 8,00 | 0,114599 | Tidak | CramersV=0,447 |
| WithinTolerance | 20 | Pendekatan Monte Carlo bersyarat (Fisher–Freeman–Halton, tabel 4×2) | 4,84 | 0,234578 | Tidak | CramersV=0,348 |
| WithinTolerance | 25 | Pendekatan Monte Carlo bersyarat (Fisher–Freeman–Halton, tabel 4×2) | 11,28 | 0,030240 | Ya | CramersV=0,531 |
| WithinTolerance | 30 | Pendekatan Monte Carlo bersyarat (Fisher–Freeman–Halton, tabel 4×2) | 14,19 | 0,008520 | Ya | CramersV=0,596 |

*\* Ukuran efek dihitung menggunakan pendekatan yang mengakomodasi ketidakhomogenan varians antarkelompok, sebagaimana dijelaskan pada Bab III.*

Tabel 4.3 menyajikan seluruh pasangan post-hoc yang signifikan setelah koreksi Holm, tanpa pemotongan. Hanya pasangan yang melewati threshold koreksi yang ditampilkan; pasangan tidak signifikan tidak disertakan. Kolom "p tersesuaikan" adalah p-value setelah penyesuaian metode yang tercantum pada kolom Metode. Kolom "CI 95%" adalah interval kepercayaan ukuran efek; tanda — menunjukkan CI tidak tersedia dari sumber.

**Tabel 4.3. Seluruh Pasangan Post-hoc Signifikan**

| Outcome | Setpoint (g) | Metode | Kelompok A | Kelompok B | p tersesuaikan | Ukuran efek | Nilai | CI 95% | Arah perbedaan |
|---|---:|---|---|---|---:|---|---:|---|---|
| MAE% | 15 | Dunn dengan koreksi Holm | Manual Cepat | GS PID | 0,010923 | Cliff_delta | 0,710 | [0,310; 1,000] | nilai/rank Manual Cepat cenderung lebih tinggi daripada GS PID |
| MAE% | 30 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,018217 | Cliff_delta | 0,780 | [0,440; 1,000] | nilai/rank Manual Cepat cenderung lebih tinggi daripada Fixed PID |
| MAE% | 30 | Dunn dengan koreksi Holm | Manual Cepat | GS PID | 0,012840 | Cliff_delta | 0,820 | [0,520; 1,000] | nilai/rank Manual Cepat cenderung lebih tinggi daripada GS PID |
| Overshoot maksimum | 15 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,037007 | Cliff_delta | 0,640 | [0,200; 0,940] | nilai/rank Manual Cepat cenderung lebih tinggi daripada Fixed PID |
| Overshoot maksimum | 15 | Dunn dengan koreksi Holm | Manual Cepat | GS PID | 0,007804 | Cliff_delta | 0,840 | [0,520; 1,000] | nilai/rank Manual Cepat cenderung lebih tinggi daripada GS PID |
| Overshoot maksimum | 30 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,008805 | Cliff_delta | 0,880 | [0,600; 1,000] | nilai/rank Manual Cepat cenderung lebih tinggi daripada Fixed PID |
| Overshoot maksimum | 30 | Dunn dengan koreksi Holm | Manual Cepat | GS PID | < 0,001 | Cliff_delta | 0,900 | [0,680; 1,000] | nilai/rank Manual Cepat cenderung lebih tinggi daripada GS PID |
| Durasi | 15 | Dunn dengan koreksi Holm | Manual Cepat | Manual Presisi | < 0,001 | Cliff_delta | -0,920 | [-1,000; -0,720] | nilai/rank Manual Presisi cenderung lebih tinggi daripada Manual Cepat |
| Durasi | 15 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,003179 | Cliff_delta | -0,900 | [-1,000; -0,640] | nilai/rank Fixed PID cenderung lebih tinggi daripada Manual Cepat |
| Durasi | 15 | Dunn dengan koreksi Holm | Manual Presisi | GS PID | 0,044907 | Cliff_delta | 0,660 | [0,200; 1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada GS PID |
| Durasi | 20 | Dunn dengan koreksi Holm | Manual Cepat | Manual Presisi | < 0,001 | Cliff_delta | -1,000 | [-1,000; -1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada Manual Cepat |
| Durasi | 20 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,001338 | Cliff_delta | -0,980 | [-1,000; -0,880] | nilai/rank Fixed PID cenderung lebih tinggi daripada Manual Cepat |
| Durasi | 20 | Dunn dengan koreksi Holm | Manual Presisi | GS PID | 0,005059 | Cliff_delta | 0,920 | [0,700; 1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada GS PID |
| Durasi | 25 | Games-Howell | Manual Cepat | Manual Presisi | < 0,001 | Hedges_g | -2,707 | [-3,920; -1,494] | rerata Manual Presisi lebih tinggi daripada Manual Cepat |
| Durasi | 25 | Games-Howell | Manual Cepat | Fixed PID | < 0,001 | Hedges_g | -3,263 | [-4,602; -1,925] | rerata Fixed PID lebih tinggi daripada Manual Cepat |
| Durasi | 25 | Games-Howell | Manual Cepat | GS PID | 0,035715 | Hedges_g | -1,408 | [-2,388; -0,429] | rerata GS PID lebih tinggi daripada Manual Cepat |
| Durasi | 25 | Games-Howell | Manual Presisi | GS PID | 0,015739 | Hedges_g | 1,482 | [0,492; 2,471] | rerata Manual Presisi lebih tinggi daripada GS PID |
| Durasi | 25 | Games-Howell | Fixed PID | GS PID | 0,015755 | Hedges_g | 1,452 | [0,467; 2,438] | rerata Fixed PID lebih tinggi daripada GS PID |
| Durasi | 30 | Dunn dengan koreksi Holm | Manual Cepat | Manual Presisi | < 0,001 | Cliff_delta | -1,000 | [-1,000; -1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada Manual Cepat |
| Durasi | 30 | Dunn dengan koreksi Holm | Manual Presisi | Fixed PID | 0,033156 | Cliff_delta | 0,840 | [0,460; 1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada Fixed PID |
| Durasi | 30 | Dunn dengan koreksi Holm | Manual Presisi | GS PID | 0,005000 | Cliff_delta | 1,000 | [1,000; 1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada GS PID |
| Rise time | 15 | Dunn dengan koreksi Holm | Manual Cepat | Manual Presisi | 0,001101 | Cliff_delta | -0,740 | [-1,000; -0,340] | nilai/rank Manual Presisi cenderung lebih tinggi daripada Manual Cepat |
| Rise time | 15 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,033906 | Cliff_delta | -0,820 | [-1,000; -0,460] | nilai/rank Fixed PID cenderung lebih tinggi daripada Manual Cepat |
| Rise time | 20 | Dunn dengan koreksi Holm | Manual Cepat | Manual Presisi | < 0,001 | Cliff_delta | -0,960 | [-1,000; -0,820] | nilai/rank Manual Presisi cenderung lebih tinggi daripada Manual Cepat |
| Rise time | 20 | Dunn dengan koreksi Holm | Manual Cepat | Fixed PID | 0,003676 | Cliff_delta | -0,880 | [-1,000; -0,640] | nilai/rank Fixed PID cenderung lebih tinggi daripada Manual Cepat |
| Rise time | 20 | Dunn dengan koreksi Holm | Manual Presisi | GS PID | 0,015026 | Cliff_delta | 0,800 | [0,440; 1,000] | nilai/rank Manual Presisi cenderung lebih tinggi daripada GS PID |
| Rise time | 25 | Games-Howell | Manual Cepat | Manual Presisi | < 0,001 | Hedges_g | -3,001 | [-4,279; -1,723] | rerata Manual Presisi lebih tinggi daripada Manual Cepat |
| Rise time | 25 | Games-Howell | Manual Cepat | Fixed PID | < 0,001 | Hedges_g | -2,663 | [-3,868; -1,460] | rerata Fixed PID lebih tinggi daripada Manual Cepat |
| Rise time | 25 | Games-Howell | Manual Cepat | GS PID | 0,035427 | Hedges_g | -1,343 | [-2,313; -0,372] | rerata GS PID lebih tinggi daripada Manual Cepat |
| Rise time | 25 | Games-Howell | Manual Presisi | GS PID | 0,001313 | Hedges_g | 2,122 | [1,026; 3,218] | rerata Manual Presisi lebih tinggi daripada GS PID |
| Rise time | 25 | Games-Howell | Fixed PID | GS PID | 0,004123 | Hedges_g | 1,861 | [0,811; 2,910] | rerata Fixed PID lebih tinggi daripada GS PID |
| Rise time | 30 | Games-Howell | Manual Cepat | Manual Presisi | < 0,001 | Hedges_g | -2,315 | [-3,447; -1,182] | rerata Manual Presisi lebih tinggi daripada Manual Cepat |
| Rise time | 30 | Games-Howell | Manual Presisi | Fixed PID | 0,002178 | Hedges_g | 2,110 | [1,016; 3,204] | rerata Manual Presisi lebih tinggi daripada Fixed PID |
| Rise time | 30 | Games-Howell | Manual Presisi | GS PID | < 0,001 | Hedges_g | 2,397 | [1,248; 3,547] | rerata Manual Presisi lebih tinggi daripada GS PID |

Tabel 4.3 memuat seluruh pasangan signifikan dari post-hoc metrik kontinu dan WithinTolerance tanpa pemotongan. Nilai p pada setiap baris merupakan p-value tersesuaikan sesuai metode yang tercantum. Tidak terdapat pasangan WithinTolerance yang tetap signifikan setelah koreksi Holm. Brown–Forsythe hanya digunakan sebagai uji omnibus konsistensi; tidak dilakukan post-hoc pairwise. CI ditampilkan bila tersedia pada sumber; tanda em dash menunjukkan bahwa sumber final tidak menyediakan CI.

## 4.4 Akurasi Massa (MAE%)

Point estimate MAE% terendah diperoleh oleh GS PID pada SP15 (1,876%); GS PID pada SP20 (3,726%); GS PID pada SP25 (2,625%); GS PID pada SP30 (1,134%).

Setelah koreksi Holm, tidak ditemukan bukti yang cukup untuk menyatakan perbedaan MAE% antarskenario pada setiap setpoint (Tabel 4.2). Perbedaan point estimate tidak ditafsirkan sebagai keunggulan inferensial. Hasil yang tidak signifikan dapat berkaitan dengan variabilitas dalam kelompok dan koreksi multipel yang diterapkan pada keluarga 16 uji; interpretasi inferensial tetap mengacu pada hasil uji statistik.

Secara keseluruhan, akurasi massa antarskenario tidak berbeda secara signifikan pada setiap setpoint setelah koreksi multipel; perbedaan point estimate bersifat deskriptif.

## 4.5 Overshoot Maksimum

GS PID memiliki rerata overshoot terendah pada SP15, SP25, dan SP30. Pada SP20, Fixed PID (6,886%) sedikit lebih rendah daripada GS PID (3,073%).

Omnibus overshoot hanya signifikan pada SP15 setelah koreksi Holm (Tabel 4.2). Pasangan signifikan pada setpoint tersebut ialah Manual Cepat–Fixed PID dan Manual Cepat–GS PID, dengan nilai/rank Manual Cepat cenderung lebih tinggi (Tabel 4.3). Pada SP30, omnibus mendekati ambang signifikansi (p_Holm=0,062404) dengan ukuran efek sedang (ε²=0,250); namun karena tidak melewati threshold koreksi Holm, interpretasi inferensial tidak dilakukan.

Overshoot pada sistem penakaran granular tidak semata-mata ditentukan oleh aksi kendali. Material granular dapat mengalami stagnasi sementara lalu mengalir kembali secara tidak terduga setelah hambatan berkurang. Ketika hal tersebut terjadi, perintah penghentian servo tidak langsung menghentikan material yang sudah bergerak karena ada jeda mekanik aktuator dan material yang telah bergerak menuju wadah. Perbedaan overshoot yang signifikan antara Manual Cepat dan skenario closed-loop pada SP15 mengindikasikan bahwa kendali closed-loop dengan perubahan parameter berbasis zona error dapat memberikan respons akhir yang lebih terukur dibandingkan aksi open-loop dengan bukaan servo lebih besar, meskipun overshoot tetap dapat muncul karena dinamika aliran granular tidak sepenuhnya dapat diantisipasi oleh sinyal kendali.

## 4.6 Durasi Proses

Manual Cepat memiliki rerata durasi paling rendah pada seluruh setpoint, sedangkan Manual Presisi memiliki rerata durasi paling tinggi (lihat Gambar 4.1 Panel C dan Tabel 4.2). Omnibus durasi signifikan pada seluruh setpoint setelah koreksi Holm. Jenis dan nilai ukuran efek dilaporkan terpisah sesuai metode uji pada Tabel 4.2; pasangan signifikan lengkap tersedia pada Tabel 4.3.

Perbedaan durasi antara skenario open-loop dan closed-loop dapat dipahami dari cara masing-masing skenario menghasilkan keputusan aksi servo. Skenario open-loop mengeksekusi perintah bukaan yang telah ditentukan tanpa memperbarui keputusan berdasarkan pembacaan massa terkini, sehingga durasi proses sangat bergantung pada laju aliran material. Skenario closed-loop memperbarui aksi kendali berdasarkan error massa terukur pada setiap siklus; durasi bergantung pada dinamika umpan balik antara pembacaan sensor, keputusan PID, dan respons servo. Secara keseluruhan, omnibus durasi signifikan pada seluruh setpoint; perbedaan antara kedua skenario closed-loop dibahas lebih lanjut pada §4.8.

Dalam implementasi kendali, durasi proses sangat dipengaruhi oleh strategi penghentian (stopping strategy) yang diterapkan pada akhir penakaran. Skenario closed-loop memiliki keuntungan adaptif dalam memperlambat pergerakan servo saat massa mendekati setpoint, yang pada gilirannya mengurangi durasi akhir akibat perlunya koreksi berulang. Sementara itu, skenario manual bergantung sepenuhnya pada estimasi awal; jika bukaan servo tidak diatur secara presisi, sistem akan mengalami kekurangan (under-shooting) yang memerlukan durasi tambahan, atau kelebihan (overshoot) yang tidak bisa dikoreksi secara aktif. Integrasi gain scheduling memfasilitasi transisi ini agar lebih efisien di setiap setpoint massa yang berbeda.

## 4.7 Konsistensi Galat Akhir (SD FinalError_g)

Secara deskriptif, GS PID memiliki simpangan baku galat akhir terendah pada SP15, SP20, dan SP25, sedangkan Fixed PID terendah pada SP30.

Brown–Forsythe hanya signifikan pada SP15 (p_Holm=0,011965, Tabel 4.2), sehingga terdapat bukti bahwa sedikitnya satu varians antarskenario berbeda. GS PID memiliki varians terkecil secara deskriptif (lihat Gambar 4.1 Panel D) dan rasio varians terbesar terhadap terkecil sebesar 64,043 (Tabel 4.2, baris Konsistensi FinalError_g SP15). Tidak dilakukan post-hoc pairwise, sehingga pasangan sumber perbedaan tidak ditetapkan. SP20, SP25, dan SP30 tidak menunjukkan bukti perbedaan varians setelah koreksi Holm.

Pada SP15, terdapat bukti bahwa konsistensi galat akhir berbeda antarskenario; GS PID menunjukkan simpangan baku terendah secara deskriptif. Pada SP20–SP30, tidak ditemukan bukti perbedaan varians setelah koreksi Holm.

Khusus pada SP15, bukti statistik mendukung adanya perbedaan varians galat akhir antarkelompok. Secara teoritis, perubahan parameter PID pada zona error kecil dapat memengaruhi konsistensi koreksi akhir antarreplikasi, meskipun hubungan ini tidak dapat diverifikasi secara kausal dari data yang tersedia. Pembahasan mekanistik ini dibatasi pada SP15; pada SP20, SP25, dan SP30 tidak terdapat bukti statistik yang mendukung interpretasi serupa sehingga perbedaan deskriptif pada ketiga setpoint tersebut tidak ditafsirkan lebih lanjut.

## 4.8 Fokus Perbandingan Fixed PID dan GS PID

Perbandingan Fixed PID dan GS PID difokuskan untuk mengevaluasi profil gain scheduling dibandingkan parameter gain tetap. Tabel 4.4 menampilkan point estimate empat outcome primer dan status Pareto per setpoint.

**Tabel 4.4. Audit Fixed PID dan GS PID Per Setpoint**

| Setpoint (g) | Skenario | MAE% | Overshoot% | Durasi (s) | SD Galat (g) |
|---|---|---|---|---|---|
| 15 | Fixed PID | 6,05 | 5,14 | 20,94 | 1,49 |
| 15 | GS PID | 1,88 | 1,23 | 15,44 | 0,41 |
| 20 | Fixed PID | 7,45 | 6,89 | 28,82 | 2,83 |
| 20 | GS PID | 3,73 | 3,07 | 18,39 | 0,83 |
| 25 | Fixed PID | 4,09 | 3,59 | 46,80 | 1,98 |
| 25 | GS PID | 2,62 | 1,93 | 24,82 | 0,79 |
| 30 | Fixed PID | 1,21 | 0,69 | 34,52 | 0,48 |
| 30 | GS PID | 1,13 | 0,49 | 27,03 | 0,43 |

*Dominated: skenario lain memiliki nilai lebih rendah atau sama pada seluruh outcome dan lebih rendah pada sedikitnya satu outcome. Non-dominated: tidak ada skenario lain yang memenuhi syarat tersebut.*

Pada SP15, GS PID mendominasi Fixed PID pada keempat outcome primer: MAE% lebih rendah (1,88 vs 6,05), overshoot lebih rendah (1,23 vs 5,14), durasi lebih rendah (15,44 vs 20,94 s), dan SD galat lebih rendah (0,41 vs 1,49 g). Pada SP20, terdapat trade-off: Fixed PID lebih rendah pada MAE% dan overshoot, sedangkan GS PID lebih rendah pada durasi dan SD galat. Pada SP25, GS PID kembali mendominasi Fixed PID pada keempat outcome primer. Pada SP30, terdapat trade-off: GS PID lebih rendah pada MAE%, overshoot, dan durasi, sedangkan Fixed PID lebih rendah pada SD galat.

Perbedaan pola antar-setpoint mengindikasikan bahwa performa sistem kendali bergantung pada kondisi operasi. Perubahan setpoint mengubah jumlah material yang dipindahkan, lama proses, dan kemungkinan terjadinya gangguan aliran. Karena zona error pada gain scheduling berbasis aturan ditentukan berdasarkan persentase error normalisasi, batas antara zona secara otomatis menyesuaikan skala terhadap setpoint. Namun, pendekatan berbasis persentase error tidak mengukur seluruh keadaan material di hopper; variasi kondisi aliran yang tidak tercermin pada pembacaan error massa kemungkinan berkontribusi pada trade-off yang terlihat pada setpoint tertentu.

Berdasarkan durasi yang dilaporkan firmware, GS PID memiliki rerata durasi lebih rendah daripada Fixed PID pada setiap setpoint. Perbandingan post-hoc menunjukkan bahwa perbedaan Fixed PID–GS PID signifikan pada SP20 dan SP25, sedangkan pada SP15 dan SP30 belum ditemukan perbedaan pasangan yang signifikan setelah penyesuaian pengujian. Dibandingkan dengan Manual Presisi, GS PID memiliki durasi tercatat lebih rendah dengan perbedaan signifikan pada seluruh setpoint. Temuan tersebut menunjukkan bahwa manfaat GS PID terutama terlihat pada pengurangan durasi proses closed-loop dibandingkan PID dengan gain tetap dan skenario Manual Presisi, bukan pada pencapaian durasi absolut terendah karena Manual Cepat tetap memiliki rerata durasi paling rendah.

Interpretasi perbandingan durasi lintas kelompok perlu dilakukan secara hati-hati. Manual Cepat dan Manual Presisi menghitung durasi sebelum penutupan serta pembacaan massa akhir, sedangkan Fixed PID dan GS PID menghitungnya setelah penutupan dan pembacaan akhir. Oleh karena itu, perbandingan di dalam kelompok manual dan di dalam kelompok PID memiliki endpoint yang lebih seragam dibandingkan perbandingan lintas kedua kelompok. Data asli tetap dipertahankan tanpa normalisasi waktu secara post-hoc.

## 4.9 Sintesis Trade-off dan Pareto Empat Dimensi

Gambar 4.2 menampilkan relasi dominasi antar-skenario berdasarkan empat point estimate primer. Skenario di pangkal panah tidak lebih buruk pada seluruh outcome primer dan memiliki nilai lebih rendah pada sedikitnya satu outcome dibandingkan skenario di ujung panah. Node persegi menunjukkan non-dominated; node lingkaran menunjukkan dominated.

Manual Cepat dan GS PID berstatus non-dominated pada seluruh setpoint. Fixed PID berstatus non-dominated pada SP20 dan SP30. Manual Presisi berstatus dominated pada seluruh setpoint karena tidak ada outcome primer di mana ia mencapai nilai terendah: durasinya selalu tertinggi, akurasinya lebih rendah dari skenario closed-loop, dan SD galat tidak pernah terkecil (lihat Tabel 4.4). Manual Cepat tetap non-dominated karena durasinya paling rendah; skenario lain tidak dapat memperbaiki outcome akurasi, overshoot, dan konsistensi tanpa menjadi lebih lambat. Status Pareto tidak menetapkan juara umum dan tidak menyatakan inferioritas statistik.

## 4.10 Outcome Tambahan: Rise Time

Rise time 10–90% mengukur waktu yang diperlukan untuk massa mencapai 90% setpoint dari 10% setpoint sebagai indikator dinamika respons sistem. Gambar 4.3 menampilkan profil rise time pada setpoint 15–30 g.

Omnibus RiseTime signifikan pada seluruh setpoint setelah koreksi Holm (Tabel 4.2). Ukuran efek epsilon_squared digunakan pada SP15–SP20, sedangkan ukuran efek yang mengakomodasi ketidakhomogenan varians digunakan pada SP25–SP30; nilai keduanya dilaporkan terpisah pada Tabel 4.2 tanpa disatukan ke dalam satu kategori verbal.

Rise time merepresentasikan fase awal respons ketika error masih besar dan massa mulai bertambah secara aktif. Pada fase ini, parameter PID yang aktif pada zona error besar, bukaan servo, dan laju aliran granular secara bersamaan memengaruhi seberapa cepat sistem mencapai 90% setpoint. Pada gain scheduling berbasis aturan, parameter yang aktif di awal proses berbeda dari yang aktif ketika sistem mendekati target, sehingga karakteristik fase pengisian awal kemungkinan berbeda dari skenario dengan parameter tetap. Rise time tidak mencerminkan keseluruhan durasi proses; interpretasi kecepatan sistem didasarkan pada Duration_s sebagai metrik utama.

## 4.11 WithinTolerance dan SettlingTime_s Kondisional

Gambar 4.4 menampilkan proporsi trial dengan galat akhir dalam toleransi ±5% (Panel A) dan settling time pada subset trial yang memenuhi kriteria toleransi tersebut (Panel B). Label n pada Panel B menunjukkan ukuran subset yang berbeda antarskenario dan antarsetpoint. Tabel 4.5 menyajikan nilai deskriptif kedua panel.

**Tabel 4.5. WithinTolerance dan SettlingTime Kondisional**

| Setpoint (g) | Skenario | Within n | Within % | Settling subset n | Settling median (s) | Settling IQR (s) |
|---|---|---|---|---|---|---|
| 15 | Manual Cepat | 3 | 30 | 3 | 2,80 | 0,90 |
| 15 | Manual Presisi | 6 | 60 | 6 | 33,80 | 17,05 |
| 15 | Fixed PID | 7 | 70 | 7 | 23,20 | 9,94 |
| 15 | GS PID | 9 | 90 | 9 | 11,06 | 4,13 |
| 20 | Manual Cepat | 4 | 40 | 4 | 8,22 | 7,88 |
| 20 | Manual Presisi | 6 | 60 | 6 | 40,89 | 3,55 |
| 20 | Fixed PID | 8 | 80 | 8 | 24,49 | 9,56 |
| 20 | GS PID | 8 | 80 | 8 | 15,97 | 5,29 |
| 25 | Manual Cepat | 3 | 30 | 3 | 9,52 | 1,55 |
| 25 | Manual Presisi | 6 | 60 | 6 | 60,53 | 26,42 |
| 25 | Fixed PID | 9 | 90 | 9 | 41,80 | 18,34 |
| 25 | GS PID | 9 | 90 | 9 | 19,07 | 14,46 |
| 30 | Manual Cepat | 4 | 40 | 4 | 21,66 | 5,49 |
| 30 | Manual Presisi | 7 | 70 | 7 | 51,36 | 9,55 |
| 30 | Fixed PID | 10 | 100 | 10 | 24,75 | 11,04 |
| 30 | GS PID | 10 | 100 | 10 | 22,94 | 4,65 |

*Settling subset n = Within n karena settling time hanya dihitung pada trial yang memenuhi toleransi ±5%.*

Proporsi WithinTolerance bervariasi antarskenario dan antarsetpoint (Tabel 4.5). Omnibus hanya signifikan pada SP25 (p_Holm=0,030240, Tabel 4.2), tetapi tidak ada pasangan yang tetap signifikan pada post-hoc setelah koreksi Holm. Kondisi ini dapat berkaitan dengan distribusi efek yang tersebar di banyak pasangan; interpretasi inferensial tetap mengacu pada hasil uji statistik. Settling time wajib dibaca bersama ukuran subset karena jumlah trial yang memenuhi toleransi berbeda antarkombinasi.

SettlingTime_s disajikan secara deskriptif saja berupa jumlah data tersedia, median, dan IQR per kelompok. Uji inferensial tidak dilakukan karena metrik ini hanya tersedia pada subset trial yang memenuhi toleransi akhir, sehingga ukuran subset berbeda antarskenario dan perbandingan langsung rentan terhadap bias seleksi. Klaim kecepatan proses didasarkan pada Duration_s sebagai metrik utama, sedangkan RiseTime_10_90_s hanya menjadi indikator respons awal tambahan. WithinTolerance menilai proporsi keberhasilan memenuhi toleransi, bukan durasi proses.

## 4.12 Kurva Respons Massa terhadap Waktu

Gambar 4.5 dan Gambar 4.6 melengkapi hasil analisis kelompok dengan memperlihatkan bentuk respons massa terhadap waktu pada trial terpilih. Kedua gambar bersifat deskriptif dan ilustratif, sedangkan kesimpulan komparatif tetap didasarkan pada analisis seluruh 160 trial final. Kurva hanya menampilkan sampel yang tercatat pada baris DATA; massa akhir pada summary tidak ditempatkan pada sumbu waktu karena timestamp pengukurannya tidak tersedia secara seragam.

Gambar 4.5 menampilkan satu trial representatif dari setiap skenario pada setpoint 20 g. Trial dipilih secara deterministik berdasarkan jumlah jarak ternormalisasi terhadap median kelompok pada AbsError_pct, MaxOvershoot_pct, Duration_s, dan RiseTime_10_90_s dengan bobot yang sama. Trial yang terpilih adalah Manual Cepat trial 5, Manual Presisi trial 2, Fixed PID trial 2, dan GS PID trial 1. Pemilihan tersebut dimaksudkan untuk menggambarkan bentuk respons yang dekat dengan pusat multivariat masing-masing kelompok, bukan untuk menampilkan trial terbaik.

Secara visual, Manual Cepat menunjukkan kenaikan massa dalam waktu paling singkat, sedangkan Manual Presisi berlangsung lebih lambat. Fixed PID dan GS PID menunjukkan respons closed-loop yang lebih bertahap. Pada trial representatif tersebut, GS PID mencapai daerah dekat setpoint lebih cepat daripada Fixed PID. Namun, satu kurva tidak digunakan untuk menyimpulkan kinerja kelompok; seluruh perbandingan tetap mengacu pada sepuluh trial pada setiap kombinasi skenario–setpoint.

Panel A Gambar 4.6 menampilkan kasus dengan MaxOvershoot_pct tertinggi di antara seluruh trial final yang memenuhi kriteria raw log lengkap, yaitu Manual Cepat pada SP15 trial 7. Panel B menampilkan kasus dengan MaxOvershoot_pct tertinggi pada kelompok GS PID yang memenuhi kriteria audit, yaitu GS PID pada SP30 trial 8. Panel A memberikan konteks terhadap kasus ekstrem global, sedangkan Panel B memperlihatkan bahwa overshoot masih dapat terjadi pada GS PID.

Kurva solid hanya merepresentasikan sampel pada baris DATA. Nilai massa akhir pada tabel ringkasan berasal dari summary firmware dan disajikan tanpa koordinat waktu. Selisih antara sampel DATA terakhir dan massa akhir tidak digunakan untuk merekonstruksi bentuk lonjakan temporal yang tidak terekam.

Pola kenaikan massa setelah periode pertambahan yang relatif rendah konsisten dengan kemungkinan pelepasan material yang sebelumnya tertahan. Namun, grafik dan rekaman video tidak digunakan untuk menyatakan bahwa overshoot sepenuhnya disebabkan oleh avalanche, bahwa PID tidak berpengaruh, atau bahwa fenomena tersebut berada di luar seluruh metode kontrol. Interpretasi yang diberikan terbatas pada hubungan temporal dan karakter fisik aliran granular yang teramati.

Rekaman video trial digunakan sebagai dokumentasi pendukung untuk mengamati perilaku mekanik selama penakaran. Video tidak menjadi dasar pemilihan trial, tidak menggantikan analisis kuantitatif, dan tidak digunakan untuk menetapkan kausalitas tunggal.

[[GAMBAR 4.5]]

[[GAMBAR 4.6]]

## 4.13 Analisis Pendukung BridgingCount

BridgingCount tidak digunakan sebagai metrik utama evaluasi kinerja kontrol, melainkan sebagai indikator pendukung untuk mendeskripsikan frekuensi gangguan aliran granular dan aktivasi mekanisme anti-bridging selama proses dispensing.

*Total event = jumlah kumulatif aktivasi mekanisme anti-bridging pada 10 trial.*

BridgingCount mencatat jumlah kejadian stagnasi aliran yang terdeteksi dan memicu mekanisme anti-bridging pada firmware. Indikator ini bukan observasi visual atas seluruh kejadian bridging fisik.

**Tabel 4.6. BridgingCount Deskriptif**

| Setpoint (g) | Skenario | n | Total event | Median | Q1 | Q3 | IQR | Min–maks | Proporsi nonzero (%) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | Manual Cepat | 10 | 3 | 0,00 | 0,00 | 0,00 | 0,00 | 0–2 | 20 |
| 15 | Manual Presisi | 10 | 29 | 3,00 | 1,50 | 3,75 | 2,25 | 1–6 | 100 |
| 15 | Fixed PID | 10 | 10 | 1,00 | 0,25 | 1,00 | 0,75 | 0–3 | 70 |
| 15 | GS PID | 10 | 3 | 0,00 | 0,00 | 0,75 | 0,75 | 0–1 | 30 |
| 20 | Manual Cepat | 10 | 2 | 0,00 | 0,00 | 0,00 | 0,00 | 0–1 | 20 |
| 20 | Manual Presisi | 10 | 44 | 3,00 | 3,00 | 4,00 | 1,00 | 1–14 | 100 |
| 20 | Fixed PID | 10 | 15 | 1,00 | 0,00 | 2,00 | 2,00 | 0–5 | 60 |
| 20 | GS PID | 10 | 7 | 1,00 | 0,25 | 1,00 | 0,75 | 0–1 | 70 |
| 25 | Manual Cepat | 10 | 0 | 0,00 | 0,00 | 0,00 | 0,00 | 0–0 | 0 |
| 25 | Manual Presisi | 10 | 61 | 6,00 | 4,25 | 7,50 | 3,25 | 3–10 | 100 |
| 25 | Fixed PID | 10 | 44 | 4,00 | 1,75 | 6,75 | 5,00 | 0–10 | 80 |
| 25 | GS PID | 10 | 4 | 0,00 | 0,00 | 1,00 | 1,00 | 0–1 | 40 |
| 30 | Manual Cepat | 10 | 7 | 0,00 | 0,00 | 1,75 | 1,75 | 0–2 | 40 |
| 30 | Manual Presisi | 10 | 85 | 7,50 | 5,25 | 11,00 | 5,75 | 4–16 | 100 |
| 30 | Fixed PID | 10 | 13 | 1,00 | 1,00 | 1,00 | 0,00 | 0–4 | 90 |
| 30 | GS PID | 10 | 9 | 1,00 | 0,00 | 1,75 | 1,75 | 0–2 | 60 |

*Total event = jumlah kumulatif aktivasi mekanisme anti-bridging pada 10 trial.*

Tabel 4.6 menampilkan statistik deskriptif bridging count per kombinasi skenario–setpoint. Manual Presisi menunjukkan aktivitas anti-bridging tertinggi pada seluruh setpoint dengan proporsi trial >0 mencapai 100% pada semua setpoint. GS PID dan Manual Cepat menunjukkan aktivitas terendah. Fixed PID menunjukkan aktivitas menengah dengan pola bervariasi antarsetpoint.

## 4.14 Sintesis Hasil dan Keterbatasan

Dibandingkan dengan Fixed PID, GS PID memiliki rerata durasi yang lebih rendah pada setiap setpoint serta mendominasi empat outcome primer pada SP15 dan SP25. Perbedaan durasi Fixed PID–GS PID signifikan pada SP20 dan SP25. Pada SP20 dan SP30, kedua pengendali menunjukkan trade-off, sehingga tidak terdapat dasar untuk menyatakan satu pengendali unggul pada seluruh outcome. Dibandingkan dengan Manual Presisi, GS PID memiliki durasi tercatat lebih rendah secara signifikan pada seluruh setpoint. Namun, perbedaan MAE antarskenario belum signifikan setelah koreksi Holm.

Manual Cepat tetap memiliki rerata durasi terendah, tetapi juga memperlihatkan kasus overshoot ekstrem global pada data final. Temuan tersebut menunjukkan bahwa kecepatan absolut tidak identik dengan kualitas kinerja keseluruhan. Kontribusi GS PID terletak pada pengurangan durasi proses closed-loop dan profil trade-off multidimensi pada kondisi tertentu, bukan sebagai bukti bahwa GS PID merupakan skenario terbaik secara universal.

Secara teknis, kontribusi penelitian ini bukan sekadar selisih nilai rata-rata antarkelompok, melainkan menunjukkan bahwa gain scheduling berbasis aturan dapat digunakan untuk mengatur karakteristik respons pada setiap fase penakaran melalui perubahan parameter sesuai zona error yang sedang aktif. Pendekatan ini memberikan fleksibilitas yang tidak dimiliki satu set parameter tetap, khususnya dalam mengatur transisi antara fase pengisian awal dan fase mendekati target. Namun, karena aturan zona berbasis persentase error tidak mencakup seluruh keadaan material, efektivitasnya tetap bergantung pada kondisi aliran aktual dan interaksi dengan mekanisme anti-bridging yang bekerja secara bersamaan.

Keterbatasan penelitian mencakup perbedaan semantik endpoint durasi antara kelompok manual dan PID; sampel terminal yang tidak selalu tercetak pada baris DATA; massa akhir yang tidak memiliki timestamp seragam; grafik trial yang bersifat ilustratif; ukuran subset SettlingTime yang berbeda; serta BridgingCount yang hanya merepresentasikan aktivitas firmware. Jenis, ukuran, kelembapan, dan karakter aliran pakan dapat memengaruhi hasil. Rekaman video hanya menjadi bukti pendukung dan tidak digunakan untuk menetapkan kausalitas tunggal. Tanpa bobot prioritas atau skor komposit yang ditetapkan sebelum analisis, hasil tidak digunakan untuk memberi rekomendasi skenario tunggal.
