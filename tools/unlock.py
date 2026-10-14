"""Recover the readable page from the published index.html.

Usage (from the repo root):
    HUB_CODE=<class code> python3 tools/unlock.py
Writes tools/page.html (git-ignored; never commit it).
"""
import base64, os, re, pathlib, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = pathlib.Path(__file__).resolve().parent.parent
code = os.environ.get("HUB_CODE", "").strip().lower()
if not code:
    sys.exit("Set HUB_CODE to the class code.")
h = (ROOT / "index.html").read_text()
g = lambda k: re.search(k + r':(?:"([^"]+)"|(\d+))', h)
salt, iv, ct = (base64.b64decode(g(k).group(1)) for k in ("salt", "iv", "ct"))
it = int(g("iter").group(2))
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(code.encode())
plain = AESGCM(key).decrypt(iv, ct, None).decode()
prefix_end = plain.index('<meta name="robots" content="noindex, nofollow">') + len('<meta name="robots" content="noindex, nofollow">')
(ROOT / "tools" / "page.html").write_text(plain[prefix_end:])
print("tools/page.html recovered. Edit the CONTENT block, then run tools/build.py.")
