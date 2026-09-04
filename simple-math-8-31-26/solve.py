"""Solver lengkap untuk challenge 'math' (C2SI).

Jalankan: python solve.py
"""
import json
from fractions import Fraction

DATA = json.load(open("enc_flag.txt"))
LO, HI = 32, 126  # rentang ASCII printable


def rref(M, ncols_rhs):
    """Gauss-Jordan eksak (Fraction). M = matriks augmented."""
    n = len(M)
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0)
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                fct = M[r][c]
                M[r] = [M[r][j] - fct * M[c][j] for j in range(n + ncols_rhs)]
    return M


# ---------------- Part 1: integral tentu (Vandermonde + DFS pruning) -------
def solve_part1():
    f = DATA["part1_calculus"]
    n = len(f)
    M = [[Fraction(k ** (i + 1), i + 1) for i in range(n)] for k in range(1, n + 1)]
    F = [Fraction(v) for v in f]                       # float -> rasional eksak
    TOL = [abs(Fraction(v)) / 2 ** 50 + 1 for v in f]  # toleransi galat float64

    # S[k][j] = sum_{i<j} M[k][i]
    S = [[Fraction(0)] * (n + 1) for _ in range(n)]
    for k in range(n):
        for j in range(1, n + 1):
            S[k][j] = S[k][j - 1] + M[k][j - 1]

    sols, cur = [], [0] * n

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

    dfs(n, F[:])
    assert len(sols) == 1, sols
    return "".join(map(chr, sols[0]))


# ---------------- Part 2: C = K . P ---------------------------------------
def solve_part2():
    C, K = DATA["part2_matrix"]
    M = [[Fraction(v) for v in K[i]] + [Fraction(v) for v in C[i]] for i in range(4)]
    M = rref(M, 5)
    return "".join(chr(int(M[i][4 + j])) for i in range(4) for j in range(5))


# ---------------- Part 3: y = A.x + b -------------------------------------
def solve_part3():
    P = DATA["part3_linear_algebra"]
    A, b, y = P["A"], P["b"], P["y"]
    n = len(y)
    M = [[Fraction(v) for v in A[i]] + [Fraction(y[i] - b[i])] for i in range(n)]
    M = rref(M, 1)
    return "".join(chr(int(M[i][n])) for i in range(n))


# ---------------- Part 4: rata-rata kumulatif -----------------------------
def solve_part4():
    cm = DATA["part4_statistics"]["cumulative_mean"]
    out, prev = [], 0
    for k, m in enumerate(cm, 1):
        s = round(m * k)
        out.append(s - prev)
        prev = s
    return "".join(map(chr, out))


if __name__ == "__main__":
    parts = [solve_part1(), solve_part2(), solve_part3(), solve_part4()]
    for i, p in enumerate(parts, 1):
        print(f"part{i}: {p}")
    print("\nFLAG:", "".join(parts))
