import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jose import jwt

output_path = Path(__file__).parent / "mockdata/jwt"
os.makedirs(output_path, exist_ok=True)


# Generate RSA key pair
def generate_rsa_key_pair() -> Tuple[RSAPrivateKey, bytes, bytes]:
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
def create_jwks(public_key: RSAPublicKey, kid: str = "pytest") -> Dict[str, Any]:
    numbers = public_key.public_numbers()
    e = base64.urlsafe_b64encode(numbers.e.to_bytes(3, "big")).decode("utf-8").rstrip("=")
    n = (
        base64.urlsafe_b64encode(
            numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
        )
        .decode("utf-8")
        .rstrip("=")
    )
    x5c = [
        base64.b64encode(
            public_key.public_bytes(
                encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo
            )
        ).decode("utf-8")
    ]
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": n,
        "e": e,
        "x5c": x5c,
    }
    return {"keys": [jwk]}


# Generate JWT
def create_jwt_token(
    scope: str,
    audience: str,
    kid: str = "pytest",
) -> str:
    with open(output_path / "private_key.pem", "rb") as f:
        private_key = f.read()

    now = int(time.time())
    claims = {
        "iss": "pytest-auth",
        "sub": "appuser",
        "exp": now + 3600,
        "iat": now,
        "scope": scope,
        "aud": audience,
    }
    token = jwt.encode(claims, key=private_key, algorithm="RS256", headers={"kid": kid})
    return token


def derive_public_key(private_key_pem: bytes) -> RSAPublicKey:
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
    )
    public_key = private_key.public_key()
    return public_key  # pyright: ignore


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # if no parameters is passed, generate a new key pair
        key_pair, private_pem, public_pem = generate_rsa_key_pair()
        public_key = key_pair.public_key()
    else:
        # the 1st parameter is the path to the private key
        with open(sys.argv[1], "rb") as f:
            private_pem = f.read()
        public_key = derive_public_key(private_pem)

    jwks_data = create_jwks(public_key)

    with open(output_path / "private_key.pem", "wb") as f:
        f.write(private_pem)
    with open(output_path / "jwks.json", "wb") as f:
        f.write(json.dumps(jwks_data, indent=2).encode())

    jwt_token = create_jwt_token(scope="read:data", audience="dummy-audience")
    print("Dummy JWT Token:", jwt_token)
