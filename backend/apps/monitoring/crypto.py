import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


class PnrEncryptionUnavailable(Exception):
    pass


def _key_bytes():
    key = settings.PNR_ENCRYPTION_KEY.strip()
    if not key:
        raise PnrEncryptionUnavailable("PNR tracking is not configured on this server.")
    try:
        return key.encode("ascii")
    except UnicodeEncodeError as exc:
        raise PnrEncryptionUnavailable("PNR encryption key must be a Fernet key.") from exc


def encrypt_pnr(pnr: str) -> str:
    try:
        return Fernet(_key_bytes()).encrypt(pnr.encode("ascii")).decode("ascii")
    except (ValueError, TypeError) as exc:
        raise PnrEncryptionUnavailable("PNR encryption key must be a valid Fernet key.") from exc


def decrypt_pnr(ciphertext: str) -> str:
    try:
        return Fernet(_key_bytes()).decrypt(ciphertext.encode("ascii")).decode("ascii")
    except (InvalidToken, ValueError, TypeError, UnicodeError) as exc:
        raise PnrEncryptionUnavailable("Stored PNR cannot be decrypted with the current key.") from exc


def fingerprint_pnr(pnr: str) -> str:
    digest_key = hashlib.sha256(_key_bytes()).digest()
    return hmac.new(digest_key, pnr.encode("ascii"), hashlib.sha256).hexdigest()
