import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


CSV_FILE = "depo_radari_tum_ihaleler_guvenli_v3.csv"
SUMMARY_FILE = "depo_radari_ozet.json"
LOG_FILE = "depo_radari_log.txt"
UPDATER_FILE = "depo_radari_veri_guncelle_v4.py"


def run(cmd, check=True, hide=False):
    shown = " ".join(cmd)
    if hide:
        shown = shown.replace(os.environ.get("GITHUB_TOKEN", ""), "***")
        shown = shown.replace(os.environ.get("GH_TOKEN", ""), "***")
    print(f"$ {shown}", flush=True)
    return subprocess.run(cmd, check=check, text=True)


def main():
    print("Depo Radari Render Cron basladi:", datetime.now().isoformat(), flush=True)

    if not Path(UPDATER_FILE).exists():
        raise FileNotFoundError(f"{UPDATER_FILE} bulunamadi.")

    # 1) Veriyi guncelle
    run([sys.executable, UPDATER_FILE])

    # 2) Degisiklik var mi?
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
    print("Git status:", status or "degisiklik yok", flush=True)

    if not status:
        print("Yeni degisiklik yok. Commit atilmadi.", flush=True)
        return

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "BushidoOT/depo-radari")
    branch = os.environ.get("GITHUB_BRANCH", "main")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN veya GH_TOKEN environment variable eksik. "
            "Render Cron Job Environment bolumune GitHub token ekle."
        )

    # 3) Git ayarlari
    run(["git", "config", "user.name", "depo-radari-render-bot"])
    run(["git", "config", "user.email", "depo-radari-render-bot@users.noreply.github.com"])

    # 4) Sadece veri dosyalarini ekle
    for file in [CSV_FILE, SUMMARY_FILE, LOG_FILE]:
        if Path(file).exists():
            run(["git", "add", file])

    commit_msg = "Render cron veri guncelleme"
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])

    if result.returncode == 0:
        print("Commit edilecek veri degisikligi yok.", flush=True)
        return

    run(["git", "commit", "-m", commit_msg])

    # 5) Token ile GitHub'a push
    remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"
    run(["git", "remote", "set-url", "origin", remote_url], hide=True)
    run(["git", "push", "origin", f"HEAD:{branch}"], hide=True)

    print("Veri guncellendi ve GitHub'a push edildi.", flush=True)


if __name__ == "__main__":
    main()
