import abc
import base64
import typing as t

if t.TYPE_CHECKING:
    from . import domain


class BaseEncryptor(abc.ABC):
    can_decrypt: bool = True
    """Whether this encryptor can reverse its own output (private key/passphrase available)."""

    device_id: t.Optional[str] = None
    """The device this encryptor is paired with; None when it is not device-bound."""

    def __init__(self, passphrase: str, *, iterations: int) -> None:
        self.passphrase = passphrase
        self.iterations = iterations

    @abc.abstractmethod
    def encrypt(self, cleartext: str) -> str:
        ...

    @abc.abstractmethod
    def decrypt(self, encrypted: str) -> str:
        ...


_Encryptor: t.Optional[t.Type[BaseEncryptor]] = None


try:
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA1, SHA256
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
    from Crypto.Signature.pss import MGF1
    from Crypto.Util.Padding import pad, unpad

    class AESEncryptor(BaseEncryptor):
        def encrypt(self, cleartext: str) -> str:
            saltBytes = self._generate_salt()
            key = self._generate_key(saltBytes, self.iterations)

            cipher = AES.new(key, AES.MODE_CBC, iv=saltBytes)

            encrypted_bytes = cipher.encrypt(pad(cleartext.encode(), AES.block_size))

            salt = base64.b64encode(saltBytes).decode("utf-8")
            encrypted = base64.b64encode(encrypted_bytes).decode("utf-8")

            return f"$aes-256-cbc/pbkdf2-sha1$i={self.iterations}${salt}${encrypted}"

        def decrypt(self, encrypted: str) -> str:
            chunks = encrypted.split("$")

            if len(chunks) < 5:
                raise ValueError("Invalid encryption format")

            if chunks[1] != "aes-256-cbc/pbkdf2-sha1":
                raise ValueError("Unsupported algorithm")

            params = self._parse_params(chunks[2])
            if "i" not in params:
                raise ValueError("Missing iteration count")

            iterations = int(params["i"])
            salt = base64.b64decode(chunks[-2])
            encrypted_bytes = base64.b64decode(chunks[-1])

            key = self._generate_key(salt, iterations)
            cipher = AES.new(key, AES.MODE_CBC, iv=salt)

            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)

            return decrypted_bytes.decode("utf-8")

        def _generate_salt(self) -> bytes:
            return get_random_bytes(16)

        def _generate_key(self, salt: bytes, iterations: int) -> bytes:
            return PBKDF2(
                self.passphrase,
                salt,
                count=iterations,
                dkLen=32,
                hmac_hash_module=SHA1,
            )

        def _parse_params(self, params: str) -> t.Dict[str, str]:
            return {k: v for k, v in [p.split("=") for p in params.split(",")]}

    _Encryptor = AESEncryptor
except ImportError:
    ...


def Encryptor(passphrase: str, *, iterations: int = 75_000) -> BaseEncryptor:
    if _Encryptor is None:
        raise ImportError("Please install cryptodome")

    return _Encryptor(passphrase, iterations=iterations)


def _mgf1_sha1(seed: bytes, mask_len: int) -> bytes:
    """MGF1 with SHA-1, independent of the OAEP hash (Android Keystore allows only MGF1-SHA-1)."""
    return MGF1(seed, mask_len, SHA1)


class PublicKeyEncryptor(BaseEncryptor):
    """Device-paired E2E encryptor producing the `$rsa-oaep-aes-256-gcm$` envelope.

    Wire format:
    `$rsa-oaep-aes-256-gcm$v=1$k={keyVersion}${b64(wrapped_key)}${b64(iv)}${b64(ct||tag)}`

    RSA-OAEP wraps a fresh 32-byte AES-256 key with OAEP hash SHA-256 and
    MGF1-SHA-1 (empty label); AES-256-GCM with a fresh 12-byte IV and a
    128-bit tag encrypts the payload. A fresh AES key and IV are generated
    for every value.

    The private key never leaves the device, so this encryptor cannot
    decrypt: `can_decrypt` is False and `decrypt` raises. When built via
    `from_device`, `device_id` records the paired device and the client
    refuses sends addressed elsewhere.
    """

    can_decrypt = False

    FORMAT = "rsa-oaep-aes-256-gcm"
    VERSION = "1"
    _AES_KEY_LEN = 32
    _GCM_IV_LEN = 12

    def __init__(
        self,
        public_key: str,
        key_version: int,
        device_id: t.Optional[str] = None,
    ) -> None:
        if _Encryptor is None:
            raise ImportError("Please install cryptodome")

        try:
            key = RSA.import_key(base64.b64decode(public_key))
        except (ValueError, IndexError, TypeError) as e:
            raise ValueError(
                "Invalid public key: must be base64-encoded X.509 SPKI DER"
            ) from e

        self._public_key = key
        self.key_version = key_version
        self.device_id = device_id

    @classmethod
    def from_device(cls, device: "domain.Device") -> "PublicKeyEncryptor":
        """Builds an encryptor from a device carrying an E2E public key.

        Args:
            device: The device with `public_key` and `key_version` populated.

        Returns:
            A PublicKeyEncryptor bound to the device's key and `device.id`.

        Raises:
            ValueError: If the device has no E2E public key.
        """
        if not device.public_key or device.key_version is None:
            raise ValueError(f"Device {device.id} has no E2E public key")

        return cls(device.public_key, device.key_version, device_id=device.id)

    def encrypt(self, cleartext: str) -> str:
        aes_key = get_random_bytes(self._AES_KEY_LEN)
        iv = get_random_bytes(self._GCM_IV_LEN)

        wrapped_key = PKCS1_OAEP.new(
            self._public_key, hashAlgo=SHA256, mgfunc=_mgf1_sha1
        ).encrypt(aes_key)

        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(cleartext.encode("utf-8"))

        return (
            f"${self.FORMAT}"
            f"$v={self.VERSION}"
            f"$k={self.key_version}"
            f"${base64.b64encode(wrapped_key).decode('ascii')}"
            f"${base64.b64encode(iv).decode('ascii')}"
            f"${base64.b64encode(ciphertext + tag).decode('ascii')}"
        )

    def decrypt(self, encrypted: str) -> str:
        raise NotImplementedError(
            "PublicKeyEncryptor cannot decrypt: the private key stays on the device"
        )
