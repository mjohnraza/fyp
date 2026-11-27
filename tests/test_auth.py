import urllib.parse
from fastapi.testclient import TestClient

from src.agentic_os.api.app import app

client = TestClient(app)


def _get_token(username: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_unauthenticated_pipeline_rejected():
    resp = client.post("/api/v1/pipeline/run", json={"founder_name": "Anon"})
    assert resp.status_code == 401


def test_oauth2_password_login_and_me():
    token = _get_token("ahmed@nu.edu.pk", "founder123")
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ahmed@nu.edu.pk"
    assert me.json()["role"] == "founder"


def test_wrong_password_rejected():
    resp = client.post(
        "/api/v1/auth/token",
        data={"username": "ahmed@nu.edu.pk", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_register_new_founder():
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newfounder@nu.edu.pk",
            "full_name": "New Founder",
            "password": "securepassword123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "founder"


def test_rbac_admin_endpoint():
    founder_tok = _get_token("ahmed@nu.edu.pk", "founder123")
    r_forbidden = client.get("/api/v1/auth/admin/users", headers={"Authorization": f"Bearer {founder_tok}"})
    assert r_forbidden.status_code == 403

    admin_tok = _get_token("admin@nu.edu.pk", "admin123")
    r_ok = client.get("/api/v1/auth/admin/users", headers={"Authorization": f"Bearer {admin_tok}"})
    assert r_ok.status_code == 200
    assert len(r_ok.json()) >= 2


def test_oauth2_authorization_code_sandbox_flow():
    # Step 1: Initiate OAuth 2.0 login
    login_resp = client.get("/api/v1/auth/oauth2/google/login")
    assert login_resp.status_code == 200
    auth_url = login_resp.json()["authorization_url"]
    state = login_resp.json()["state"]

    # Step 2: Visit sandbox consent page to mint authorization code
    consent_resp = client.get(auth_url)
    assert consent_resp.status_code == 200
    assert "code=" in consent_resp.text

    # Extract code from consent page HTML link
    marker = "code="
    start = consent_resp.text.index(marker) + len(marker)
    end = consent_resp.text.index("&", start)
    code = consent_resp.text[start:end]

    # Step 3: Exchange authorization code + state for Bearer JWT
    cb_resp = client.get(
        f"/api/v1/auth/oauth2/google/callback?code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}"
    )
    assert cb_resp.status_code == 200
    cb_data = cb_resp.json()
    assert cb_data["token_type"] == "bearer"
    assert cb_data["user"]["email"] == "ahmed@nu.edu.pk"
