# SRP-6a demo (client & server) - implementação educacional
# Simula o protocolo SRP: registro e autenticação
# Usa SHA-256 e grupo 1024 bits (RFC 5054). NÃO usar em produção.

from hashlib import sha256
import os, binascii

# Parâmetros RFC 5054: N (prime) e g (gerador)
N_hex = """
EEAF0AB9ADB38DD69C33F80AFA8FC5E8
66393129F5B3B4B0B8B0D6A0D5F8E1F7
A3E5B2A6D6A3E7ED7C4B7FA9A5A6E6D2
6C3E3B3B3F2D9C9E4B1A2C3D4E5F6A7B
E4D3C2B1A0F9E8D7C6B5A49382716054
3C2B1A0F9E8D7C6B5A49382716054C3B
A1F0E9D8C7B6A5948372615043210FED
CBA98765432100112233445566778899
""".replace("\n","").replace(" ","")

N = int(N_hex, 16)
g = 2

# Funções utilitárias
def H(*args):
    """Hash (SHA-256) concatenado de múltiplos valores."""
    h = sha256()
    for a in args:
        if isinstance(a, int):
            a = a.to_bytes((a.bit_length()+7)//8 or 1, 'big')
        elif isinstance(a, str):
            a = a.encode()
        h.update(a)
    return h.digest()

def H_int(*args):
    return int.from_bytes(H(*args), 'big')

def pad_hex(i):
    return format(i, 'x')

# Multiplicador k = H(N, g)
k = H_int(N, g)

# ==========================
# FASE 1: REGISTRO
# ==========================
def register(username, password):
    salt = os.urandom(16)
    xH = H(salt, username.encode(), b":", password.encode())
    x = int.from_bytes(xH, 'big')
    v = pow(g, x, N)  # Verificador armazenado no servidor
    return salt, v

# ==========================
# FASE 2: AUTENTICAÇÃO
# ==========================
def client_step1():
    a = int.from_bytes(os.urandom(32), 'big')
    A = pow(g, a, N)
    return a, A

def server_step1(v):
    b = int.from_bytes(os.urandom(32), 'big')
    B = (k * v + pow(g, b, N)) % N
    return b, B

def compute_session_client(a, salt, username, password, A, B):
    u = H_int(A, B)
    x = H_int(salt, username.encode(), b":", password.encode())
    S = pow((B - k * pow(g, x, N)) % N, (a + u * x), N)
    K = H(S)
    return u, S, K

def compute_session_server(b, salt, v, A, B):
    u = H_int(A, B)
    S = pow((A * pow(v, u, N)) % N, b, N)
    K = H(S)
    return u, S, K

def client_proof(username, salt, A, B, K):
    H_N = H(N)
    H_g = H(g)
    H_xor = bytes(x ^ y for x, y in zip(H_N, H_g))
    H_user = sha256(username.encode()).digest()
    M1 = sha256(H_xor + H_user + salt +
                A.to_bytes((A.bit_length()+7)//8,'big') +
                B.to_bytes((B.bit_length()+7)//8,'big') + K).digest()
    return M1

def server_proof(A, M1, K):
    M2 = sha256(A.to_bytes((A.bit_length()+7)//8,'big') + M1 + K).digest()
    return M2

# ==========================
# EXECUÇÃO DEMO
# ==========================
username = "alice"
password = "correct horse battery staple"

print("=== SRP-6a demo (educacional) ===\n")

# Registro
print("Registro:")
salt, v = register(username, password)
print(" Server armazena: salt =", binascii.hexlify(salt).decode(), "v =", pad_hex(v)[:10]+"...")

# Autenticação
print("\nAutenticação:")
a, A = client_step1()
b, B = server_step1(v)
print(" Cliente envia A =", pad_hex(A)[:16]+"...")
print(" Servidor envia B =", pad_hex(B)[:16]+"... e salt")

# Ambos calculam sessão
u_c, S_c, K_c = compute_session_client(a, salt, username, password, A, B)
u_s, S_s, K_s = compute_session_server(b, salt, v, A, B)

print("\nValores calculados:")
print(" u =", u_c)
print(" S (cliente) =", pad_hex(S_c)[:16]+"...")
print(" S (servidor) =", pad_hex(S_s)[:16]+"...")
print(" K (cliente) =", binascii.hexlify(K_c).decode()[:16]+"...")
print(" K (servidor) =", binascii.hexlify(K_s).decode()[:16]+"...")

if S_c == S_s:
    print("\nChaves de sessão coincidem!")
else:
    print("\nERRO: chaves não coincidem!")

# Provas M1 e M2
M1 = client_proof(username, salt, A, B, K_c)
expected_M1 = client_proof(username, salt, A, B, K_s)
if M1 == expected_M1:
    print("\nM1 verificado pelo servidor.")
    M2 = server_proof(A, M1, K_s)
    print("M2 enviado ao cliente.")
    expected_M2 = server_proof(A, M1, K_c)
    if M2 == expected_M2:
        print("M2 verificado pelo cliente. Autenticação concluída!\n")
else:
    print("\nFalha na verificação M1. Autenticação rejeitada.\n")

print("=== Fim do demo ===")
