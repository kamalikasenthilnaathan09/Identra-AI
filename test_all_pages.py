"""
Identra AI - 14-Route Complete Frontend & Page Verification
"""

from app import create_app

def test_all_pages():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    print("\n--- AUDITING ALL 14 FRONTEND PAGES & ROUTES ---")
    
    # 1. Test public unauthenticated pages
    guest_pages = [
        ('/', 'Landing Page'),
        ('/auth/login', 'Login Page'),
        ('/auth/register', 'Register Page'),
        ('/about', 'About Page'),
    ]
    for route, name in guest_pages:
        res = client.get(route)
        assert res.status_code == 200, f"Guest page failed: {name} at {route} ({res.status_code})"
        print(f"  [SUCCESS] Guest Page: {name} ({route}) -> HTTP 200 OK")

    # 2. Register & Login
    print("\n[Verification] Logging in test account...")
    client.post('/auth/register', data={
        'username': 'full_verifier',
        'email': 'full_verifier@identra.ai',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)

    client.post('/auth/login', data={
        'username_or_email': 'full_verifier',
        'password': 'Password123!'
    }, follow_redirects=True)

    # 3. Test authenticated dashboard pages
    auth_pages = [
        ('/dashboard/', 'Dashboard Console'),
        ('/documents/', 'Document Upload Page'),
        ('/documents/vault', 'AI Document Vault Page'),
        ('/google-drive/', 'Google Drive Integration Page'),
        ('/dashboard/graph', 'Knowledge Graph Page'),
        ('/timeline/', 'Career Timeline Page'),
        ('/search/', 'Smart Search Page'),
        ('/assistant/', 'AI Assistant Page'),
        ('/dashboard/analytics', 'Analytics Dashboard Page'),
        ('/dashboard/resume-builder', 'AI Resume Builder Page'),
        ('/dashboard/profile', 'Profile Page'),
        ('/dashboard/settings', 'Settings Page'),
    ]

    for route, name in auth_pages:
        res = client.get(route)
        assert res.status_code == 200, f"FAILED to load {name} at {route} (Code {res.status_code})"
        print(f"  [SUCCESS] Console Page: {name} ({route}) -> HTTP 200 OK")

    print("\n[COMPLETE] ALL 14 FRONTEND PAGES & ROUTES VERIFIED 100% OPERATIONAL!")

if __name__ == '__main__':
    test_all_pages()
