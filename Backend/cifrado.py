from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os

# Generar un par de claves RSA (pública y privada)
def generar_claves_rsa():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Guardar una clave RSA en un archivo
def guardar_clave(clave, archivo, es_privada=True):
    if es_privada:
        pem = clave.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        pem = clave.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    with open(archivo, "wb") as f:
        f.write(pem)

# Cargar una clave RSA desde un archivo
def cargar_clave(archivo, es_privada=True):
    with open(archivo, "rb") as f:
        pem = f.read()
    if es_privada:
        return serialization.load_pem_private_key(pem, password=None, backend=default_backend())
    else:
        return serialization.load_pem_public_key(pem, backend=default_backend())

# Cifrar un archivo con AES-256
def cifrar_archivo(archivo_entrada, archivo_salida, clave_aes):
    iv = os.urandom(16)  # Vector de inicialización (IV)
    cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv), backend=default_backend())
    encriptador = cifrador.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    with open(archivo_entrada, "rb") as f_entrada, open(archivo_salida, "wb") as f_salida:
        f_salida.write(iv)  # Escribir el IV al inicio del archivo
        while True:
            chunk = f_entrada.read(1024)
            if not chunk:
                break
            chunk_padded = padder.update(chunk)
            chunk_cifrado = encriptador.update(chunk_padded)
            f_salida.write(chunk_cifrado)
        chunk_padded = padder.finalize()
        chunk_cifrado = encriptador.update(chunk_padded) + encriptador.finalize()
        f_salida.write(chunk_cifrado)

# Descifrar un archivo con AES-256
def descifrar_archivo(archivo_entrada, archivo_salida, clave_aes):
    with open(archivo_entrada, "rb") as f_entrada:
        iv = f_entrada.read(16)  # Leer el IV del archivo
        cifrador = Cipher(algorithms.AES(clave_aes), modes.CBC(iv), backend=default_backend())
        desencriptador = cifrador.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        with open(archivo_salida, "wb") as f_salida:
            while True:
                chunk = f_entrada.read(1024)
                if not chunk:
                    break
                chunk_descifrado = desencriptador.update(chunk)
                chunk_unpadded = unpadder.update(chunk_descifrado)
                f_salida.write(chunk_unpadded)
            chunk_unpadded = unpadder.finalize()
            f_salida.write(chunk_unpadded)

# Cifrar la clave AES con RSA
def cifrar_clave_aes(clave_aes, clave_publica):
    return clave_publica.encrypt(
        clave_aes,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# Descifrar la clave AES con RSA
def descifrar_clave_aes(clave_cifrada, clave_privada):
    return clave_privada.decrypt(
        clave_cifrada,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )