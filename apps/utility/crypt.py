from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.backends import default_backend
from django.utils.crypto import get_random_string
import base64


def gen_aes_key(length=16) -> str:
    if length not in [16, 32, 64, 128]:
        raise ValueError('length illegal!')
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ*&^%$#@!~0123456789'
    return get_random_string(length, chars)


def aes_cbc_pkcs7_encrypt(data: str, key: str, iv=b'\0' * 16) -> str:
    """
    use AES CBC to encrypt message, using key and init vector， padding: PKCS7
    :param data: 待加密的数据
    :param key: 密钥字符串
    :param iv: 初始向量字节串
    :return: base64编码后的字符串
    """
    adata = data.encode()  # bytes
    akey = key.encode()
    iv = iv.encode() if isinstance(iv, str) else iv
    backend = default_backend()
    encryptor = Cipher(
        algorithms.AES(akey),
        modes.CBC(iv),
        backend=backend
    ).encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    enc_content = encryptor.update(
        padder.update(adata) + padder.finalize()
    ) + encryptor.finalize()
    enc_data = base64.b64encode(enc_content)
    return enc_data.decode()


def aes_cbc_pkcs7_decrypt(data: str, key: str, iv=b'\0' * 16) -> str:
    """
    use AES CBC to decrypt message, using key and init vector， padding: PKCS7
    :param data: 待加密的数据
    :param key: 密钥字符串
    :param iv: 初始向量字节串
    :return: base64编码后的字符串
    """
    data = base64.b64decode(data)
    key = key.encode()
    iv = iv.encode() if isinstance(iv, str) else iv
    backend = default_backend()
    decryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=backend
    ).decryptor()
    enc_content = decryptor.update(data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    enc_content = unpadder.update(enc_content) + unpadder.finalize()
    return enc_content.decode()


def load_pkcs12_file(file_path: str, password: str) -> PrivateKeyTypes:
    """
    load p12 file and return private key and certificate
    :param file_path: p12 file path
    :param password: password of p12 file
    :return: private key bytes, certificate bytes
    """
    from cryptography.hazmat.primitives.serialization.pkcs12 import load_pkcs12
    with open(file_path, 'rb') as f:
        p12_data = f.read()
    certificates = load_pkcs12(p12_data, password.encode())
    return certificates.key


def load_private_key_from_pem_file(file_path: str, password: str) -> PrivateKeyTypes:
    """
    load private key from pem file
    :param file_path: pem file path
    :param password: password of private key
    :return: private key bytes
    """
    with open(file_path, 'rb') as f:
        private_key = f.read()
    return load_private_key_from_pem_bytes(private_key, password)


def load_private_key_from_pem_bytes(private_key_bytes: bytes, password: str) -> PrivateKeyTypes:
    """
    load private key from pem bytes
    :param private_key_bytes: private key bytes in pem format
    :param password: password of private key
    :return: private key bytes
    """
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    private_key = load_pem_private_key(private_key_bytes, password.encode(), backend=default_backend())
    return private_key


def rsa_private_key_sign_sha1(private_key: PrivateKeyTypes, data: bytes):
    """
    use rsa private key to sign data with sha1
    :param private_key: private key object
    :param data: data to be signed
    :return: signature bytes
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    return signature


def gen_rsa_key_pair() -> tuple[str, str]:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    private_key_string = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_string = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key_string.decode(), public_key_string.decode()


def rsa_private_decrypt(private_key_string: str, data: str) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.asymmetric import rsa
    private_key: rsa.RSAPrivateKey = serialization.load_pem_private_key(
        private_key_string.encode(),
        password=None,
        backend=default_backend()
    )  # type: ignore
    decode_data = base64.b64decode(data)
    decrypted_data = private_key.decrypt(
        decode_data,
        padding.PKCS1v15()
    )
    return decrypted_data.decode()


def rsa_public_encrypt(public_key_string: str, data: str) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.asymmetric import rsa
    public_key: rsa.RSAPublicKey = serialization.load_pem_public_key(
        public_key_string.encode(),
        backend=default_backend()
    )  # type: ignore
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.PKCS1v15()
    )
    return base64.b64encode(encrypted_data).decode()


def main():
    import base64
    password = 'ys@hgj'
    rsa_private_key = load_private_key_from_pem_file('private_key.pem', password)
    print(rsa_private_key.key_size)
    test_data = 'hello world'
    encrypted_data = rsa_private_key_sign_sha1(rsa_private_key, test_data.encode())
    print(base64.b64encode(encrypted_data).decode())


if __name__ == '__main__':
    main()
