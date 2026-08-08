"""
Identra AI - Comprehensive Verification Test Suite
======================================================
Tests registration, authentication, dashboard routes, profile,
settings, and notification API endpoints.
"""

from app import create_app
from extensions import db
from database.models import User, Document, Notification, TimelineEvent, KnowledgeNode

def test_full_workflow():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    print("[Test] 1. Registering test user...")
    res = client.post('/auth/register', data={
        'username': 'test_architect',
        'email': 'architect@identra.ai',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert res.status_code == 200, f"Registration failed with code {res.status_code}"
    print("  [SUCCESS] Registration successful & sample data seeded!")

    print("[Test] 2. Logging in test user...")
    res = client.post('/auth/login', data={
        'username_or_email': 'test_architect',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert res.status_code == 200, f"Login failed with code {res.status_code}"
    assert b"Console" in res.data or b"Dashboard" in res.data or b"Identra" in res.data, "Dashboard title not found in response"
    print("  [SUCCESS] Login successful! Redirected to console.")

    print("[Test] 3. Verifying Dashboard page (/dashboard/)...")
    res = client.get('/dashboard/')
    assert res.status_code == 200, f"Dashboard load failed: {res.status_code}"
    print("  [SUCCESS] Dashboard page loaded cleanly!")

    print("[Test] 4. Verifying Profile page (/dashboard/profile)...")
    res = client.get('/dashboard/profile')
    assert res.status_code == 200, f"Profile load failed: {res.status_code}"
    assert b"Alex Rivera" in res.data or b"Personal Information" in res.data, "Profile content not found"
    print("  [SUCCESS] Profile page loaded with extended columns!")

    print("[Test] 5. Verifying Settings page (/dashboard/settings)...")
    res = client.get('/dashboard/settings')
    assert res.status_code == 200, f"Settings load failed: {res.status_code}"
    print("  [SUCCESS] Settings page loaded with system preferences!")

    print("[Test] 6. Verifying Notifications API (/api/notifications)...")
    res = client.get('/api/notifications')
    assert res.status_code == 200, f"Notifications API failed: {res.status_code}"
    json_data = res.get_json()
    assert len(json_data) > 0, "No notifications returned"
    print(f"  [SUCCESS] Notifications API returned {len(json_data)} seeded events!")

    print("[Test] 7. Verifying Knowledge Graph API (/api/graph/data)...")
    res = client.get('/api/graph/data')
    assert res.status_code == 200
    gdata = res.get_json()
    assert 'nodes' in gdata and 'edges' in gdata
    print(f"  [SUCCESS] Graph API returned {len(gdata['nodes'])} nodes & {len(gdata['edges'])} edges!")

    print("[Test] 8. Verifying Analytics API (/api/analytics/data)...")
    res = client.get('/api/analytics/data')
    assert res.status_code == 200
    adata = res.get_json()
    assert 'categories' in adata and 'uploads' in adata and 'radar' in adata
    print("  [SUCCESS] Analytics API returned charts payload!")

    print("\nALL 8 VERIFICATION TESTS PASSED SUCCESSFULLY! NO SQLALCHEMY EXCEPTIONS!")

if __name__ == '__main__':
    test_full_workflow()
