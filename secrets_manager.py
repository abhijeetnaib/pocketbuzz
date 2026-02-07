"""
PocketBuzz Secrets Management
Encrypts and decrypts .env files for secure storage in Git.
"""
import os
import sys
import base64
import hashlib
from pathlib import Path

# Simple XOR encryption with password stretching
def derive_key(password: str, length: int = 256) -> bytes:
    """Derive a key from password using SHA-256."""
    key = password.encode()
    result = b""
    counter = 0
    while len(result) < length:
        result += hashlib.sha256(key + str(counter).encode()).digest()
        counter += 1
    return result[:length]


def encrypt(data: bytes, password: str) -> bytes:
    """Encrypt data with password."""
    key = derive_key(password, len(data))
    encrypted = bytes(a ^ b for a, b in zip(data, key))
    return base64.b64encode(encrypted)


def decrypt(encrypted_data: bytes, password: str) -> bytes:
    """Decrypt data with password."""
    decoded = base64.b64decode(encrypted_data)
    key = derive_key(password, len(decoded))
    return bytes(a ^ b for a, b in zip(decoded, key))


def encrypt_env_file(env_path: str, password: str, output_path: str = None):
    """Encrypt an .env file."""
    if not output_path:
        output_path = env_path + ".encrypted"
    
    with open(env_path, "rb") as f:
        data = f.read()
    
    encrypted = encrypt(data, password)
    
    with open(output_path, "wb") as f:
        f.write(encrypted)
    
    print(f"✅ Encrypted {env_path} -> {output_path}")
    print(f"   Original size: {len(data)} bytes")
    print(f"   Encrypted size: {len(encrypted)} bytes")


def decrypt_env_file(encrypted_path: str, password: str, output_path: str = None):
    """Decrypt an encrypted .env file."""
    if not output_path:
        output_path = encrypted_path.replace(".encrypted", "")
    
    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()
    
    try:
        decrypted = decrypt(encrypted_data, password)
        
        with open(output_path, "wb") as f:
            f.write(decrypted)
        
        print(f"✅ Decrypted {encrypted_path} -> {output_path}")
        print(f"   Output size: {len(decrypted)} bytes")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        print("   Make sure you're using the correct password.")
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Encrypt: python secrets_manager.py encrypt <password>")
        print("  Decrypt: python secrets_manager.py decrypt <password>")
        print("")
        print("Encrypts backend/.env and frontend/.env.local")
        sys.exit(1)
    
    action = sys.argv[1]
    password = sys.argv[2]
    
    base_dir = Path(__file__).parent
    
    backend_env = base_dir / "backend" / ".env"
    frontend_env = base_dir / "frontend" / ".env.local"
    
    if action == "encrypt":
        print("🔐 Encrypting environment files...")
        if backend_env.exists():
            encrypt_env_file(str(backend_env), password)
        else:
            print(f"⚠️  {backend_env} not found, skipping")
        
        if frontend_env.exists():
            encrypt_env_file(str(frontend_env), password)
        else:
            print(f"⚠️  {frontend_env} not found, skipping")
        
        print("\n✅ Done! You can now safely commit the .encrypted files.")
        print("   The original .env files are NOT committed (protected by .gitignore)")
    
    elif action == "decrypt":
        print("🔓 Decrypting environment files...")
        
        backend_encrypted = base_dir / "backend" / ".env.encrypted"
        frontend_encrypted = base_dir / "frontend" / ".env.local.encrypted"
        
        if backend_encrypted.exists():
            decrypt_env_file(str(backend_encrypted), password)
        else:
            print(f"⚠️  {backend_encrypted} not found")
        
        if frontend_encrypted.exists():
            decrypt_env_file(str(frontend_encrypted), password)
        else:
            print(f"⚠️  {frontend_encrypted} not found")
        
        print("\n✅ Done! Environment files restored.")
    
    else:
        print(f"Unknown action: {action}")
        print("Use 'encrypt' or 'decrypt'")
        sys.exit(1)


if __name__ == "__main__":
    main()
