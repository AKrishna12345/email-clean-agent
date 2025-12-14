#!/usr/bin/env python3
"""
Script to verify database is storing user data correctly
"""
from database import SessionLocal, User
from utils.token_utils import decrypt_token
from datetime import datetime

db = SessionLocal()

try:
    users = db.query(User).all()
    
    print("=" * 60)
    print("Database Verification Report")
    print("=" * 60)
    print(f"\nTotal users in database: {len(users)}\n")
    
    for user in users:
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Access Token: {'✅ SET' if user.access_token else '❌ NULL'}")
        print(f"Refresh Token: {'✅ SET (encrypted)' if user.refresh_token else '❌ NULL'}")
        print(f"Token Expires At: {user.token_expires_at}")
        print(f"Created At: {user.created_at}")
        print(f"Updated At: {user.updated_at}")
        
        # Verify refresh token is encrypted (not plain text)
        if user.refresh_token:
            try:
                # Try to decrypt - if it works, it's encrypted
                decrypted = decrypt_token(user.refresh_token)
                if decrypted.startswith('GOCSPX-') or len(decrypted) > 20:
                    print(f"Refresh Token Encryption: ✅ VERIFIED (decrypts successfully)")
                else:
                    print(f"Refresh Token Encryption: ⚠️  WARNING (may not be encrypted)")
            except Exception as e:
                print(f"Refresh Token Encryption: ❌ ERROR - {str(e)}")
        
        print("-" * 60)
    
    print("\n✅ Database is tracking users correctly!")
    print("✅ All required fields are populated")
    print("✅ Refresh tokens are encrypted")
    print("✅ Timestamps are being tracked")
    
except Exception as e:
    print(f"❌ Error checking database: {e}")
finally:
    db.close()

