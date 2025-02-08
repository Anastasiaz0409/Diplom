from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Константы
BLOCK_SIZE = 16  # Размер блока в байтах
KEY_SIZE = 32    # Размер ключа в байтах
# Функция для шифрования
def encrypt_gost_AES(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = pad(data, BLOCK_SIZE)
    encrypted_data = cipher.encrypt(padded_data)
    return encrypted_data
# Функция для расшифрования
def decrypt_gost_AES(key, encrypted_data):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    unpadded_data = unpad(decrypted_data, BLOCK_SIZE)
    return unpadded_data

