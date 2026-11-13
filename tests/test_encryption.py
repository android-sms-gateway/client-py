import base64

import pytest

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA1, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pss import MGF1

from android_sms_gateway.domain import Device
from android_sms_gateway.encryption import AESEncryptor, PublicKeyEncryptor


def test_decrypt():
    passphrase = "passphrase"
    cleartext = "hello"
    encrypted = "$aes-256-cbc/pbkdf2-sha1$i=75000$obSTW6ittQvTtdAxonQKIw==$g3QFAC9CtBcPxoKlouqsyQ=="
    encryptor = AESEncryptor(passphrase, iterations=75000)

    decrypted = encryptor.decrypt(encrypted)

    assert cleartext == decrypted


def test_encrypt_decrypt():
    passphrase = "correcthorsebatterystaple"
    encryptor = AESEncryptor(passphrase, iterations=1000)
    cleartext = "The quick brown fox jumps over the lazy dog"
    encrypted = encryptor.encrypt(cleartext)
    decrypted = encryptor.decrypt(encrypted)
    assert cleartext == decrypted


def test_invalid_format_error():
    passphrase = "correcthorsebatterystaple"
    encryptor = AESEncryptor(passphrase, iterations=1000)
    with pytest.raises(ValueError, match="Invalid encryption format"):
        encryptor.decrypt("invalid$format$string")


def test_unsupported_algorithm_error():
    passphrase = "correcthorsebatterystaple"
    encryptor = AESEncryptor(passphrase, iterations=1000)
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        encryptor.decrypt("$unsupported-algorithm$i=0$salt$data")


def test_missing_iteration_count_error():
    passphrase = "correcthorsebatterystaple"
    encryptor = AESEncryptor(passphrase, iterations=1000)
    with pytest.raises(ValueError, match="Missing iteration count"):
        encryptor.decrypt("$aes-256-cbc/pbkdf2-sha1$x=0$salt$data")


def test_passphrase_encryptor_can_decrypt():
    assert AESEncryptor("passphrase", iterations=1).can_decrypt is True


@pytest.fixture(scope="module")
def rsa_keypair():
    return RSA.generate(2048)


def _spki_b64(key) -> str:
    return base64.b64encode(key.publickey().export_key(format="DER")).decode(
        "ascii"
    )


def _decrypt_wrapped_key(wrapped_key: bytes, private_key) -> bytes:
    """Decrypts the AES key with OAEP SHA-256 + MGF1-SHA-1 (the wire params)."""
    cipher = PKCS1_OAEP.new(
        private_key, hashAlgo=SHA256, mgfunc=lambda s, n: MGF1(s, n, SHA1)
    )
    return cipher.decrypt(wrapped_key)


@pytest.mark.parametrize(
    "plaintext",
    ["", "hello", "unicode: 日本語 и ελληνικά", "a" * 1000],
)
def test_public_key_encryptor_round_trip(rsa_keypair, plaintext):
    encryptor = PublicKeyEncryptor(_spki_b64(rsa_keypair), key_version=7)

    envelope = encryptor.encrypt(plaintext)

    chunks = envelope.split("$")
    assert len(chunks) == 7
    assert chunks[0] == ""
    assert chunks[1] == "rsa-oaep-aes-256-gcm"
    assert chunks[2] == "v=1"
    assert chunks[3] == "k=7"

    wrapped_key = base64.b64decode(chunks[4])
    iv = base64.b64decode(chunks[5])
    ct_tag = base64.b64decode(chunks[6])

    assert len(wrapped_key) == 256
    assert len(iv) == 12
    assert len(ct_tag) == len(plaintext.encode("utf-8")) + 16

    aes_key = _decrypt_wrapped_key(wrapped_key, rsa_keypair)
    assert len(aes_key) == 32

    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    recovered = cipher.decrypt_and_verify(ct_tag[:-16], ct_tag[-16:])
    assert recovered.decode("utf-8") == plaintext


def test_public_key_encryptor_is_randomized(rsa_keypair):
    encryptor = PublicKeyEncryptor(_spki_b64(rsa_keypair), key_version=1)

    first = encryptor.encrypt("payload")
    second = encryptor.encrypt("payload")

    assert first != second
    # Fresh AES key per value -> wrapped key chunk differs
    assert first.split("$")[4] != second.split("$")[4]
    # Fresh IV per value -> IV chunk differs
    assert first.split("$")[5] != second.split("$")[5]


def test_public_key_encryptor_mgf1_pinned_to_sha1(rsa_keypair):
    """The default pycryptodome OAEP (MGF1-SHA-256) must NOT decrypt our output."""
    encryptor = PublicKeyEncryptor(_spki_b64(rsa_keypair), key_version=1)
    wrapped_key = base64.b64decode(encryptor.encrypt("x").split("$")[4])

    with pytest.raises(ValueError):
        PKCS1_OAEP.new(rsa_keypair, hashAlgo=SHA256).decrypt(wrapped_key)


def test_public_key_encryptor_decrypt_not_supported(rsa_keypair):
    encryptor = PublicKeyEncryptor(_spki_b64(rsa_keypair), key_version=1)

    assert encryptor.can_decrypt is False
    with pytest.raises(NotImplementedError, match="private key stays on the device"):
        encryptor.decrypt(encryptor.encrypt("x"))


def test_public_key_encryptor_from_device(rsa_keypair):
    device = Device(
        id="device-1",
        name="ZTE/BLADE",
        public_key=_spki_b64(rsa_keypair),
        key_version=3,
    )

    encryptor = PublicKeyEncryptor.from_device(device)

    assert encryptor.key_version == 3
    assert encryptor.device_id == "device-1"
    assert encryptor.encrypt("x").split("$")[3] == "k=3"

    envelope = encryptor.encrypt("hello").split("$")
    aes_key = _decrypt_wrapped_key(base64.b64decode(envelope[4]), rsa_keypair)
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=base64.b64decode(envelope[5]))
    ct_tag = base64.b64decode(envelope[6])
    assert cipher.decrypt_and_verify(ct_tag[:-16], ct_tag[-16:]) == b"hello"


def test_public_key_encryptor_from_device_without_key():
    with pytest.raises(ValueError, match="has no E2E public key"):
        PublicKeyEncryptor.from_device(Device(id="device-1", name="n"))


def test_public_key_encryptor_invalid_public_key():
    with pytest.raises(ValueError, match="Invalid public key"):
        PublicKeyEncryptor("not-base64!!", key_version=1)
