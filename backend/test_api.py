"""
Quick test script to verify backend works
Run: python test_api.py
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_analyze():
    """Test analyze endpoint"""
    print("Testing analyze endpoint...")

    payload = {
        "inputType": "text",
        "content": """
{
  "user": "admin",
  "email": "jdoe@company.com",
  "token": "ghp_xYz123AbCdEfGhIjKlMnOpQrStUvWxYz",
  "query": "SELECT * FROM users WHERE id = 1 OR 1=1;"
}
        """.strip(),
        "options": {
            "mask": True,
            "blockHighRisk": False,
            "advancedDetection": True
        }
    }

    response = requests.post(f"{API_URL}/api/analyze", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Analysis successful!")
        print(f"Risk Score: {data['overallRiskScore']}/100")
        print(f"Risk Level: {data['overallRiskLevel']}")
        print(f"Primary Action: {data['primaryAction']}")
        print(f"Total Findings: {data['totalFindings']}")
        print(f"\nFindings:")
        for finding in data['findings']:
            print(f"  - {finding['type']} ({finding['risk']}) on line {finding['line']}")

        print(f"\n✅ Backend is working correctly!")
    else:
        print(f"\n❌ Error: {response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("SecureData AI Backend Test")
    print("=" * 60 + "\n")

    try:
        test_health()
        test_analyze()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend.")
        print("Make sure the backend is running on http://localhost:8000")
        print("\nStart it with: python run.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
