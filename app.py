from flask import Flask, render_template, request, redirect, url_for, session, flash
import re, json, os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USERS_FILE = 'users.json'
BOOKINGS_FILE = 'bookings.json'

def load_data(file, default):
    """
    Load JSON data from a specified file path.

    If the file doesn't exist, create it with the provided default data.

    Parameters:
    ----------
    file : str
        Path to the JSON file to load data from
    default : dict or list
        Default data to save if the file doesn't exist

    Returns:
    -------
    dict or list
        The loaded data from the JSON file
    """
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump(default, f)
    with open(file, 'r') as f:
        return json.load(f)

def save_data(file, data):
    """
    Save data to a JSON file.

    Args:
        file (str): The path to the file where data will be saved.
        data (dict or list): The data to be saved in JSON format.

    Returns:
        None

    Note:
        This function will overwrite the contents of the file if it already exists.
        The data is formatted with an indent of 4 spaces and non-serializable objects 
        are converted to strings using the str() function.
    """
    with open(file, 'w') as f:
        json.dump(data, f, indent=4, default=str)

users_db = load_data(USERS_FILE, {})
bookings_db = load_data(BOOKINGS_FILE, [])

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_strong_password(password):
    """
    Checks if a password meets the criteria for being strong.

    A strong password must:
    1. Be at least 8 characters long
    2. Contain at least one digit
    3. Contain at least one special character from '!@#$%^&*()'

    Parameters:
    ----------
    password : str
        The password string to check

    Returns:
    -------
    bool
        True if the password meets all criteria, False otherwise
    """
    return (
        len(password) >= 8 and
        any(c.isdigit() for c in password) and
        any(c in "!@#$%^&*()" for c in password)
    )

def validate_payment(card, expiry, cvv):
    """
    Validates credit card payment information.

    This function checks if a credit card is valid by verifying:
    1. The card number starts with 4 or 5 (Visa or MasterCard) and is 16 digits long
    2. The expiry date is in the future and in valid format (MM/YY)
    3. The CVV is a 3-digit number

    Parameters:
    ----------
    card : str
        The credit card number to validate
    expiry : str
        The expiry date in format "MM/YY"
    cvv : str
        The 3-digit CVV code

    Returns:
    -------
    str
        "valid" if all validations pass, otherwise an error message describing the issue
    """
    if not (card.startswith("4") or card.startswith("5")) or len(card) != 16:
        return "Invalid card number"
    try:
        if datetime.strptime(expiry, "%m/%y") < datetime.now():
            return "Card expired"
    except ValueError:
        return "Invalid expiry date"
    if not (cvv.isdigit() and len(cvv) == 3):
        return "Invalid CVV"
    return "valid"

def login_required(f):
    """
    A decorator to ensure that a user is logged in before accessing a route.

    This decorator checks if the user's email is in the session. If the email
    is not present, it flashes a message indicating that login is required and
    redirects the user to the login page. Otherwise, it allows the request to
    proceed to the decorated function.

    Usage:
        @login_required
        def protected_route():
            # This route can only be accessed by logged-in users
            pass

    Args:
        f (function): The view function to be decorated.

    Returns:
        function: The decorated function that checks if the user is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash("Login required.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """
    Main route for the application.

    Returns:
        str: Rendered HTML template for the index page.
    """
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration functionality.

    This function processes the user registration form submitted via POST method.
    It validates the email format, checks if the email already exists in the database,
    verifies password strength, and saves valid user credentials to the database.

    Returns:
        If POST and registration successful: Redirects to the login page
        Otherwise: Renders the registration template
        
    Flash messages:
        "Email already exists." - When the provided email is already registered
        "Invalid email format." - When the email doesn't meet format requirements
        "Weak password." - When the password doesn't meet strength requirements
        "Account created." - When registration is successful
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users_db:
            flash("Email already exists.")
        elif not is_valid_email(email):
            flash("Invalid email format.")
        elif not is_strong_password(password):
            flash("Weak password.")
        else:
            users_db[email] = {'password': password}
            save_data(USERS_FILE, users_db)
            flash("Account created.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login functionality.

    This function processes login attempts through both GET and POST methods.
    For POST requests, it validates the provided email and password against 
    the users database. If credentials are valid, it creates a session for 
    the user and redirects to the dashboard. Otherwise, it displays an error 
    message.

    Returns:
        flask.Response: Either a redirect to the dashboard page upon successful
        login or the login page template with appropriate flash messages.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users_db and users_db[email]['password'] == password:
            session['email'] = email
            session['last_active'] = datetime.now().isoformat()
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logs the user out of the application.

    This function clears the user's session data, displays a flash message
    confirming the logout, and redirects the user to the index page.

    Returns:
        A redirect response to the index page.
    """
    session.clear()
    flash("Logged out.")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Renders the dashboard page showing user's bookings.

    This function filters the bookings database to find bookings associated with the
    current user's email from the session, then renders the dashboard template with
    these bookings.

    Returns:
        flask.Response: Rendered dashboard.html template with the user's bookings.
    """
    user_bookings = [b for b in bookings_db if b['email'] == session['email']]
    return render_template('dashboard.html', bookings=user_bookings)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    """
    Handle the booking process for travel reservations.
    This function manages a two-step booking process:
    1. Collect travel details (origin, destination, dates, passengers)
    2. Process payment information and create the booking
    The function handles both GET and POST requests:
    - GET: Displays the initial booking form
    - POST: Processes form submissions for each step
    Returns:
        For GET requests: Renders the 'book.html' template for initial form
        For POST step 1: Renders the 'book_payment.html' template for payment details
        For POST step 2: 
            - If payment is valid: Redirects to dashboard with booking confirmation
            - If payment is invalid: Returns to payment page with error message
    Session data:
        - Stores travel details between steps in session['booking']
        - Uses session['email'] to associate booking with user
    Side effects:
        - Adds new booking to bookings_db
        - Saves updated bookings to disk
        - Flashes confirmation or error messages to the user
    """
    if request.method == 'POST':
        # Check which step of the booking process we're in
        step = request.form.get('step', '1')
        
        if step == '1':
            # Store the travel details in the session
            session['booking'] = {
                'origin': request.form['origin'],
                'destination': request.form['destination'],
                'depart_date': request.form['depart_date'],
                'return_date': request.form.get('return_date', ''),
                'passengers': int(request.form['passengers'])
            }
            return render_template('book_payment.html')
            
        elif step == '2':
            # Process payment and create booking
            card = request.form['card']
            expiry = request.form['expiry']
            cvv = request.form['cvv']
            
            result = validate_payment(card, expiry, cvv)
            if result != "valid":
                flash(result)
                return render_template('book_payment.html')
            
            # Create booking with all details
            ref = f"BK{len(bookings_db)+1:04d}"
            booking_details = session.get('booking', {})
            
            new_booking = {
                "email": session['email'],
                "ref": ref,
                "timestamp": datetime.now().isoformat(),
                "origin": booking_details.get('origin', ''),
                "destination": booking_details.get('destination', ''),
                "depart_date": booking_details.get('depart_date', ''),
                "return_date": booking_details.get('return_date', ''),
                "passengers": booking_details.get('passengers', 1)
            }
            
            bookings_db.append(new_booking)
            save_data(BOOKINGS_FILE, bookings_db)
            
            # Clear the temporary booking data from session
            session.pop('booking', None)
            
            flash(f"Booking confirmed: {ref}")
            return redirect(url_for('dashboard'))
    
    # GET request - show the first booking step
    return render_template('book.html')

@app.route('/cancel/<ref>')
@login_required
def cancel(ref):
    """
    Cancel a booking based on the reference number.
    
    This function cancels a booking if:
    - The booking reference matches the provided ref
    - The booking email matches the current user's email
    - The cancellation is requested more than 24 hours before the flight
    
    Args:
        ref (str): The reference number of the booking to cancel
        
    Returns:
        Response: A redirect to the dashboard page
        
    Side effects:
        - Removes the booking from bookings_db if conditions are met
        - Saves the updated bookings to the storage file
        - Flashes appropriate messages for success or failure cases
    """
    for booking in bookings_db:
        if booking['ref'] == ref and booking['email'] == session['email']:
            timestamp = datetime.fromisoformat(booking['timestamp'])
            if (datetime.now() - timestamp).total_seconds() > 86400:
                flash("Cannot cancel within 24 hours of flight.")
            else:
                bookings_db.remove(booking)
                save_data(BOOKINGS_FILE, bookings_db)
                flash("Booking cancelled.")
            break
    else:
        flash("Booking not found.")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
