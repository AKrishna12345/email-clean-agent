"""
Helper script to generate an encryption key for ENCRYPTION_KEY in .env
"""
import secrets
import base64

# Generate a random 32-byte key
random_bytes = secrets.token_bytes(32)

# Base64 encode it (Fernet format - 44 characters)
key_string = base64.urlsafe_b64encode(random_bytes).decode()

print("=" * 50)
print("Generated Encryption Key:")
print("=" * 50)
print(key_string)
print("=" * 50)
print("\nAdd this to your .env file as:")
print(f"ENCRYPTION_KEY={key_string}")
print("\nNote: Keep this key secure and never commit it to version control!")
print("This key is 44 characters (base64-encoded 32-byte key for Fernet encryption)")

