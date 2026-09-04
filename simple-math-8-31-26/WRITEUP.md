# Writeup — Crypto: "Math" (C2SI)

**Flag:** `C2SI{e4sy_m4th_w3lc0m3_t0_ctf_f0r_n3w_m3mber_4t_SMK_Immanuel_Pontianak_G00DLUCK}`

## File

| File | Isi |
|---|---|
| `enc.py` | Encoder yang diberikan panitia |
| `enc_flag.txt` | Output JSON, satu-satunya data yang dipegang solver |
| `solve.py` | Solver lengkap keempat part |
| `naive_fail.py` | Demo kenapa Part 1 tidak bisa di-solve langsung dengan numpy |
| `verify.py` | Re-encrypt flag hasil recovery, bandingkan dengan file panitia |

```
python solve.py       # cetak flag
python naive_fail.py  # demo kegagalan solve langsung
python verify.py      # verifikasi end-to-end
```

## 1. Analisis

`enc.py` memotong flag (80 karakter) jadi 4 chunk @20 karakter, lalu tiap chunk di-encode dengan operasi matematika berbeda:

```python
chunk_size = len(flag) // 4
chunks = [flag[i * chunk_size : (i + 1) * chunk_size] for i in range(4)]
```

Semua operasinya **linear dan invertible** — tidak ada key rahasia, tidak ada operasi satu arah. Jadi tiap part cukup dibalik.

| Part | Operasi | Cara balik |
|---|---|---|
| 1 | Integral tentu polinomial | Sistem linear tipe Vandermonde (ill-conditioned) → DFS + interval pruning |
| 2 | Perkalian matriks `C = K·P`, `K` diberikan | `P = K⁻¹·C` |
| 3 | `y = A·x + b`, `A` & `b` diberikan | Solve `A·x = y − b` |
| 4 | Rata-rata kumulatif | Selisih dari sum kumulatif |

Karena `A` dan `b` dibangkitkan dengan `np.random.seed(1337)` yang fixed **dan** ikut ditulis ke output, part 3 tidak menyimpan rahasia apa pun.

## 2. Part 4 — Cumulative Mean

`mean[k] = (a₀+…+a_k)/(k+1)`. Kalikan balik jadi sum kumulatif, lalu selisihkan:

```python
def solve_part4():
    cm = DATA["part4_statistics"]["cumulative_mean"]
    out, prev = [], 0
    for k, m in enumerate(cm, 1):
        s = round(m * k)
        out.append(s - prev)
        prev = s
    return "".join(map(chr, out))
```

→ `_Pontianak_G00DLUCK}`

## 3. Part 3 — Linear Algebra

`y = A·x + b` dengan `A` (20×20) dan `b` diketahui, jadi `x = A⁻¹(y − b)`. Solve pakai Gauss-Jordan dengan `Fraction`, bukan float, supaya hasilnya integer bersih tanpa galat pembulatan:

```python
def solve_part3():
    P = DATA["part3_linear_algebra"]
    A, b, y = P["A"], P["b"], P["y"]
    n = len(y)
    M = [[Fraction(v) for v in A[i]] + [Fraction(y[i] - b[i])] for i in range(n)]
    M = rref(M, 1)
    return "".join(chr(int(M[i][n])) for i in range(n))
```

→ `mber_4t_SMK_Immanuel`

## 4. Part 2 — Matrix

Plaintext di-reshape jadi `P` (4×5), dikali key `K` (4×4) yang **ikut dibocorkan** di `enc_flag.txt`. Solve `K·P = C` dengan rutin eksak yang sama:

```python
def solve_part2():
    C, K = DATA["part2_matrix"]
    M = [[Fraction(v) for v in K[i]] + [Fraction(v) for v in C[i]] for i in range(4)]
    M = rref(M, 5)
    return "".join(chr(int(M[i][4 + j])) for i in range(4) for j in range(5))
```

→ `m3_t0_ctf_f0r_n3w_m3`

## 5. Part 1 — Calculus (bagian menarik)

Inti encoder-nya:

```python
val = sum(Fraction(a, i + 1) * (k ** (i + 1)) for i, a in enumerate(data_ord))
```

Ini adalah integral tentu dari polinomial `p(x) = Σ aᵢ·xⁱ` dari `0` sampai `k`:

$$V_k=\int_0^k p(x)\,dx=\sum_{i=0}^{19}\frac{a_i\,k^{i+1}}{i+1},\qquad k=1..20$$

20 persamaan, 20 unknown → matriks `M[k][i] = k^(i+1)/(i+1)` yang secara teori invertible.

### Kenapa solve langsung gagal

Output disimpan sebagai `float` (`float(val)`). Matriksnya bertipe Vandermonde dengan condition number ~10²⁶, sedangkan float64 cuma punya ~16 digit signifikan — galat pembulatan saat enkripsi diperbesar jauh melampaui nilai yang dicari:

```
$ python naive_fail.py
Ukuran sistem      : 20 persamaan, 20 unknown
Condition number M : 4.679e+26
Presisi float64    : ~16 digit signifikan

Hasil np.linalg.solve (seharusnya integer di rentang 32-126):
[ 5.837e+14 -4.094e+15  9.379e+15 -1.122e+16  8.385e+15 -4.286e+15  1.583e+15 -4.380e+14  9.284e+13
 -1.531e+13  1.983e+12 -2.025e+11  1.628e+10 -1.025e+09  4.990e+07 -1.839e+06  4.965e+04 -8.140e+02
  1.096e+02  4.794e+01]

Dipaksa jadi karakter:
'??????????????????n0'

Hanya 2/20 koefisien yang jatuh di rentang ASCII printable.
=> solve langsung GAGAL, perlu pendekatan lain (DFS + interval pruning).
```

Kegagalannya bukan acak: dua nilai terakhir (`47.94` dan `109.6`, indeks 19 dan 18) masih dekat ke nilai asli 48 (`'0'`) dan 99 (`'c'`), karena bobot suku berindeks tinggi dominan. Sisanya hancur total.

### Solusi: constraint ASCII + DFS

Ada satu constraint yang belum dipakai sama sekali — tiap `aᵢ` pasti **ASCII printable (32–126)**. Ini mengubah masalah numerik yang ill-conditioned jadi search problem yang bisa di-prune habis.

DFS dari koefisien tertinggi (`a₁₉`) ke terendah, karena pada `k=20` bobot `20^(i+1)/(i+1)` bikin suku indeks tinggi mendominasi sehingga rentang kandidatnya paling sempit. Di tiap level, untuk setiap persamaan `k`:

```
R_k = V_k − (kontribusi koefisien yang sudah dipilih)
S   = Σ_{i<j} M[k][i]                      (bobot koefisien yang belum dipilih)
sisa kontribusi ∈ [32·S, 126·S]
⇒  a_j ∈ [ (R_k − 126·S − tol)/M[k][j] , (R_k − 32·S + tol)/M[k][j] ]
```

Rentang dari 20 persamaan diinterseksikan, biasanya tersisa 0–2 kandidat per level:

```python
def dfs(j, R):
    if j == 0:
        if all(abs(R[k]) <= TOL[k] for k in range(n)):
            sols.append(list(cur))
        return
    lo, hi = LO, HI
    for k in range(n):
        c = M[k][j - 1]
        a_lo = (R[k] - HI * S[k][j - 1] - TOL[k]) / c
        a_hi = (R[k] - LO * S[k][j - 1] + TOL[k]) / c
        lo = max(lo, -(-a_lo.numerator // a_lo.denominator))  # ceil
        hi = min(hi, a_hi.numerator // a_hi.denominator)      # floor
        if lo > hi:
            return
    for a in range(lo, hi + 1):
        cur[j - 1] = a
        dfs(j - 1, [R[k] - a * M[k][j - 1] for k in range(n)])
```

Semua aritmetika pakai `Fraction` (eksak), dengan toleransi `tol = |V_k| / 2⁵⁰` untuk menampung galat pembulatan float64 yang sudah terlanjur terjadi saat enkripsi.

Hasil: **32.802 node, solusi unik** dalam beberapa detik.

→ `C2SI{e4sy_m4th_w3lc0`

## 6. Gabung & Verifikasi

```
$ python solve.py
part1: C2SI{e4sy_m4th_w3lc0
part2: m3_t0_ctf_f0r_n3w_m3
part3: mber_4t_SMK_Immanuel
part4: _Pontianak_G00DLUCK}

FLAG: C2SI{e4sy_m4th_w3lc0m3_t0_ctf_f0r_n3w_m3mber_4t_SMK_Immanuel_Pontianak_G00DLUCK}
```

`verify.py` mengenkripsi ulang flag hasil recovery dengan `enc.py` asli, lalu membandingkannya dengan file panitia. Re-encrypt dijalankan di folder temporary karena `enc.py` menulis ke `enc_flag.txt` di direktori kerjanya — kalau tidak, file asli ketimpa:

```
$ python verify.py
Flag hasil recovery : C2SI{e4sy_m4th_w3lc0m3_t0_ctf_f0r_n3w_m3mber_4t_SMK_Immanuel_Pontianak_G00DLUCK}
Panjang             : 80 karakter

Re-encrypt dengan enc.py asli di folder temp ...
  output enc.py: done!

                        byte  sha256 (setelah normalisasi line ending)
enc_flag.txt asli      11197  88ad85d3e6a443015ac8c395ae6ea29ea705e489a523c279dca84c9ef7724f56
enc_flag.txt baru      11197  88ad85d3e6a443015ac8c395ae6ea29ea705e489a523c279dca84c9ef7724f56

Identik byte per byte : True
Identik struktur JSON : True

>>> MATCH - flag terkonfirmasi benar.
```

Catatan: di Windows mode tulis teks mengubah `\n` jadi `\r\n` sedangkan file panitia pakai LF (selisih persis 593 byte = jumlah baris JSON), jadi byte dibandingkan setelah line ending dinormalkan, plus pengecekan kedua lewat `json.loads()`.

## Flag

```
C2SI{e4sy_m4th_w3lc0m3_t0_ctf_f0r_n3w_m3mber_4t_SMK_Immanuel_Pontianak_G00DLUCK}
```

## Takeaway

- Encoding matematis linear ≠ enkripsi. Kalau key ikut dikirim (part 2 & 3), itu cuma encoding reversible.
- Menyimpan hasil sebagai `float` memang membocorkan lebih sedikit info daripada yang dikira author, tapi **struktur plaintext** (ASCII printable) selalu jadi constraint tambahan yang cukup untuk menutup gap presisi itu.
