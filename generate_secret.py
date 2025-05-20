import secrets

secret_key = secrets.token_urlsafe(32)
print(f"Your Secret Key: {secret_key}")
