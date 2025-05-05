import base64
import json
import os
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

from settings import settings

output_path = Path(__file__).parent / "mockdata/jwt"
os.makedirs(output_path, exist_ok=True)


# Generate RSA key pair
def generate_rsa_key_pair():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return key, private_key_pem, public_key_pem


# Encode public key to JWKS
def create_jwks(public_key, kid="pytest"):
    numbers = public_key.public_numbers()
    e = base64.urlsafe_b64encode(numbers.e.to_bytes(3, "big")).decode("utf-8").rstrip("=")
    n = (
        base64.urlsafe_b64encode(
            numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
        )
        .decode("utf-8")
        .rstrip("=")
    )
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": n,
        "e": e,
    }
    return {"keys": [jwk]}


# Generate JWT
def create_jwt_token(
    scope,
    kid="pytest",
):
    with open(output_path / "private_key.pem", "rb") as f:
        private_key = f.read()

    now = int(time.time())
    claims = {
        "iss": "pytest-auth",
        "sub": "appuser",
        "exp": now + 3600,
        "iat": now,
        "scope": scope,
        "aud": settings.api_audience,
    }
    token = jwt.encode(claims, key=private_key, algorithm="RS256", headers={"kid": kid})
    return token


if __name__ == "__main__":
    key_pair, private_pem, public_pem = generate_rsa_key_pair()
    public_key = key_pair.public_key()
    jwks_data = create_jwks(public_key)

    with open(output_path / "private_key.pem", "wb") as f:
        f.write(private_pem)
    with open(output_path / "jwks.json", "wb") as f:
        f.write(json.dumps(jwks_data, indent=2).encode())

    jwt_token = create_jwt_token(scope="read:data")
    print("JWT Token:", jwt_token)
