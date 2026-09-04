"""Verifikasi: enkripsi ulang flag hasil recovery, bandingkan dengan file panitia.

enc.py menulis ke enc_flag.txt di direktori kerjanya, jadi proses re-encrypt
dijalankan di folder temporary terpisah supaya enc_flag.txt asli tidak tertimpa.

Catatan: di Windows, mode tulis teks mengubah \\n menjadi \\r\\n, sedangkan file
dari panitia memakai LF. Perbandingan byte dilakukan setelah line ending
dinormalkan, dan ditambah perbandingan struktur JSON.

Jalankan dari folder challenge: python verify.py
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import solve  # menjalankan solver, DATA dibaca dari enc_flag.txt

HERE = Path(__file__).parent
ORIG = HERE / "enc_flag.txt"

flag = "".join([solve.solve_part1(), solve.solve_part2(),
                solve.solve_part3(), solve.solve_part4()])
print(f"Flag hasil recovery : {flag}")
print(f"Panjang             : {len(flag)} karakter")

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    shutil.copy(HERE / "enc.py", td / "enc.py")
    (td / "flag.txt").write_text(flag)

    print(f"\nRe-encrypt dengan enc.py asli di folder temp ...")
    r = subprocess.run([sys.executable, "enc.py"], cwd=td,
                       capture_output=True, text=True, check=True)
    print(f"  output enc.py: {r.stdout.strip()}")

    baru = (td / "enc_flag.txt").read_bytes()

asli = ORIG.read_bytes()

# normalkan CRLF -> LF (artefak mode tulis teks di Windows, bukan beda isi)
na, nb = asli.replace(b"\r\n", b"\n"), baru.replace(b"\r\n", b"\n")

print(f"\n{'':20}{'byte':>8}  sha256 (setelah normalisasi line ending)")
print(f"{'enc_flag.txt asli':20}{len(na):>8}  {hashlib.sha256(na).hexdigest()}")
print(f"{'enc_flag.txt baru':20}{len(nb):>8}  {hashlib.sha256(nb).hexdigest()}")

sama_byte = na == nb
sama_json = json.loads(asli) == json.loads(baru)
print(f"\nIdentik byte per byte : {sama_byte}")
print(f"Identik struktur JSON : {sama_json}")

if sama_byte and sama_json:
    print("\n>>> MATCH - flag terkonfirmasi benar.")
else:
    beda = next((i for i, (a, b) in enumerate(zip(na, nb)) if a != b), min(len(na), len(nb)))
    print(f"\n>>> MISMATCH - byte pertama yang berbeda di offset {beda}")
    sys.exit(1)
