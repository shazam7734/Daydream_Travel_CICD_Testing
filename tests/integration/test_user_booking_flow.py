# tests/integration/test_user_booking_flow.py

import pytest
from app import app

@pytest.fixture
def client():
    """Flask test client setup with test config."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_and_login_user(client):
    """Tests registering a user and logging in with correct credentials."""
    response = client.post('/register', data={
        'email': 'integration@example.com',
        'password': 'TestPass123!'
    }, follow_redirects=True)
    assert b'Login' in response.data or b'Success' in response.data

    response = client.post('/login', data={
        'email': 'integration@example.com',
        'password': 'TestPass123!'
    }, follow_redirects=True)
    assert b'Dashboard' in response.data or b'logout' in response.data.lower()

def test_booking_process(client):
    """Tests the 2-step travel booking flow: travel details + payment."""
    client.post('/register', data={
        'email': 'bookme@example.com',
        'password': 'Secure123!'
    })
    client.post('/login', data={
        'email': 'bookme@example.com',
        'password': 'Secure123!'
    })

    # Step 1 – Enter travel info
    response_step1 = client.post('/book', data={
        'step': '1',
        'origin': 'Melbourne',
        'destination': 'Perth',
        'depart_date': '2025-08-01',
        'return_date': '2025-08-10',
        'passengers': '1'
    }, follow_redirects=True)
    assert b'Payment' in response_step1.data or b'card' in response_step1.data

    # Step 2 – Enter payment info
    response_step2 = client.post('/book', data={
        'step': '2',
        'card': '4111111111111111',
        'expiry': '12/30',
        'cvv': '123'
    }, follow_redirects=True)
    assert b'Booking confirmed' in response_step2.data or b'Dashboard' in response_step2.data

def test_dashboard_requires_login(client):
    """Verifies unauthenticated users cannot access the dashboard."""
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in response.data or b'Please log in' in response.data
