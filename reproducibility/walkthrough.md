# Walkthrough Verifikasi Revisi Terbatas Bab IV

## Paket Final

1. [DOCX revisi terbatas](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/bab4_hasil_dan_pembahasan_revisi_terbatas.docx)
2. [PDF render lengkap](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/render_docx_bab4_revisi_terbatas/bab4_hasil_dan_pembahasan_revisi_terbatas.pdf)
3. [Audit DOCX terbaru](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/audit_docx_bab4_revisi_terbatas.json)
4. [Diff narasi final sebelum WithinTolerance](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/diff_narasi_revisi_terbatas_final.md)
5. [Diff narasi final termasuk WithinTolerance](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/diff_narasi_revisi_terbatas_final_withintolerance.md)
6. [Diff caption ringkas](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/diff_caption_revisi_ringkas.md)

## Perubahan Caption

- Caption Gambar 4.1 memakai `MAE%` dan `overshoot maksimum (%)`.
- Caption Gambar 4.2 memakai `antarskenario` dan menjelaskan arah panah.
- Caption Gambar 4.3–4.6 sesuai versi yang disetujui.
- Sumber revisi terisolasi: [caption_tahap5_revisi_ringkas.md](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/caption_tahap5_revisi_ringkas.md).
- Caption baseline [caption_tahap5.md](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/caption_tahap5.md) tidak berubah.

## Audit Struktur

Status generator: **PASS**.

| Pemeriksaan | Hasil |
|---|---:|
| Subbagian | 14 |
| Tabel Word | 6 |
| Gambar | 6 |
| Caption | 6 |
| Setiap caption tepat satu kali | PASS |
| Caption hanya dari sumber revisi | PASS |
| Gambar dan caption pada halaman sama | PASS |
| Gambar 4.5–4.6 pada §4.12 | PASS |
| §4.13 membahas BridgingCount | PASS |
| §4.14 memuat sintesis dan tiga paragraf keterbatasan | PASS |
| Statistik, tabel, gambar, dan penomoran berubah | Tidak |

## Audit Render

- PDF memuat 28 halaman.
- Seluruh 28 PNG diperiksa secara programatik; semua nonblank dan memiliki bounding box konten.
- Paragraf sintesis WithinTolerance muncul tepat satu kali pada halaman 28.
- Enam caption diekstrak dari PDF tepat satu kali pada halaman 3, 17, 18, 19, 23, dan 24.
- Setiap caption berada pada halaman yang sama dengan gambar terkait.
- [Audit visual programatik](file:///d:/SKRIPSI/draft/3.%20dok%20trial%20hasil/Pengambilan%20Data/rekap%20data/Laporan/Tahap5/render_docx_bab4_revisi_terbatas/audit_visual_programatik.json) menyimpan hasil per halaman.

> [!NOTE]
> Viewer raster sesi tidak mengembalikan citra contact sheet. Karena itu, klaim inspeksi mata tidak dibuat. Tujuh contact sheet exact tersedia pada direktori render sebagai `audit_final_1.jpg` sampai `audit_final_7.jpg` untuk pemeriksaan manusia. Audit otomatis tidak menemukan halaman kosong, caption terpisah, caption ganda, atau glyph yang hilang.

## SHA-256

| File | SHA-256 |
|---|---|
| DOCX revisi + WithinTolerance | `84ac629f62516000ec9491607ab889a9d467cbd7c22ec259de3e6bd8fa85d63c` |
| DOCX revisi sebelum WithinTolerance | `16f3b62084ac2f86af13678aa78bb42c9e72452a23e880df71eff9df05576275` |
| DOCX baseline | `b8b812a9be58601c45a42cb1392c2e2cb6b340308667c3025566fb15514f6643` |
| Narasi revisi + WithinTolerance | `8928d6ed623d48d09155747123643154208957f8061343552d82f1a8400f2c27` |
| Narasi baseline | `3569a8e5e217f031ad713d1e3561ff209dc6e6fa7db0ad25233369d8917ef8a9` |
| Caption revisi | `d195875af92fbc09171c2da4cfa3e43a3b2c387bd255a85af6fae4b05bce1d39` |
| Caption baseline | `1386942122a7af95994331396c9efc1a17a95c781123f04b91a7bbda882f87a2` |

## Integritas Baseline

Hash, ukuran, dan `LastWriteTimeUtc` lima baseline identik sebelum dan sesudah eksekusi:

- `caption_tahap5.md`
- `narasi_bab4_baseline_14_subbagian.md`
- `bab4_hasil_dan_pembahasan.docx`
- `audit_docx_bab4.json`
- `tahap5_generate_docx_bab4.py`

Baseline tidak ditimpa.
