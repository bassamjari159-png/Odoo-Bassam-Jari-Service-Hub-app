import requests


BASE_URL = "http://localhost:8069"

session = requests.Session()
authentication = session.post(
    f"{BASE_URL}/web/session/authenticate",
    json={
        "jsonrpc": "2.0",
        "params": {
            "db": "odoo_learning",
            "login": "portal",
            "password": "portal",
        },
    },
    timeout=20,
)
authentication.raise_for_status()
uid = authentication.json().get("result", {}).get("uid")
assert uid, "Portal authentication failed"

repair_list = session.get(f"{BASE_URL}/my/repairs", timeout=20)
repair_list.raise_for_status()
assert "Customer Demo Phone" in repair_list.text
assert "BASSAM JARI Service Hub" in repair_list.text
assert "LAP-DEMO-001" not in repair_list.text

own_repair = session.get(f"{BASE_URL}/my/repairs/3", timeout=20)
own_repair.raise_for_status()
assert "REP/00003" in own_repair.text
assert "Repair Progress" in own_repair.text
assert "Payment Summary" in own_repair.text

other_customer_repair = session.get(
    f"{BASE_URL}/my/repairs/1",
    timeout=20,
    allow_redirects=False,
)
assert other_customer_repair.status_code in {302, 303}

print("Portal security and enhanced tracking pages verified successfully.")
