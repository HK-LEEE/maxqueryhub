#!/usr/bin/env python3
"""
Test the internal execute API endpoint directly.
"""
import requests
import json


def test_debug_endpoint(query_id=7):
    """Test the debug endpoint first."""
    url = f"http://localhost:8006/api/v1/debug/query/{query_id}"
    
    print(f"Testing debug endpoint for query {query_id}...")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error calling debug endpoint: {e}")
        return None


def test_execute_endpoint(query_id, jwt_token, params=None):
    """Test the internal execute endpoint."""
    url = f"http://localhost:8006/api/v1/internal/execute/{query_id}"
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "params": params or {}
    }
    
    print(f"\nTesting internal execute endpoint for query {query_id}...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.json()
    except Exception as e:
        print(f"Error calling execute endpoint: {e}")
        if hasattr(response, 'text'):
            print(f"Response text: {response.text}")
        return None


def main():
    # First, check what queries exist
    print("=" * 80)
    print("STEP 1: Check available queries")
    print("=" * 80)
    
    # Test with different query IDs
    for query_id in [1, 2, 3, 4, 5, 6, 7]:
        debug_info = test_debug_endpoint(query_id)
        if debug_info and 'error' not in debug_info:
            print(f"\nQuery {query_id} exists!")
            break
    
    # You'll need to get a valid JWT token from the authentication server
    # For testing, you can get this from the browser developer tools after logging in
    print("\n" + "=" * 80)
    print("STEP 2: Test query execution")
    print("=" * 80)
    print("\nTo test execution, you need a valid JWT token.")
    print("You can get this from:")
    print("1. Login to the frontend at http://localhost:3006")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Application/Storage -> Local Storage")
    print("4. Copy the 'token' value")
    print("\nOr run this curl command to get a token:")
    print("curl -X POST http://localhost:8000/auth/login \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"username\": \"your_username\", \"password\": \"your_password\"}'")
    
    jwt_token = input("\nEnter your JWT token (or press Enter to skip): ").strip()
    
    if jwt_token:
        # Test with a simple query (if it exists)
        test_execute_endpoint(1, jwt_token, {"start_date": "2024-01-01", "end_date": "2024-01-31"})


if __name__ == "__main__":
    main()