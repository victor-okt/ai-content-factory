# Pixel Office — worker antrean lokal (Windows / Linux)

**Bukan** pabrik AI otomatis. Ini antrean tugas SQLite yang tahan crash, dengan worker.
Tugas `story_outline` (Kiro) dan `quality_gate` (Zek) masih **template**, bukan AI generatif.
Belum ada ElevenLabs, model AI, atau render video. Tidak ada API berbayar, tidak ada publikasi otomatis.

## Yang sudah diuji (`test_jobqueue.py`, 20 tes)
- Tugas tersimpan di disk dan tetap ada setelah program dimatikan.
- Tugas yang tertinggal "running" setelah crash dipulihkan (diuji juga dengan `kill -9` sungguhan).
- Retry terbatas (3 kali) dengan jeda 30 detik, 2 menit, 10 menit; setelah itu ditandai gagal.
- Kunci idempotensi: `--key` yang sama tidak membuat tugas ganda.
- Empat worker serentak tidak pernah mengambil tugas yang sama.
- Berhenti dengan aman (file `STOP`, perintah `stop`, atau Ctrl+C).
- Log berputar (`runtime-data/logs/worker.log`), `status.json`, dan `report.md`.
- GitHub Actions menjalankan tes yang sama di Linux **dan Windows**.

## Windows
1. Pasang Python 3.10+ dari python.org (centang "Add Python to PATH").
2. Unduh repo sebagai ZIP, ekstrak, buka folder `office/runtime`.
3. `START_WINDOWS.bat` — uji cepat 2 tugas contoh.
4. `RUN_WORKER_WINDOWS.bat` — worker terus berjalan. `STOP_WINDOWS.bat` — menghentikannya.

File `.bat` belum pernah dijalankan manual di Windows pemilik; yang diuji otomatis adalah kode Python-nya.
Worker belum dipasang sebagai layanan: tidak berjalan sendiri saat komputer menyala.

## Perintah
```
python jobqueue.py init
python jobqueue.py enqueue --agent kiro --kind story_outline --idea "Bayangan yang Ingin Libur" --key cerita-1
python jobqueue.py worker [--until-empty] [--poll 5] [--max-jobs N]
python jobqueue.py status | report | stop
```
Data ada di `office/runtime/runtime-data/` (diabaikan git). Ganti dengan `--dir` atau `OFFICE_RUNTIME_DIR`.

## Tes
`cd office/runtime && python -m unittest -v test_jobqueue`

## Penting
File ini sengaja **bukan** `queue.py`: nama itu menimpa modul bawaan Python `queue` dan akan merusak
fitur lain (logging, threading) begitu worker bertambah fungsi.

## Langkah berikutnya
- Hubungkan story ke model AI yang disetujui pemilik, dengan batas biaya.
- Puppet Kitsune dari aset master, renderer, narasi, subtitle, FFmpeg.
- Task Scheduler Windows setelah worker terbukti andal.
- Kunci/API disimpan di environment atau OS secret, tidak pernah di repo.
