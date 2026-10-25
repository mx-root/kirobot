<h1 align="center">🤖 BOT KIRO DEV</h1>

<div align="center">

**Auto-register KIRO DEV via GSuite (Google Workspace) → auto-import refresh token ke 9Router**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/Status-Working-brightgreen)

</div>

---

## ✨ Fitur

- 🚀 **Auto-register** akun KIRO DEV lewat Google Sign-In (GSuite / Workspace)
- 🔗 **Auto-import** refresh token ke 9Router (`/api/oauth/kiro/import`)
- 🎨 **Interactive UI** — banner warna, loader animasi, progress bar
- 🕶️ **Headless** — browser jalan di background, gak ganggu
- 📦 **Zero-setup** — patchright, requests, chromium auto-install
- 💾 **Auto-resume** — akun yang sudah dipakai otomatis di-skip
- 🌍 **Cross-platform** — Windows, Linux, macOS
- 🛡️ **Graceful fallback** — 9Router offline? token tetap disimpan

---

## 📋 Requirement

| Item | Keterangan |
|------|------------|
| **Python 3.8+** | ⚠️ satu-satunya yang harus diinstall manual |
| **Internet** | login Google + download dependency (sekali saja) |
| **9Router** | jalan di `127.0.0.1:20128` (opsional — lihat catatan) |

> Semua dependency lain (**patchright**, **requests**, **chromium**) di-install otomatis saat pertama kali dijalankan.

---

## 🚀 Cara Pakai

### 1. Install Python

**Windows** — [python.org](https://python.org) → centang **"Add Python to PATH"**

**Ubuntu / Debian**
```bash
sudo apt install python3 python3-pip
```

**macOS**
```bash
brew install python3
```

### 2. Siapkan akun

Edit `google.txt` — format `email:password`, satu akun per baris:

```
nama@domain.com:password
nama2@domain.com:password
nama3@domain.com:password
```

### 3. Jalankan

```bash
python kirobot.py      # Windows
python3 kirobot.py     # Linux / macOS
```

```
    ██╗  ██╗██╗██████╗  ██████╗ ██████╗  ██████╗ ████████╗
    ██║ ██╔╝██║██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝
    █████╔╝ ██║██████╔╝██║   ██║██████╔╝██║   ██║   ██║
    ██╔═██╗ ██║██╔══██╗██║   ██║██╔══██╗██║   ██║   ██║
    ██║  ██╗██║██║  ██║╚██████╔╝██████╔╝╚██████╔╝   ██║
    ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
               GSuite  →  KIRO DEV  →  9Router
══════════════════════════════════════════════════════════════

  ✓ google.txt        : 10 akun
  › googleused.txt    : 0 akun (sudah dipakai)
  ✓ Belum dipakai     : 10 akun
  ✓ 9Router           : ONLINE http://127.0.0.1:20128

  ▸ Jumlah akun [10]:
──────────────────────────────────────────────────────────────
  MULAI: 10 akun  •  browser=HEADLESS  •  target 9Router
──────────────────────────────────────────────────────────────

  [1/10] nama@domain.com
  ✓ IMPORT 200  conn=487cea38-9c34-4f9e-ad07-c62ec480de44  16.1s

  PROGRESS  ██████████████████████████████████████ 10/10 (100.0%)
```

Ketik jumlah akun (Enter = semua), lalu tunggu. Selesai. ✅

---

## 📁 Struktur File

```
kirobot/
├── kirobot.py          # script utama — jalankan ini
├── google.txt          # input akun (email:password)
├── README.md           # dokumen ini
├── googleused.txt      # [auto] daftar akun terpakai
├── result.jsonl        # [auto] detail hasil (token, conn id, timing)
└── token.txt           # [auto] refresh token (kalau 9Router offline)
```

> Output selalu dibuat di **folder yang sama** dengan script — portable, bisa dipindah ke mana saja.

---

## 🔧 Konfigurasi

| Variabel | Default | Keterangan |
|----------|---------|------------|
| `NR` | `http://127.0.0.1:20128` | endpoint 9Router |
| `GOOGLE_TXT` | `./google.txt` | file input akun |
| `BRAVE` | auto-detect | browser Chromium-based |

9Router jalan di host/port lain? Edit baris ini di `kirobot.py`:

```python
NR = "http://127.0.0.1:20128"
```

---

## ❓ Catatan & Troubleshooting

**Akun gagal?**
- Jalankan ulang script — akun gagal **tidak** masuk `googleused.txt`
- Atau hapus barisnya dari `googleused.txt` untuk retry

**9Router offline?**
- Script tidak crash — token tetap disimpan ke `token.txt`
- Import manual nanti pakai token tersebut

**Windows SmartScreen warning?**
- Normal saat pertama install / download chromium

**Proxy?**
- Jalur GSuite → 9Router **tidak butuh proxy**

**Patchright tidak terinstall?**
```bash
pip install patchright requests
patchright install chromium
```

---

## 🔬 Cara Kerja

```
google.txt (email:password)
        │
        ▼
[1] Buka app.kiro.dev/signin
[2] Klik "Google Sign in"
[3] Isi email + password Google
[4] Handle consent (workspace ToS)
[5] Landing app.kiro.dev/home
[6] Baca cookie RefreshToken (aorAAAAAG...)
        │
        ▼
[7] POST /api/oauth/kiro/import  →  9Router
        │
        ▼
googleused.txt + result.jsonl
```

---

## ⚖️ Disclaimer

Dokumen & tool ini dibuat untuk **keperluan riset keamanan dan pengujian otomatisasi**.
Pengguna bertanggung jawab penuh atas kepatuhan terhadap syarat layanan (ToS) platform
terkait dan hukum yang berlaku di wilayahnya masing-masing.

---

<div align="center">

**Made with 🖤 by [mx-root](https://github.com/mx-root)**

</div>
