import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Dict, List, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel, Field

# Secret key for HS256 JWT signing (override via AGENTIC_OS_JWT_SECRET in production)
JWT_SECRET = os.environ.get("AGENTIC_OS_JWT_SECRET", "agentic-os-fyp-2026-dev-secret-key-change-in-prod")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "pipeline:run": "Execute the 13-agent opportunity discovery pipeline",
        "agent:run": "Execute live MCP + SKILL.md ReAct agent loops",
        "memo:approve": "Approve human-in-the-loop checkpoints and unlock memos",
        "admin:read": "Inspect platform users and audit telemetry",
    },
)


class UserRecord(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str = "founder"  # "founder" | "admin"
    scopes: List[str] = Field(default_factory=lambda: ["pipeline:run", "agent:run", "memo:approve"])
    hashed_password: str
    auth_provider: str = "local"  # "local" | "google" | "github"
    is_active: bool = True


class PublicUser(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    scopes: List[str]
    auth_provider: str


def hash_password(password: str, salt: Optional[str] = None) -> str:
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected_hex = stored_hash.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return hmac.compare_digest(dk.hex(), expected_hex)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(
    subject: str,
    role: str,
    scopes: List[str],
    expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS,
) -> str:
    now = int(time.time())
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": subject,
        "role": role,
        "scopes": scopes,
        "iat": now,
        "exp": now + expires_delta,
    }
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(sig)}"


def decode_access_token(token: str) -> Dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid token signature")
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("Token expired")
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# In-memory user store seeded with default FYP demo accounts
USER_DB: Dict[str, UserRecord] = {
    "ahmed@nu.edu.pk": UserRecord(
        user_id="usr-founder-01",
        email="ahmed@nu.edu.pk",
        full_name="Ahmed Raza",
        role="founder",
        scopes=["pipeline:run", "agent:run", "memo:approve"],
        hashed_password=hash_password("founder123"),
        auth_provider="local",
    ),
    "admin@nu.edu.pk": UserRecord(
        user_id="usr-admin-01",
        email="admin@nu.edu.pk",
        full_name="FYP Evaluator Admin",
        role="admin",
        scopes=["pipeline:run", "agent:run", "memo:approve", "admin:read"],
        hashed_password=hash_password("admin123"),
        auth_provider="local",
    ),
}


def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> PublicUser:
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    payload = decode_access_token(token)
    email = payload.get("sub")
    if not email or email not in USER_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": authenticate_value},
        )

    user = USER_DB[email]
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    token_scopes = set(payload.get("scopes", []))
    for required_scope in security_scopes.scopes:
        if required_scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Missing scope: {required_scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return PublicUser(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        scopes=user.scopes,
        auth_provider=user.auth_provider,
    )


def require_admin(current_user: PublicUser = Security(get_current_user, scopes=["admin:read"])) -> PublicUser:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user
