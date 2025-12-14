from cryptography.fernet import Fernet
import config
import base64

# Initialize Fernet cipher with encryption key
def get_cipher():
    # Fernet key should be base64-encoded 32-byte key (44 characters)
    # If it's already a valid Fernet key, use it directly
    # Otherwise, try to decode/encode it properly
    key_str = config.ENCRYPTION_KEY
    
    try:
        # Try using it directly (if it's already a valid Fernet key)
        return Fernet(key_str.encode())
    except Exception:
        # If not, try to create a valid key from it
        # Take first 32 bytes and base64 encode
        key_bytes = key_str.encode()[:32]
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b'0')
        key_b64 = base64.urlsafe_b64encode(key_bytes)
        return Fernet(key_b64)


def encrypt_token(token: str) -> str:
    """Encrypt a token for storage"""
    if not token:
        return ""
    cipher = get_cipher()
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored token"""
    if not encrypted_token:
        return ""
    cipher = get_cipher()
    try:
        return cipher.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt token: {str(e)}")

