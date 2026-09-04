from fractions import Fraction
import numpy as np
import json

with open("flag.txt","r") as f:
    flag = f.read().strip()

chunk_size = len(flag) // 4
chunks = [flag[i * chunk_size : (i + 1) * chunk_size] for i in range(4)] 

part1 = [ord(c) for c in chunks[0]]
part2 = [ord(c) for c in chunks[1]]
part3 = [ord(c) for c in chunks[2]]
part4 = [ord(c) for c in chunks[3]]

# Definite Integral
def calculus(data_ord): 
    n = len(data_ord)
    cipher_integrals = []

    for k in range(1, n + 1):
        val = sum(Fraction(a, i + 1) * (k ** (i + 1)) for i, a in enumerate(data_ord))
        cipher_integrals.append(float(val))

    return cipher_integrals  

key_matrix_4x4 = np.array([
        [3, 2, 1, 5],
        [4, 6, 4, 3],
        [6, 7, 6, 4],
        [2, 3, 4, 6]
    ], dtype=np.int64)

def matrix(data_ord):
    padded_data = data_ord

    P = np.array(padded_data, dtype=np.int64).reshape((4,5))

    C = np.dot(key_matrix_4x4, P)

    return C.tolist(), key_matrix_4x4.tolist()

def algebra(data_ord):
    n = len(data_ord)
    np.random.seed(1337)

    A = np.random.randint(1, 10, size=(n, n))

    while int(round(np.linalg.det(A))) == 0:
        A = np.random.randint(1, 10, size=(n,n))

    b = np.random.randint(10, 50, size=n)

    x = np.array(data_ord, dtype=np.int64)

    y = np.dot(A,x) + b

    return {
        "A": A.tolist(),
        "b": b.tolist(),
        "y": y.tolist()
    }

def statistics(data_ord):
    n = len(data_ord)
    cumulative_means = []
    running_sum = 0
    
    for k in range(1, n + 1):
        running_sum += data_ord[k - 1]
        cumulative_means.append(running_sum / k)
        
    return {
        "cumulative_mean": cumulative_means
    }

output_data = {
    "part1_calculus": calculus(part1),
    "part2_matrix": matrix(part2),
    "part3_linear_algebra": algebra(part3),
    "part4_statistics": statistics(part4)
}

with open("enc_flag.txt","w") as f:
    json.dump(output_data, f, indent=4)

print("done!")