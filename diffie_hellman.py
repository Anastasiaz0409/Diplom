import secrets
from Crypto.Hash import SHA256

# Большое простое P (используется в вычислениях DH), генератор G=2 (является базой для экспоненциальных вычислений).
P_HEX = """FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1
29024E08A67CC74020BBEA63B139B22514A08798E3404DDEF951
9B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B5766
25E7CBE9995FCFEDB2FA"""
P = int(P_HEX.replace('\n',''), 16)
G = 2
# генерирует пару ключей для Диффи-Хеллмана
def generate_dh_keypair():
    """
    Возвращает кортеж (private_key, public_key).
    """
    private_key = secrets.randbelow(P-2) + 1
    public_key = pow(G, private_key, P)
    return private_key, public_key
# вычисляет общий секретный ключ
def compute_shared_secret(my_private, other_public):
    """
    Возвращает (other_public ^ my_private) mod P
    """
    return pow(other_public, my_private, P)
#  создает ключ для AES из общего секрета
def derive_aes_key(shared_secret):
    """
    Простейший KDF: SHA256(shared_secret).
    Возвращает 32 байта.
    """
    h = SHA256.new()
    # integer -> bytes
    secret_bytes = shared_secret.to_bytes((shared_secret.bit_length() + 7)//8, 'big')
    h.update(secret_bytes)
    return h.digest() # 32 байта