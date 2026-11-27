import os
import secrets
import urllib.parse
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from src.agentic_os.auth.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    USER_DB,
    PublicUser,
    UserRecord,
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & OAuth 2.0"])

# Ephemeral state & sandbox authorization-code stores for OAuth 2.0 Authorization Code flow
_OAUTH_STATES: Dict[str, str] = {}
_SANDBOX_AUTH_CODES: Dict[str, Dict[str, str]] = {}


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=120)
    full_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS
    scope: str
    user: PublicUser


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: RegisterRequest):
    email = req.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=422, detail="Invalid email address.")
    if email in USER_DB:
        raise HTTPException(status_code=409, detail="Email is already registered.")

    scopes = ["pipeline:run", "agent:run", "memo:approve"]
    record = UserRecord(
        user_id=f"usr-{secrets.token_hex(4)}",
        email=email,
        full_name=req.full_name.strip(),
        role="founder",
        scopes=scopes,
        hashed_password=hash_password(req.password),
        auth_provider="local",
    )
    USER_DB[email] = record
    token = create_access_token(subject=email, role=record.role, scopes=scopes)

    return TokenResponse(
        access_token=token,
        scope=" ".join(scopes),
        user=PublicUser(
            user_id=record.user_id,
            email=record.email,
            full_name=record.full_name,
            role=record.role,
            scopes=record.scopes,
            auth_provider=record.auth_provider,
        ),
    )


@router.post("/token", response_model=TokenResponse)
def oauth2_password_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Standard OAuth 2.0 Password Grant / Bearer Token endpoint (RFC 6749)."""
    email = form_data.username.strip().lower()
    user = USER_DB.get(email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    requested_scopes = form_data.scopes or user.scopes
    granted_scopes = [s for s in requested_scopes if s in user.scopes] or user.scopes
    token = create_access_token(subject=user.email, role=user.role, scopes=granted_scopes)

    return TokenResponse(
        access_token=token,
        scope=" ".join(granted_scopes),
        user=PublicUser(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            scopes=granted_scopes,
            auth_provider=user.auth_provider,
        ),
    )


@router.get("/me", response_model=PublicUser)
def read_current_user(current_user: PublicUser = Depends(get_current_user)):
    return current_user


@router.get("/admin/users")
def list_users_admin(_admin: PublicUser = Depends(require_admin)):
    return [
        PublicUser(
            user_id=u.user_id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            scopes=u.scopes,
            auth_provider=u.auth_provider,
        ).model_dump()
        for u in USER_DB.values()
    ]


@router.get("/oauth2/{provider}/login")
def oauth2_provider_login(provider: str, redirect: bool = False):
    """Initiates OAuth 2.0 Authorization Code flow for Google, GitHub, or Sandbox."""
    provider_clean = provider.lower()
    if provider_clean not in ("google", "github", "sandbox"):
        raise HTTPException(status_code=400, detail="Unsupported OAuth 2.0 provider.")

    state = secrets.token_urlsafe(24)
    _OAUTH_STATES[state] = provider_clean

    if provider_clean == "google" and os.environ.get("GOOGLE_CLIENT_ID"):
        params = urllib.parse.urlencode({
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/api/v1/auth/oauth2/google/callback"),
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        })
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
    elif provider_clean == "github" and os.environ.get("GITHUB_CLIENT_ID"):
        params = urllib.parse.urlencode({
            "client_id": os.environ["GITHUB_CLIENT_ID"],
            "redirect_uri": os.environ.get("GITHUB_REDIRECT_URI", "http://127.0.0.1:8000/api/v1/auth/oauth2/github/callback"),
            "scope": "read:user user:email",
            "state": state,
        })
        auth_url = f"https://github.com/login/oauth/authorize?{params}"
    else:
        # Local OAuth 2.0 Authorization Code Sandbox when external client secrets are not configured
        params = urllib.parse.urlencode({"provider": provider_clean, "state": state})
        auth_url = f"/api/v1/auth/oauth2/sandbox-authorize?{params}"

    if redirect:
        return RedirectResponse(url=auth_url)
    return {"provider": provider_clean, "state": state, "authorization_url": auth_url}


@router.get("/oauth2/sandbox-authorize", response_class=HTMLResponse)
def oauth2_sandbox_consent_page(provider: str = "google", state: str = ""):
    """Local OAuth 2.0 Consent UI for testing Authorization Code flow without external credentials."""
    if state not in _OAUTH_STATES:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth 2.0 state.")
    code = f"code-{secrets.token_hex(8)}"
    _SANDBOX_AUTH_CODES[code] = {
        "provider": provider,
        "email": "ahmed@nu.edu.pk",
        "full_name": f"Ahmed Raza ({provider.title()} OAuth 2.0)",
    }
    callback_url = f"/api/v1/auth/oauth2/{provider}/callback?code={code}&state={urllib.parse.quote(state)}&redirect_ui=true"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>OAuth 2.0 Consent — {provider.title()}</title>
<style>
  body {{ font-family: 'Inter', system-ui, sans-serif; background: #faf6ec; color: #211a0f; display: grid; place-items: center; min-height: 100vh; margin: 0; }}
  .card {{ background: #fffdf8; border: 1px solid rgba(139,101,20,0.24); padding: 36px; max-width: 440px; text-align: center; }}
  h2 {{ font-family: Georgia, serif; font-weight: 500; margin-top: 0; }}
  .btn {{ display: inline-block; margin-top: 18px; background: #211a0f; color: #faf6ec; padding: 12px 24px; text-decoration: none; font-weight: 600; }}
  .btn:hover {{ background: #93630f; }}
</style></head>
<body><div class="card">
  <h2>OAuth 2.0 Authorization ({provider.title()})</h2>
  <p><strong>Agentic Entrepreneur OS</strong> requests access to your profile and email (<code>openid email profile</code>).</p>
  <p style="font-size:0.88rem;color:#786646;">Signing in as <strong>ahmed@nu.edu.pk</strong></p>
  <a class="btn" href="{callback_url}">Authorize &amp; Return Token</a>
</div></body></html>"""


@router.get("/oauth2/{provider}/callback")
def oauth2_provider_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    redirect_ui: bool = False,
):
    """Exchanges OAuth 2.0 Authorization Code + State for a signed Bearer JWT."""
    expected_provider = _OAUTH_STATES.pop(state, None)
    if expected_provider != provider.lower():
        raise HTTPException(status_code=400, detail="Invalid OAuth 2.0 state parameter.")

    email: Optional[str] = None
    full_name: str = "OAuth Founder"

    if code in _SANDBOX_AUTH_CODES:
        info = _SANDBOX_AUTH_CODES.pop(code)
        email = info["email"]
        full_name = info["full_name"]
    elif provider.lower() == "google" and os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
        token_resp = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/api/v1/auth/oauth2/google/callback"),
                "grant_type": "authorization_code",
            },
            timeout=10.0,
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Google OAuth token exchange failed.")
        access_tok = token_resp.json().get("access_token")
        profile_resp = httpx.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_tok}"},
            timeout=10.0,
        )
        profile_data = profile_resp.json()
        email = profile_data.get("email")
        full_name = profile_data.get("name", "Google Founder")
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired authorization code.")

    if not email:
        raise HTTPException(status_code=400, detail="OAuth provider did not return an email.")

    email = email.lower()
    if email not in USER_DB:
        USER_DB[email] = UserRecord(
            user_id=f"usr-{secrets.token_hex(4)}",
            email=email,
            full_name=full_name,
            role="founder",
            scopes=["pipeline:run", "agent:run", "memo:approve"],
            hashed_password=hash_password(secrets.token_urlsafe(16)),
            auth_provider=provider.lower(),
        )

    user = USER_DB[email]
    jwt_token = create_access_token(subject=user.email, role=user.role, scopes=user.scopes)

    if redirect_ui:
        return RedirectResponse(url=f"/?oauth_token={urllib.parse.quote(jwt_token)}")

    return TokenResponse(
        access_token=jwt_token,
        scope=" ".join(user.scopes),
        user=PublicUser(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            scopes=user.scopes,
            auth_provider=provider.lower(),
        ),
    )
