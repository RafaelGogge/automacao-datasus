import os
import time
import socket
import subprocess
from playwright.sync_api import sync_playwright
import pyperclip
import sys

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

URLS = [
    "http://sia.datasus.gov.br/versao/versao.php",
    "http://sia.datasus.gov.br/versao/listar_ftp_apac.php",
    "http://sia.datasus.gov.br/versao/listar_ftp_bpa.php",
    "http://sia.datasus.gov.br/versao/listar_ftp_raas.php",
    "http://sia.datasus.gov.br/versao/listar_ftp_sia.php"
]

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEBUG_PORT = 9222


def aguardar_porta(host="127.0.0.1", port=DEBUG_PORT, timeout=15):
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def verificar_pagina(page):
    if page.is_closed():
        sys.exit(1)


def pressionar(page, tecla):
    verificar_pagina(page)
    try:
        page.keyboard.press(tecla)
    except Exception:
        sys.exit(1)


# ──────────────────────────────────────────────
# ETAPA 1: Fechar Edge aberto e reabrir com debug
# ──────────────────────────────────────────────

subprocess.call(
    ["taskkill", "/F", "/IM", "msedge.exe"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(1.5)

subprocess.Popen([
    EDGE_PATH,
    f"--remote-debugging-port={DEBUG_PORT}",
    "--no-first-run",
    "--no-default-browser-check"
])

if not aguardar_porta():
    sys.exit(1)

# ──────────────────────────────────────────────
# ETAPA 2: Playwright conecta ao Edge aberto
# ──────────────────────────────────────────────

with sync_playwright() as p:

    browser = p.chromium.connect_over_cdp(
        f"http://127.0.0.1:{DEBUG_PORT}",
        slow_mo=50
    )

    context = browser.contexts[0]
    page = context.new_page()

    page.goto("edge://settings/defaultBrowser")
    page.wait_for_timeout(100)
    verificar_pagina(page)

    try:
        page.locator('fluent-menu-button[aria-haspopup="menu"]').click()
    except Exception:
        sys.exit(1)

    page.wait_for_timeout(100)

    pressionar(page, "ArrowUp")
    page.wait_for_timeout(100)
    pressionar(page, "Enter")
    page.wait_for_timeout(100)

    pressionar(page, "Tab")
    page.wait_for_timeout(100)
    pressionar(page, "Tab")
    page.wait_for_timeout(100)
    pressionar(page, "Enter")
    page.wait_for_timeout(100)

    for indice, url in enumerate(URLS, start=1):
        verificar_pagina(page)

        pressionar(page, "Tab")
        page.wait_for_timeout(100)

        pyperclip.copy(url)

        try:
            page.keyboard.press("Control+V")
        except Exception:
            sys.exit(1)

        page.wait_for_timeout(100)

        pressionar(page, "Tab")
        page.wait_for_timeout(100)
        pressionar(page, "Tab")
        page.wait_for_timeout(100)
        pressionar(page, "Enter")
        page.wait_for_timeout(100)

        if indice < len(URLS):
            verificar_pagina(page)
            pressionar(page, "Enter")
            page.wait_for_timeout(100)

    verificar_pagina(page)

    try:
        page.keyboard.press("Shift+Tab")
    except Exception:
        sys.exit(1)

    page.wait_for_timeout(100)
    pressionar(page, "Enter")

    input("\nPressione ENTER para fechar...")
    browser.close()
