from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

import pymysql
import bcrypt
import os
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.INFO)  # Log INFO and above levels

# Configurations for file uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')  # Folder to save uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Password',  # Change this to your actual DB password
    'database': 'urbanfinds'
}

# Function to get a database connection
def get_db_connection():
    try:
        connection = pymysql.connect(**db_config)
        print("Connected to the database")
        return connection
    except pymysql.MySQLError as e:
        print(f"Database connection failed: {e}")
        return None

# Home route
@app.route('/')
def index():
    return render_template('index.html')


#-----------------------------USER Login & Sign Up-----------------------------#
# Login route
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['loginEmail']
        password = request.form['loginPassword'].encode('utf-8')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()

                if result and bcrypt.checkpw(password, result[1].encode('utf-8')):
                    session['user_id'] = result[0]  # Store user ID in session
                    flash('Login successful!', 'success')
                    print('Login successful!, success')
                    return redirect(url_for('buyer_dashboard'))  # Redirect to cart page
                else:
                    flash('Invalid credentials. Please try again.', 'error')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Could not connect to the database.', 'error')

    return render_template('user_details.html')

# Signup route
@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form['signupName']
        mobile = request.form['signupNumber']
        email = request.form['signupEmail']
        password = request.form['signupPassword'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO users (name, mobile, email, password) VALUES (%s, %s, %s, %s)",
                               (name, mobile, email, hashed_password))
                connection.commit()
                flash('Account created successfully!', 'success')
                return render_template('user_details.html')
            except pymysql.MySQLError as e:
                flash('Error creating account. Email may already exist.', 'error')
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Could not connect to the database.', 'error')

    return render_template('user_details.html')


#-----------------------------SELLER Login & Sign Up-----------------------------#
# Login route
@app.route('/seller/login', methods=['GET', 'POST'])
def seller_login():
    print("Login route accessed")
    if request.method == 'POST':
        email = request.form['loginEmail']
        password = request.form['loginPassword'].encode('utf-8')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id, password FROM seller WHERE email = %s", (email,))
                result = cursor.fetchone()

                if result and bcrypt.checkpw(password, result[1].encode('utf-8')):
                    session['user_id'] = result[0]  # Store user ID in session
                    flash('Login successful!', 'success')
                    return redirect(url_for('seller_dashboard'))  # Redirect to cart page
                else:
                    flash('Invalid credentials. Please try again.', 'error')
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Could not connect to the database.', 'error')

    return render_template('seller_details.html')

# Signup route
@app.route('/seller/signup', methods=['GET', 'POST'])
def seller_signup():
    if request.method == 'POST':
        name = request.form['signupName']
        mobile = request.form['signupNumber']
        email = request.form['signupEmail']
        password = request.form['signupPassword'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO seller (name, mobile, email, password) VALUES (%s, %s, %s, %s)",
                               (name, mobile, email, hashed_password))
                connection.commit()
                # flash('Account created successfully!', 'success')
                return render_template('seller_details.html')
            except pymysql.MySQLError as e:
                flash('Error creating account. Email may already exist.', 'error')
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Could not connect to the database.', 'error')

    return render_template('seller_details.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))  # Redirect to the login page

# About page
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/items')
def items():
    return render_template('items.html')

@app.route('/sitevisit')
def sitevisit():
    return render_template('sitevisit.html')

@app.route('/seller_dashboard')
def seller_dashboard():
    return render_template('seller_dashboard.html')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/buyer_dashboard')
def buyer_dashboard():
    return render_template('buyer_dashboard.html')



@app.route('/upload_product', methods=['POST'])
def upload_product():
    # Get the form data
    name = request.form['name']
    category = request.form['category']
    price = int(request.form['price'])
    description = request.form.get('description')
    artist = request.form.get('artist')
    quantity = int(request.form['quantity'])

    # Handling file upload
    file = request.files['image']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        flash('No image selected', 'error')
        return redirect(request.url)

    # Insert product details into the database
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO lands 
                     (PropertyType, Category, Price, Address, OwnerName, Sqft, Image) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (name, category, price, description, artist, quantity, filename))
            connection.commit()
        flash('Product successfully uploaded', 'success')
        return render_template('seller_cart.html')
    except pymysql.MySQLError as e:
        flash('Error uploading product to the database.', 'error')
        print(f"Error: {e}")
    finally:
        connection.close()

    return redirect(url_for('seller_dashboard'))

@app.route('/open_plots')
def open_plots():
    # user_id = session.get('user_id')
    # print("user ID:",user_id)  # Get user ID from session
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            
            # Fetch all products in the 'Art' category
            sql = "SELECT * FROM lands WHERE Category = %s"
            cursor.execute(sql, ('Open Plots',))
            artworks = cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error fetching artworks: {e}")
        artworks = []
    finally:
        connection.close()

    # Pass the artworks data and user_id to the template
    return render_template('open_plots.html', artworks=artworks)



@app.route('/upload_appointment', methods=['POST'])
def upload_appointment():
    user_id = session.get('user_id')

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        if not product_id:
            flash('Product ID is missing', 'error')
            return redirect(request.url)

        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            appointment_date = request.form['date']
        except KeyError as e:
            flash(f'Missing field: {str(e)}', 'error')
            return redirect(request.url)

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = '''INSERT INTO appointments 
                         (user_id, product_id, name, email, phone, appointment_date) 
                         VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (user_id, product_id, name, email, phone, appointment_date))
                connection.commit()

                if cursor.rowcount > 0:
                    flash('Appointment successfully booked', 'success')
                    return redirect(url_for('thanks'))
                else:
                    flash('Failed to book appointment.', 'error')
        except pymysql.MySQLError as e:
            print(f"Error occurred: {e}")
            flash('Error booking appointment.', 'error')
        finally:
            connection.close()

    return redirect(url_for('index'))




@app.route('/apartments')
def apartments():
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Fetch all products in the 'Art' category
            sql = "SELECT * FROM lands WHERE category = %s"
            cursor.execute(sql, ('Apartments',))
            homedecors = cursor.fetchall()
            print("homedecors:",homedecors)
    except pymysql.MySQLError as e:
        print(f"Error fetching homedecors: {e}")
        homedecors = []
    finally:
        connection.close()

    # Pass the artworks data to the template
    return render_template('apartments.html', homedecors=homedecors)


@app.route('/villas')
def villas():
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Fetch all products in the 'Art' category
            sql = "SELECT * FROM lands WHERE category = %s"
            cursor.execute(sql, ('Villas',))
            toys = cursor.fetchall()
            print("toy:",toys)
    except pymysql.MySQLError as e:
        print(f"Error fetching toys: {e}")
        toys = []
    finally:
        connection.close()

    # Pass the artworks data to the template
    return render_template('villas.html', toys=toys)

@app.route('/seller_cart')
def seller_cart():
    seller_id = session.get('user_id') 
    print(seller_id)
     # Get the logged-in seller's ID from the session
    if not seller_id:
        flash("Please log in to view your appointments.", "error")
        return redirect(url_for('seller_login'))  # Redirect to login if no seller ID is found in session

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Fetch appointments for the logged-in seller where land ID matches the appointment's product ID
            sql = '''SELECT a.name, a.email, a.phone, a.appointment_date
FROM appointments a
JOIN lands l ON a.product_id = l.id
WHERE a.product_id IN (SELECT id FROM lands WHERE user_id = %s)'''
            cursor.execute(sql, (seller_id,))
            appointments = cursor.fetchall() 
            print(appointments)
             # Fetch all matching appointments

    except pymysql.MySQLError as e:
        print(f"Error fetching appointments: {e}")
        flash("An error occurred while retrieving your appointments.", "error")
        appointments = []  # Empty list in case of error

    finally:
        connection.close()

    return render_template('seller_cart.html', appointments=appointments)


# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# User details page
@app.route('/user_details')
def user_details():
    return render_template('user_details.html')


@app.route('/seller_details')
def seller_details():
    return render_template('seller_details.html')


# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)
