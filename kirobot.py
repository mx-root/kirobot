#!/usr/bin/env python3
"""
 ██╗  ██╗██╗██████╗  ██████╗ ██████╗  ██████╗ ████████╗
 ██║ ██╔╝██║██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝
 █████╔╝ ██║██████╔╝██║   ██║██████╔╝██║   ██║   ██║
 ██╔═██╗ ██║██╔══██╗██║   ██║██╔══██╗██║   ██║   ██║
 ██║  ██╗██║██║  ██║╚██████╔╝██████╔╝╚██████╔╝   ██║
 ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
            BOT KIRO DEV  •  GSuite → 9Router
"""
import asyncio, json, os, re, secrets, sys, time, threading, itertools, shutil, platform

# ---------- Windows: aktifkan ANSI + UTF-8 biar warna & banner jalan ----------
if os.name == "nt":
    try:
        os.system("")  # memicu VT processing di cmd
    except Exception:
        pass
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass
try:
    sys.stdout.reconfigure(encoding="utf-8")  # biar karakter box/braille aman
except Exception:
    pass

# ---------- paths (PORTABLE: semua relatif ke folder script) ----------
HERE = os.path.dirname(os.path.abspath(__file__))
GOOGLE_TXT = os.path.join(HERE, "google.txt")
USED_TXT   = os.path.join(HERE, "googleused.txt")
RESULTS    = os.path.join(HERE, "result.jsonl")

NR = "http://127.0.0.1:20128"

# ---------- venv/site-packages auto-detect (portable) ----------
def _add_local_site_packages():
    """Cari patchright di: venv di folder script, venv umum, atau site system."""
    cands = []
    # venv di sebelah script
    for vn in (".venv", "venv", "env", "farm_venv"):
        cands.append(os.path.join(HERE, vn))
        cands.append(os.path.join(os.path.dirname(HERE), vn))
    # venv home umum
    home = os.path.expanduser("~")
    for vn in ("farm_venv", ".venv", "venv"):
        cands.append(os.path.join(home, vn))
    for v in cands:
        for lib in ("lib", "Lib"):
            base = os.path.join(v, lib)
            if not os.path.isdir(base):
                continue
            for py in os.listdir(base):
                sp = os.path.join(base, py, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
    # fallback: /usr/lib/python3*/site-packages lain
_add_local_site_packages()

# cek patchright bisa ke-import; kalau belum -> AUTO-INSTALL
def _pip_install(pkgs):
    import subprocess
    base = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check"]
    for extra in ([], ["--break-system-packages"], ["--user"]):
        try:
            r = subprocess.run(base + extra + pkgs, capture_output=True, text=True, timeout=600)
            if r.returncode == 0:
                return True
        except Exception:
            pass
    return False

try:
    import patchright  # noqa
except ImportError:
    print("\n  \033[38;5;221m!\033[0m patchright belum terinstall - install otomatis...")
    ok1 = _pip_install(["patchright"])
    ok2 = _pip_install(["requests"])
    if not ok1:
        print("  \033[38;5;203m✗\033[0m gagal install. jalankan manual:")
        print("      pip install patchright requests")
        sys.exit(1)
    # muat ulang path & import
    import importlib, site
    importlib.invalidate_caches()
    try:
        site.main()
    except Exception:
        pass
    try:
        import patchright  # noqa
        print("  \033[38;5;84m✓\033[0m patchright terinstall")
    except ImportError:
        print("  \033[38;5;203m✗\033[0m patchright masih tidak bisa diimport. restart script.")
        sys.exit(1)

# pastikan browser tersedia (install chromium kalau tidak ada browser sama sekali)
try:
    import requests  # noqa
except ImportError:
    _pip_install(["requests"])
    import requests  # noqa

# ---------- browser auto-detect (portable) ----------
def find_browser():
    """Cari browser Chromium-based di OS manapun."""
    name = (platform.system() or "").lower()
    cands = [
        # Linux
        "/usr/bin/brave-browser", "/usr/bin/brave",
        "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium", "/usr/bin/chromium-browser",
        "/snap/bin/chromium", "/snap/bin/brave",
        # macOS
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        # Windows (umum)
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    for exe in ("brave-browser", "brave", "google-chrome", "chromium", "chromium-browser", "chrome"):
        w = shutil.which(exe)
        if w:
            return w
    return None

BRAVE = find_browser()   # None -> patchright pakai chromium bundled-nya

# ---------- ANSI ----------
class C:
    R="\033[0m"; B="\033[1m"; D="\033[2m"
    RED="\033[38;5;203m"; GRN="\033[38;5;84m"; YEL="\033[38;5;221m"
    BLU="\033[38;5;75m"; MAG="\033[38;5;177m"; CYN="\033[38;5;87m"
    ORG="\033[38;5;215m"; WHT="\033[38;5;255m"; GRY="\033[38;5;245m"
    BG_BL="\033[48;5;24m"; BG_GN="\033[48;5;22m"; BG_RD="\033[48;5;88m"

W = 62
def clear(): os.system("cls" if os.name=="nt" else "clear")
def line(ch="─", col=C.BLU): print(f"{col}{ch*W}{C.R}")
def _vislen(s): return len(re.sub(r'\033\[[0-9;]*m','',s))
def center(s, col="", bold=True):
    pad = max(0, (W - _vislen(s))//2)
    print(" "*pad + (C.B if bold else "") + col + s + C.R)

# Presisi: strip leading newline & trailing spaces, rata kiri, prefix global
BANNER = [
 "██╗  ██╗██╗██████╗  ██████╗ ██████╗  ██████╗ ████████╗",
 "██║ ██╔╝██║██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝",
 "█████╔╝ ██║██████╔╝██║   ██║██████╔╝██║   ██║   ██║   ",
 "██╔═██╗ ██║██╔══██╗██║   ██║██╔══██╗██║   ██║   ██║   ",
 "██║  ██╗██║██║  ██║╚██████╔╝██████╔╝╚██████╔╝   ██║   ",
 "╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   ",
]

def header():
    print()
    # hitung lebar banner utk centering presisi
    bw = max(len(x.rstrip()) for x in BANNER)
    pad = " " * max(0, (W - bw)//2)
    for ln in BANNER:
        print(pad + C.CYN + ln.rstrip() + C.R)
    center("GSuite  →  KIRO DEV  →  9Router", C.MAG, bold=False)
    line("═", C.BLU)

def ok(m):   print(f"  {C.GRN}✓{C.R} {m}")
def err(m):  print(f"  {C.RED}✗{C.R} {m}")
def info(m): print(f"  {C.BLU}›{C.R} {m}")
def warn(m): print(f"  {C.YEL}!{C.R} {m}")

# ---------- animated loader ----------
SPIN_A = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
SPIN_B = ["◐","◓","◑","◒"]
SPIN_C = ["▖","▘","▝","▗"]
BAR_CH = "█"

class Loader:
    def __init__(self, msg, color=C.CYN):
        self.msg=msg; self.color=color; self.run=False; self.t=threading.Thread(target=self._spin)
        self.t0=time.time()
    def _spin(self):
        frames=[SPIN_A, SPIN_B, SPIN_C]
        i=0
        while self.run:
            f = frames[(i//4)%3][i%len(frames[(i//4)%3])]
            el=time.time()-self.t0
            dots="."*(int(el)%4)
            sys.stdout.write(f"\r  {self.color}{f}{C.R} {self.msg}{C.D}{dots:<3}{C.R} {C.GRY}[{el:4.1f}s]{C.R}  ")
            sys.stdout.flush()
            i+=1
            time.sleep(0.08)
    def __enter__(self): self.run=True; self.t.start(); return self
    def __exit__(self,*a):
        self.run=False; self.t.join()
        sys.stdout.write("\r" + " "*W + "\r"); sys.stdout.flush()

def progress_bar(done, total, label="PROGRESS"):
    pct = done/total if total else 0
    filled = int(38*pct)
    bar = f"{C.GRN}{BAR_CH*filled}{C.GRY}{BAR_CH*(38-filled)}{C.R}"
    print(f"  {C.B}{label:<9}{C.R} {bar} {C.YEL}{done}/{total}{C.R} {C.GRY}({pct*100:5.1f}%){C.R}")

# ---------- helpers ----------
def nr_token():
    """Baca CLI token 9Router. Return None kalau 9Router belum terpasang."""
    import hashlib, pathlib
    try:
        mid=(pathlib.Path.home()/".9router/machine-id").read_text().strip()
        sec=(pathlib.Path.home()/".9router/auth/cli-secret").read_text().strip()
    except Exception:
        return None
    return hashlib.sha256((mid+"9r-cli-auth"+sec).encode()).hexdigest()[:16]

_NRTOK = None
_NR_WARNED = False
def nr_import(rt):
    """Import refresh token ke 9Router. Kalau 9Router tidak ada -> return status khusus."""
    global _NRTOK, _NR_WARNED
    import requests as rq
    if _NRTOK is None:
        _NRTOK = nr_token()
    if _NRTOK is None:
        if not _NR_WARNED:
            _NR_WARNED = True
        return 0, {"error": "9R-NOT-INSTALLED"}
    try:
        r=rq.post(f"{NR}/api/oauth/kiro/import",
            headers={"Content-Type":"application/json","x-9r-cli-token":_NRTOK},
            json={"refreshToken":rt,"region":"us-east-1"},timeout=40)
        try: return r.status_code, r.json()
        except Exception: return r.status_code, {"raw":r.text[:150]}
    except Exception as e:
        return 0, {"error": "9R-UNREACHABLE", "detail": str(e)[:120]}

def save_token(email, rt):
    """Simpan token ke tokens.txt di folder script (fallback kalau 9Router offline)."""
    p = os.path.join(HERE, "tokens.txt")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"{email}:{rt}\n")

def find_rt(cookies):
    for c in cookies:
        if c.get("value","").startswith("aorAAAAAG"): return c["value"]
    for c in cookies:
        if "refresh" in c.get("name","").lower() and len(c.get("value",""))>60: return c["value"]
    return None

def read_google_txt():
    if not os.path.exists(GOOGLE_TXT):
        err(f"File {C.B}google.txt{C.R} tidak ada di {HERE}")
        sys.exit(1)
    pairs=[]
    seen=set()
    for ln in open(GOOGLE_TXT, encoding="utf-8"):
        ln=ln.strip()
        if not ln or ln.startswith("#"): continue
        if ":" not in ln: continue
        e,p=ln.split(":",1)
        e=e.strip()
        if e in seen: continue
        seen.add(e); pairs.append((e,p.strip()))
    return pairs

def to_used(email, status):
    with open(USED_TXT,"a",encoding="utf-8") as f:
        f.write(f"{email}:{status}\n")

# ---------- core (headless patchright) ----------
async def ck(pg, labels, t=1500):
    for lab in labels:
        try:
            el=pg.get_by_role("button",name=re.compile(lab,re.I)).first
            if await el.is_visible(timeout=t): await el.click(timeout=6000); return True
        except Exception: pass
    return False

async def wait_el(pg, sels, n=30):
    for _ in range(n):
        for s in sels:
            try:
                el=pg.locator(s).first
                if await el.is_visible(timeout=600): return el
            except Exception: pass
        await pg.wait_for_timeout(350)
    return None

CONSENT = ["Saya mengerti","I understand","Continue","Lanjutkan","Allow","Izinkan","Agree","Setuju","Lanjut"]

async def run_account(pw_obj, email, password, headless=True):
    t0=time.time()
    rec={"email":email,"refresh_token":None,"connection":None,"ok":False,"secs":0,"err":None}
    br=None
    try:
        launch_kw = dict(headless=headless,
            args=["--no-sandbox","--disable-blink-features=AutomationControlled","--disable-dev-shm-usage"])
        if BRAVE and os.path.exists(BRAVE):
            launch_kw["executable_path"] = BRAVE
        br=await pw_obj.chromium.launch(**launch_kw)
        ctx=await br.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
            viewport={"width":1920,"height":1080}, locale="id-ID", timezone_id="Asia/Jakarta")
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        pg=await ctx.new_page()

        await pg.goto("https://app.kiro.dev/signin",timeout=60000,wait_until="domcontentloaded")
        await pg.get_by_role("button",name=re.compile("Google",re.I)).first.click(timeout=30000)

        e=await wait_el(pg,['input[type="email"]','#identifierId','input[name="identifier"]'],30)
        if not e: raise RuntimeError("Google email field tidak muncul")
        await e.fill(email); await pg.wait_for_timeout(250)
        if not await ck(pg,["Berikutnya","Next"]): await pg.keyboard.press("Enter")

        p_=await wait_el(pg,['input[type="password"]','input[name="Passwd"]'],25)
        if not p_: raise RuntimeError("Google password field tidak muncul")
        await p_.fill(password); await pg.wait_for_timeout(250)
        if not await ck(pg,["Berikutnya","Next"]): await pg.keyboard.press("Enter")

        for _ in range(30):
            if "app.kiro.dev" in pg.url and "signin" not in pg.url: break
            await ck(pg,CONSENT,1200); await pg.wait_for_timeout(800)
        for _ in range(18):
            if "app.kiro.dev" in pg.url: break
            await pg.wait_for_timeout(700)
        await pg.wait_for_timeout(2200)

        rt=None
        for _ in range(15):
            rt=find_rt(await ctx.cookies())
            if rt: break
            await pg.wait_for_timeout(700)
        if not rt: raise RuntimeError("RefreshToken tidak ditemukan di cookie")

        rec["refresh_token"]=rt
        st, j = nr_import(rt)
        if st == 0:  # 9Router tidak ada / unreachable -> simpan token ke file
            save_token(email, rt)
            rec["ok"] = True                       # token BERHASIL didapat
            rec["err"] = "TOKEN-SAVED (9Router offline)"
            rec["connection"] = None
        else:
            rec["connection"]=j.get("connection",{}).get("id") if isinstance(j,dict) else None
            rec["ok"]=(st==200)
            if not rec["ok"]: rec["err"]=f"import HTTP {st}"
    except Exception as e:
        rec["err"]=str(e)[:160]
    finally:
        try:
            if br: await br.close()
        except Exception: pass
    rec["secs"]=round(time.time()-t0,1)
    return rec

# ---------- interactive mode ----------
async def interactive():
    clear(); header()

    # detect files
    pairs = read_google_txt()
    used = set()
    if os.path.exists(USED_TXT):
        for ln in open(USED_TXT,encoding="utf-8"):
            if ":" in ln: used.add(ln.split(":",1)[0].strip())

    avail = [(e,p) for (e,p) in pairs if e not in used]
    print()
    ok(f"google.txt        : {C.B}{len(pairs)}{C.R} akun")
    info(f"googleused.txt    : {C.B}{len(used)}{C.R} akun (sudah dipakai)")
    ok(f"Belum dipakai     : {C.B}{len(avail)}{C.R} akun")

    # cek 9Router (kalau offline, token tetap disimpan ke tokens.txt)
    _nr_ok = False
    try:
        import requests as _rq
        _rq.get(f"{NR}/api/auth/status", timeout=4)
        _nr_ok = True
    except Exception:
        pass
    if _nr_ok:
        ok(f"9Router           : {C.GRN}ONLINE{C.R} {C.GRY}{NR}{C.R}")
    else:
        warn(f"9Router           : {C.YEL}OFFLINE{C.R} — token akan disimpan ke {C.B}tokens.txt{C.R}")
    print()

    if not avail:
        warn("Semua akun di google.txt sudah terpakai.")
        return

    # prompt sederhana (headless selalu ON)
    try:
        jn = input(f"  {C.CYN}▸{C.R} Jumlah akun {C.GRY}[{len(avail)}]{C.R}: ").strip()
        n = int(jn) if jn.isdigit() else len(avail)
    except Exception: n = len(avail)
    n = max(1, min(n, len(avail)))
    headless = True

    todo = avail[:n]
    print()
    line("─", C.GRY)
    print(f"  {C.B}MULAI:{C.R} {n} akun  •  browser={'HEADLESS' if headless else 'HEADFUL'}  •  target {C.MAG}9Router{C.R}")
    line("─", C.GRY); print()

    results=[]; okc=0; failc=0; t_start=time.time()
    async with async_playwright() as p:
        for i,(email,pw) in enumerate(todo,1):
            print(f"  {C.B}{C.BLU}[{i}/{n}]{C.R} {C.WHT}{email}{C.R}")
            with Loader(f"Login Google + ambil token", C.CYN) as L:
                rec=await run_account(p, email, pw, headless=headless)
            if rec["ok"]:
                okc+=1
                ok(f"IMPORT {C.GRN}200{C.R}  {C.GRY}conn={rec['connection']}{C.R}  {C.GRY}{rec['secs']}s{C.R}")
                to_used(email, "OK")
            else:
                failc+=1
                err(f"GAGAL  {C.GRY}{rec.get('err')}{C.R}  {C.GRY}{rec['secs']}s{C.R}")
                to_used(email, "FAIL")
            results.append(rec)
            print()
            progress_bar(i, n, "PROGRESS")
            print()

    dur=time.time()-t_start
    line("═", C.GRN)
    center("◈ HASIL ◈", C.GRN)
    line("─", C.GRN)
    print(f"  {C.GRN}✓ Sukses : {okc}{C.R}")
    print(f"  {C.RED}✗ Gagal  : {failc}{C.R}")
    print(f"  {C.CYN}⏱ Total  : {dur:.1f}s  ({dur/max(1,n):.1f}s/akun){C.R}")
    print(f"  {C.GRY}→ googleused.txt diupdate{C.R}")
    print(f"  {C.GRY}→ result.jsonl disimpan{C.R}")
    line("═", C.GRN)
    with open(RESULTS,"a",encoding="utf-8") as f:
        for r in results: f.write(json.dumps(r)+"\n")

# ---------- entry ----------
from patchright.async_api import async_playwright

def _ensure_chromium():
    """Kalau tidak ada browser Chromium-based sama sekali -> install chromium patchright."""
    if find_browser():
        return
    import subprocess
    print("  \033[38;5;221m!\033[0m tidak ada browser Chromium - download chromium (sekali saja)...")
    try:
        subprocess.run([sys.executable, "-m", "patchright", "install", "chromium"],
                       timeout=1200)
    except Exception as e:
        print(f"  \033[38;5;203m✗\033[0m gagal download chromium: {e}")

def main():
    try:
        _ensure_chromium()
        asyncio.run(interactive())
    except KeyboardInterrupt:
        print(f"\n  {C.YEL}!{C.R} Dihentikan user.")
    except Exception as e:
        print(f"\n  {C.RED}✗ Error: {e}{C.R}")

if __name__ == "__main__":
    main()
