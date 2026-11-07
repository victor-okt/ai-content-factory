# Motion Video — prototype 30 detik

Prototipe Remotion untuk AI Content Factory. Ini **animasi 2D berbasis kode**, bukan generator video AI sinematik.

## Cara mencoba (Windows / macOS / Linux)

Prasyarat: Node.js 20+ dan koneksi internet saat instalasi.

```bash
cd motion-video
npm install
npm run studio
```

Pilih komposisi **HorrorShort** untuk melihat preview. Untuk ekspor:

```bash
npm run render
```

Hasil: `motion-video/out/horror-short.mp4` (30 detik, 1080x1920, 30 fps).

## Status dan keterbatasan

- Lima adegan animasi dan subtitle statis, total 30 detik.
- Belum ada audio narator, TTS, sinkronisasi per kata, AI generatif, integrasi dengan pipeline Python, atau upload TikTok.
- Belum ada biaya API; rendering memakai perangkat sendiri. Dependensi npm dan Chromium perlu diunduh.
- Perintah `/motion-video` belum dihubungkan dengan chatbot.
- Belum diverifikasi lewat CI atau rendering aktual. Jangan anggap siap produksi sampai diuji.

Ini dibuat sebagai jalur eksperimen terpisah agar tidak mengubah pipeline atau Credit Guard yang ada.
