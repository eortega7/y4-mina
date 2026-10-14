"""Encrypt tools/page.html with the class code and write index.html.

Usage (from the repo root):
    HUB_CODE=<class code> python3 tools/build.py

The salt is read from the published index.html so parents who already
entered the code stay unlocked. page.html is never committed.
"""
import base64, os, re, pathlib, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
ITER = 600_000

code = os.environ.get("HUB_CODE", "").strip().lower()
if not code:
    sys.exit("Set HUB_CODE to the class code.")

index = ROOT / "index.html"
m = re.search(r'salt:"([^"]+)"', index.read_text()) if index.exists() else None
salt = base64.b64decode(m.group(1)) if m else os.urandom(16)

key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(code.encode())
iv = os.urandom(12)
head = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<meta name="robots" content="noindex, nofollow">')
plain = head + (TOOLS / "page.html").read_text()
ct = AESGCM(key).encrypt(iv, plain.encode("utf-8"), None)

b64 = lambda b: base64.b64encode(b).decode()
out = ((TOOLS / "wrapper.html").read_text()
       .replace("__SALT__", b64(salt)).replace("__IV__", b64(iv))
       .replace("__CT__", b64(ct)).replace("__ITER__", str(ITER)))
index.write_text(out)
(ROOT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")

# Self-check: the new file must open with the same code.
chk = re.search(r'ct:"([^"]+)"', out).group(1)
AESGCM(key).decrypt(iv, base64.b64decode(chk), None)
print(f"index.html written ({len(out):,} bytes), opens with the class code.")
