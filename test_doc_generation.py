import httpx

login_url = "http://localhost:8005/api/v1/auth/login"
cases_url = "http://localhost:8005/api/v1/cases"

def test_generation():
    # 1. Login
    payload = {
        "email": "landlord@legalflow.lk",
        "password": "LegalFlow2026!"
    }
    print("Logging in...")
    try:
        resp = httpx.post(login_url, json=payload, timeout=10.0)
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return
        
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} - {resp.text}")
        return
    token = resp.json()["token"]["access_token"]
    print("Login successful! Token acquired.")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 2. Get Cases
    print("Fetching active cases...")
    resp = httpx.get(cases_url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch cases: {resp.status_code} - {resp.text}")
        return
    cases = resp.json()
    if not cases:
        print("No cases found in DB. Please seed the DB first.")
        return

    # Find the case for Kamal Silva
    case_to_test = None
    for case in cases:
        print(f"Case ID: {case['id']} | Status: {case['status']}")
        if case["status"] == "OPEN":
            case_to_test = case
            break

    if not case_to_test:
        case_to_test = cases[0]

    case_id = case_to_test["id"]
    print(f"Using Case ID: {case_id} for generation test.")

    # 3. Generate Letter of Demand
    gen_url = f"http://localhost:8005/api/v1/cases/{case_id}/generate?document_type=LETTER_OF_DEMAND"
    print(f"Triggering document generation for model google/gemini-2.5-flash...")
    resp = httpx.post(gen_url, headers=headers, timeout=60.0)
    if resp.status_code == 200:
        data = resp.json()
        print("\n✅ Document Generated Successfully!")
        print(f"Document ID: {data.get('id')}")
        print(f"Title: {data.get('title')}")
        print("--- CONTENT ---")
        print(data.get("content"))
        print("---------------")
    else:
        print(f"❌ Generation failed with status {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    test_generation()
