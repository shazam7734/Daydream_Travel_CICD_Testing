
import pytest
from app import app

@pytest.fixture
def client():
    """
    Pytest fixture that creates a test client for Flask application.

    This fixture configures the Flask application for testing and provides
    a test client that can be used in tests to make requests to the application.

    Returns:
        FlaskClient: A Flask test client instance that can be used to simulate 
                    HTTP requests to the application.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# TC001-REG: Verify user can register with valid username and password
def test_register_valid_user(client):
    """
    Test function to verify the registration process with valid user credentials.

    This test posts a registration form with valid email and password to the '/register' 
    endpoint and checks if the response contains either 'Login' or 'Success' text, 
    indicating successful registration.

    Parameters:
        client (Flask test client): The Flask test client fixture to make HTTP requests.

    Returns:
        None
    """
    response = client.post('/register', data={
        'email': 'newuser123@example.com',
        'password': 'Secure123!'
    }, follow_redirects=True)
    assert b'Login' in response.data or b'Success' in response.data

# TC002-REG: Verify registration fails with duplicate username
def test_register_duplicate_user(client):
    """
    Test registering a duplicate user.

    This test verifies that the registration system properly handles duplicate 
    registration attempts with the same email address. It performs the following steps:
    1. Registers a user with a specific email address
    2. Attempts to register another user with the same email but different password
    3. Verifies that the system returns an error message indicating the email is already in use

    Parameters:
        client: Flask test client fixture

    Returns:
        None
    """
    # First registration
    client.post('/register', data={
        'email': 'testuser@example.com',
        'password': 'Password123!'
    })
    # Attempt duplicate
    response = client.post('/register', data={
        'email': 'testuser@example.com',
        'password': 'AnotherPass123'
    })
    assert b'Email already exists' in response.data

# TC004-LOGIN: Verify login with valid credentials
def test_login_valid_user(client):
    """
    Tests the login functionality for a valid registered user.

    This function:
    1. Registers a new user with valid credentials
    2. Attempts to log in using those same credentials
    3. Verifies that the login was successful by checking for the presence of 'login' in the response data

    Args:
        client: The Flask test client fixture

    Returns:
        None

    Note: This test depends on the registration functionality working correctly.
    """
    # Ensure user exists
    client.post('/register', data={
        'email': 'validuser@example.com',
        'password': 'Secure123'
    })
    response = client.post('/login', data={
        'email': 'validuser@example.com',
        'password': 'Secure123'
    }, follow_redirects=True)
    assert b'login' in response.data

# TC005-LOGIN: Verify login fails with incorrect password
def test_login_wrong_password(client):
    """
    Test user login function with incorrect password.

    This test performs the following steps:
    1. Registers a new user with email 'wrongpassuser@example.com' and password 'RightPass123'
    2. Attempts to login with the correct email but wrong password 'WrongPass'
    3. Verifies that the response contains either 'Invalid' or 'Error' message

    Parameters:
        client: Flask test client fixture

    Returns:
        None
    """
    client.post('/register', data={
        'email': 'wrongpassuser@example.com',
        'password': 'RightPass123'
    })
    response = client.post('/login', data={
        'email': 'wrongpassuser@example.com',
        'password': 'WrongPass'
    })
    assert b'Invalid' in response.data or b'Error' in response.data

# TC006-BOOK: Verify travel booking with valid input
def test_booking_two_step_process(client):
    """
    Test the two-step booking process in the Daydream application.
    This test verifies the complete booking flow from login to confirmation:
    1. Registers a new user and logs them in
    2. Submits travel details in the first step of booking (origin, destination, dates, etc.)
    3. Submits payment information in the second step
    4. Verifies that the booking is confirmed successfully
    The test uses assertions to check the expected responses at each step:
    - Successful login 
    - Transition to payment page after travel details
    - Booking confirmation after payment submission
    """
    # Register and login the user
    client.post('/register', data={
        'email': 'bookuser@newexample.com',
        'password': 'Secure123@123'
    })
    response = client.post('/login', data={
        'email': 'bookuser@newexample.com',
        'password': 'Secure123@123'
    }, follow_redirects=True)
    assert b'login' in response.data

    # Step 1: Submit travel details
    step1_data = {
        'step': '1',
        'origin': 'Melbourne',
        'destination': 'Sydney',
        'depart_date': '2025-07-01',
        'return_date': '2025-07-10',
        'passengers': '2'
    }
    response_step1 = client.post('/book', data=step1_data, follow_redirects=True)    
    assert b'Payment' in response_step1.data or b'card' in response_step1.data  # assumes book_payment.html mentions payment/card

    # Step 2: Submit payment info
    step2_data = {
        'step': '2',
        'card': '4111111111111111',
        'expiry': '12/30',
        'cvv': '123'
    }
    response_step2 = client.post('/book', data=step2_data, follow_redirects=True)
    
    assert b'Booking confirmed' in response_step2.data or b'Dashboard' in response_step2.data



# TC012-SESS: Verify dashboard access is restricted without login
def test_dashboard_requires_login(client):
    """
    Tests that the dashboard page requires login.

    This test function verifies that when an unauthenticated user attempts to access
    the dashboard page, they are redirected to the login page.

    Parameters:
    ----------
    client : Flask test client
        The Flask test client fixture used to make requests to the application

    Returns:
    -------
    None
        This test passes if the login page is shown when accessing the dashboard
        without authentication
    """
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Login' in response.data
