import sys
from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    client = TestClient(app)

    print("--- TEST 1: Unauthenticated request to /api/v1/ai/parse-request ---")
    resp_unauth = client.post("/api/v1/ai/parse-request", json={"text": "My father urgently needs O+ blood at Mayo Hospital Lahore."})
    print(f"Status: {resp_unauth.status_code}")
    print(f"Response: {resp_unauth.json()}")
    assert resp_unauth.status_code == 401, f"Expected 401, got {resp_unauth.status_code}"
    print("PASS: Unauthenticated request correctly returns 401 Unauthorized.\n")

    print("--- TEST 2: User Login to /api/v1/auth/login ---")
    resp_login = client.post("/api/v1/auth/login", json={"email": "user@lifelink.pk", "password": "user123"})
    print(f"Status: {resp_login.status_code}")
    assert resp_login.status_code == 200, f"Expected 200, got {resp_login.status_code}"
    login_data = resp_login.json()
    token = login_data.get("access_token")
    assert token, "No access_token returned"
    print(f"PASS: Login successful. Token obtained: {token[:15]}...\n")

    print("--- TEST 3: Authenticated AI extraction request ---")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"text": "My father urgently needs O+ blood at Mayo Hospital Lahore."}
    resp_ai = client.post("/api/v1/ai/parse-request", json=payload, headers=headers)
    print(f"Status: {resp_ai.status_code}")
    print(f"Response JSON: {resp_ai.json()}")
    assert resp_ai.status_code == 200, f"Expected 200, got {resp_ai.status_code}"
    result = resp_ai.json()
    assert result.get("blood_group") == "O+" or result.get("bloodGroup") == "O+", f"Expected O+, got {result}"
    assert result.get("hospital") == "Mayo Hospital", f"Expected Mayo Hospital, got {result}"
    assert result.get("city") == "Lahore", f"Expected Lahore, got {result}"
    assert result.get("urgency") in ("Critical", "Urgent"), f"Expected Critical or Urgent, got {result}"
    print("PASS: Gemini AI extraction returned correct structured JSON!\n")

if __name__ == "__main__":
    run_tests()
