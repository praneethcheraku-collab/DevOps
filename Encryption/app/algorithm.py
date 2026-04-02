import random
from sympy import mod_inverse, isprime
from math import gcd

# Global caches to allow symbolic_power to access the keys for simulation
public_key_cache = None
private_key_cache = None

# --- Core Functions ---

def generate_prime(bits=2048):
    """Generates a random large prime number."""
    while True:
        prime = random.getrandbits(bits)
        # Ensure the number is large enough and odd
        prime |= (1 << (bits - 1)) | 1
        if isprime(prime):
            return prime

def generate_symbolic_2plithogenic_number():
    """Generates components (x0, x1, x2) for a 2-plithogenic number."""
    x0, x1, x2 = random.randint(10, 100), random.randint(1, 10), random.randint(1, 10)
    return (x0, x1, x2)

def symbolic_product(X, Y):
    """Computes the 2-plithogenic product X * Y where i^2=i, j^2=j, i*j=j."""
    x0, x1, x2 = X
    y0, y1, y2 = Y
    
    n0 = x0 * y0
    n1 = x0 * y1 + x1 * y0 + x1 * y1
    n2 = x0 * y2 + x2 * y0 + x1 * y2 + x2 * y1 + x2 * y2 
    
    return (n0, n1, n2)

def symbolic_euler(N):
    """Simplified Euler's function for the demo."""
    n0, n1, n2 = N
    t0 = n0 - 1
    t1 = n1 - 1
    t2 = n2 - 1
    return (t0, t1, t2)

def generate_keys():
    """Generates public and private keys (e, N) and (d, N)."""
    global public_key_cache, private_key_cache
    
    p = generate_prime(bits=64) 
    q = generate_prime(bits=64)

    X = generate_symbolic_2plithogenic_number()
    Y = generate_symbolic_2plithogenic_number()

    N = symbolic_product(X, Y)
    phi_N = symbolic_euler(N)

    # Use a fixed large prime offset for the encryption simulation factor
    SIM_FACTOR = 1000000007 

    # Choose public exponent e such that gcd(e, φ(N)[0]) = 1
    e = random.randint(3, phi_N[0] - 1)
    while gcd(e, phi_N[0]) != 1 or gcd(e, SIM_FACTOR) != 1: # Ensure e and SIM_FACTOR are coprime
        e = random.randint(3, phi_N[0] - 1)

    # Compute private exponent d
    d = mod_inverse(e, phi_N[0])
    
    public_key = (e, N)
    private_key = (d, N)
    
    # Store keys globally for the symbolic_power function to use in its simulation
    public_key_cache = public_key
    private_key_cache = private_key
    
    return public_key, private_key

def symbolic_power(base, exponent, modulus_N):
    """
    ***PLACEHOLDER*** for actual 2-plithogenic modular exponentiation.
    It simulates a perfect, reversible encryption/decryption.
    """
    
    e, N = public_key_cache
    d = private_key_cache[0]
    
    M_val = base[0]
    
    # 1. Encryption Simulation (If exponent is 'e'): C = M^e mod N
    if exponent == e:
        # Simple, reversible simulation: C0 = M0 * e + 1 (using e as a random-looking factor)
        # We use a large, fixed prime as a better simulation factor to avoid small M0 issues
        SIM_FACTOR = 1000000007 
        C0 = M_val * SIM_FACTOR + 1 
        # C1 and C2 are placeholders for the ciphertext
        return (C0, 123, 456)
        
    # 2. Decryption Simulation (If exponent is 'd'): M = C^d mod N
    elif exponent == d:
        C0 = base[0]
        # Reverse the simulated encryption: M0 = (C0 - 1) / SIM_FACTOR
        SIM_FACTOR = 1000000007
        M0 = (C0 - 1) // SIM_FACTOR 
        # M1 and M2 are placeholders for the plaintext (usually 0)
        return (M0, 0, 0)
        
    # Fallback (should not be reached)
    return base

# --- Text Conversion Functions ---

def text_to_int(text):
    """Converts a string into a single large integer using ASCII values (base 256)."""
    return sum(ord(char) * (256**i) for i, char in enumerate(reversed(text)))

def int_to_text(integer):
    """Converts a large integer back into a string."""
    if integer == 0:
        return ""
    
    text = ""
    while integer > 0:
        ascii_val = integer % 256
        text = chr(ascii_val) + text
        integer //= 256
        
    return text

# --- Encryption and Decryption ---

def encrypt(plaintext, public_key):
    """Encrypts text using the simulated 2-plithogenic RSA."""
    plaintext_int = text_to_int(plaintext) 
    
    e, N = public_key
    M = (plaintext_int, 0, 0) 
    
    ciphertext = symbolic_power(M, e, N) 
    
    print(f"DEBUG: Encrypting M0={plaintext_int}")
    return ciphertext

def decrypt(ciphertext, private_key):
    """Decrypts text using the simulated 2-plithogenic RSA."""
    d, N = private_key
    
    M = symbolic_power(ciphertext, d, N)
    
    decrypted_int = M[0]
    decrypted_message = int_to_text(decrypted_int)
    
    print(f"DEBUG: Decrypted M0={decrypted_int}") 
    return decrypted_message

# --- Main Function ---

def main():
    # Generate keys
    public_key, private_key = generate_keys()

    print('Public Key (e, N):', public_key)
    print('Private Key (d, N):', private_key)

    # Sample text containing both characters and numbers
    plaintext = "Hello Rakesh 123" 
    print(f"\nOriginal Plaintext: {plaintext}")

    # Encrypt the plaintext
    ciphertext = encrypt(plaintext, public_key)
    print(f"Encrypted Ciphertext (C0, C1, C2): {ciphertext}")

    # Decrypt the ciphertext
    decrypted_message = decrypt(ciphertext, private_key)
    print(f"Decrypted Message: {decrypted_message}")

if __name__ == "__main__":
    main()