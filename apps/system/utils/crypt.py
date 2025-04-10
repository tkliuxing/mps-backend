from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.backends import default_backend
from django.utils.crypto import get_random_string
import base64

PRIVATE_KEY = b'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dn\
U2pBZ0VBQW9JQkFRREN1SnBOVFAyWE1lWnkKTkN6MHh3UGVZOXBYb1o5MlIvem9BS2lhVGxBOUM4ajA0MkNheis4cXBWeGh1WldGMmVHW\
FNQUlVQUnhJMTFGTgpvL2pNU2RGb1F1Sm44aGxKWVc3K3VMWENjNWN6VXU3M2VPSTUzOWlHU0JTQ2NkZjJCS3hrMk1PVEc2TCtlcXBsCn\
lkOGE2RURjWkNicGJBcTNxVngvVzlBZlJqWGdwdCtNd1dsSXVhc29zMTBQcUx5OFJzSU1mamNXZkVrQTU3Uk8KNDIrL0FIWE8xelc0NGF\
ybDF3ZlJjOWRqNkM2blZRMXI1VUp4c2M2VUhZNlk1V3AzYTJZQ2tYSldBZDR4aCs3MgpRTDN4UFhKVUxpbDZYUVBlcitiRjZDU0ZhZTI3N\
jd6WWo5bHM4U3lCMjFhTGx3L0p1TUVQNzhyOTFQTGo2QmdUCnJlcmVuR0NsQWdNQkFBRUNnZ0VBWTY5OEZ4eldLbVE2ZExidldQVFZyekZ\
4WXpGejRHcmtONlcycXlCeWhYNFcKQ0FDcndUVzRYQjNCMktuWXVXaWN6QVZtU0FYdENBRnJOeE05Mk4vbG03bTZETHJ0WlJyRFp4WUt2e\
HpNQ0ZOcAowVG1LbjFSUWxoWXFvY2xFWlVkcE5rdWVmQjVHNkg3RjQweGdzbmE2VmRuVDdlWUk2cE9DcmhURHpHNzJRQ1puCjl1bWxzMU1\
aSFRIY3FTZUpick9RNkNETjVlZlB6YXM1WmJLdFJUcXNiOWVVNUUybDdGaWtsUlZYVlVFbFhQZWMKcjBWR3pVSE1DM0RPOGJMRDFtSWJva\
FByT2NhNXc5eTREdFNyZlA2WW9CbndvL0NJVTE1VUJ4aUVrVGsrOER4KwpUOGJabmRHS1RjRUJqMWttZVRDTi90MGVnQkFHL2ZXOXBUd0l\
WYWZvdFFLQmdRRDU2dERFRmRZMnIxWERDdFFnCk1LbXlla2M5dXJ6ZTJQazhHZmtOcEtoMS9Wd2xhUWJ0WGRRUGN5UlhPUEFDT2w0UXI2L\
3k5bS9NSVByaDdBM2YKdis2RFpNbUJYWUErS2tXeUNWYU1RRTRKT3BxcTY5WXBJNGduOE9CK3FRVEVnWE5qWHlIZXJXakJROGV5MmppUgp\
sUzJldmxBcU9OQVIvQVlZUEt3bVNpcTc3d0tCZ1FESGRkNy82Z1dZdnVaTUhWbzJIYmRUcmpCdFdzSU1ueU0xCmRXSGhMeWJUU3RMQWNLe\
mpqMlN1eVBzaGNUdG42dEVzdk0yKzNOblJOZDNEY29iWlFybERQbExGSDFna3NvV2UKNUlnRmwxK2JoN0RGOSsyK3pEb0NVVndDZWx0QmZ\
3M3hTalNKV2Q0RFpyUjlIcDdEYUlrSXl1OVFsU3lBYWltVwp0REZnTndTb3F3S0JnQzBkdGRoZ05NNmtjbkFHYVdyeVBnQkpVTWtWQi9tV\
zQ4OTB4T0F3cEhUQWF6MFpxN1Y0Ckpjc3dOeFJENUJnUzMxNVZ5UWFzZEZ3K2Erd1RDQ0luYlBCdFptOGpLUDZQOVFzQjRvenBJdTFKbGh\
oYkFNdG0KYmJNQUtoYlRmbGZYSXJTQ3ZRT00vSWMvTERMZWNDM2Y1MTlyN2Q3aGFMYUdiN2M2WkwxNDBDUWpBb0dBY3UvYwpXZkg3MmFJZ\
nlUcWMwbFJiWVBBZVhkV1B2b0F4Wk12SVpGK3NhdE5TRUt5ZEkrQnNiei9IWHVVR0M0TEhtSlVQCnBtMVRZdmc4V3pUeXVkMTJMbWFLZ2F\
iblB2WlVnMVJEZ1oxUjdhaktWN25mbVRQTU5hdTJib01kZE9lSEhFVGIKYzA2QzNjamdOcjFmVlZFMnJnZHEwaSt6M2lmTzRWWGlvZ1B5U\
GxNQ2dZRUE0N1JyN2hKQVZFclhlQ0hTbFNSUQpqZmRqbEpiVTNGc08wdXRmRU0ybW44ZDZHWGx6WUVPVkJuUk9WZ0FBVHB3RFlWRHROZnp\
KSWo0TVovdm1uekt2CjVXdlVJakNKdWJHcE53MzVtTVp4VjhsUUNKU0pOTU4xRDRvaWlkdzlzVkhKc3NJS3VTQmxWK2VoRzhYT2ZTdmYKR\
1VPTXlvV2pmb1dOYlY1bDdoMHBicnc9Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K'


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    serialized_private_key = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )

    public_key = private_key.public_key()

    serialized_public_key = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return serialized_public_key, serialized_private_key


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
    data = data.encode()  # bytes
    key = key.encode()
    iv = iv.encode() if isinstance(iv, str) else iv
    backend = default_backend()
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=backend
    ).encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    enc_content = encryptor.update(
        padder.update(data) + padder.finalize()
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


def rsa_encrypt(data: str, public_key_string: str) -> bytes:
    """通过银行公钥对信息加密，并返回字节串"""
    from cryptography.hazmat.primitives.asymmetric import padding
    if not isinstance(data, str):
        raise TypeError('data is not a string!')
    data = data.encode()
    backend = default_backend()
    public_key = serialization.load_pem_public_key(public_key_string.encode(), backend)
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        ),
    )
    return ciphertext


def rsa_decrypt(data: bytes, private_key_string: str) -> str:
    """通过我方私钥对信息解密，并返回字符串"""
    from cryptography.hazmat.primitives.asymmetric import padding
    backend = default_backend()
    private_key = serialization.load_pem_private_key(private_key_string.encode(), password=None, backend=backend)
    plaintext = private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return plaintext.decode()


def base64_rsa_sign(data: str, private_key_string: str) -> str:
    """通过我方私钥对数据签名，并返回base64编码后的字符串"""
    from cryptography.hazmat.primitives.asymmetric import padding
    if not isinstance(data, str):
        raise TypeError('data is not a string!')
    data = data.encode()
    backend = default_backend()
    private_key = serialization.load_pem_private_key(
        private_key_string.encode(), password=None, backend=backend
    )  # type: rsa.RSAPrivateKey
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def base64_rsa_verify(data: str, signature: str, public_key_string: str) -> bool:
    from cryptography.hazmat.primitives.asymmetric import padding
    public_key = serialization.load_pem_public_key(
        public_key_string.encode(), backend=default_backend()
    )  # type: rsa.RSAPublicKey
    try:
        public_key.verify(
            signature.encode(),
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        return False
    return True


def base64_rsa_encrypt(data: str, public_key_string: str) -> str:
    """通过银行公钥对信息加密，并返回base64编码后的字符串"""
    ciphertext = rsa_encrypt(data, public_key_string)
    return base64.b64encode(ciphertext).decode()


def base64_rsa_decrypt(data: str, private_key_string: str) -> str:
    """通过我方私钥对base64字符串解密，并返回字符串"""
    data = base64.b64decode(data)
    return rsa_decrypt(data, private_key_string)
