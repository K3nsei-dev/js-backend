# imported modules that are used in this project
import sqlite3
import hmac
from flask import Flask, request
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
import re
from datetime import *


# user class
class User(object):
    def __init__(self, id, email, password):  # initialising constructor function
        self.id = id
        self.email = email
        self.password = password


# products class
class Products(object):
    def __init__(self, product_name, product_type, product_price, product_description,
                 product_image):  # initialisation of constructor function
        self.product_name = product_name
        self.product_type = product_type
        self.product_price = product_price
        self.product_description = product_description
        self.product_image = product_image


# update project class
class UpdateProducts(object):
    def __init__(self):  # initialisation of constructor function
        self.conn = sqlite3.connect('products.db')
        self.cursor = self.conn.cursor()

    def add_product(self, value):  # add a product to the database
        add_query = "INSERT INTO products (product_name, product_type, product_price, product_description, product_image) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(add_query, value)

    def update_product(self, value, product_id):  # update a product in the database
        update_query = "UPDATE products SET product_name = ?, product_type = ?, product_price = ?, product_description = ?, product_image = ? WHERE product_id =" + str(
            product_id)
        self.cursor.execute(update_query, value)

    def delete_product(self, value):  # delete a product in the database
        productid = str(value)
        query = "DELETE FROM products WHERE product_id='" + productid + "'"
        self.cursor.execute(query)

    def get_products(self):  # get the products from the database
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

    def commit(self):  # committing to the database
        self.conn.commit()


# calling the class
products_db = UpdateProducts()


# function to create users table
def create_users():
    conn = sqlite3.connect('products.db')  # connecting to the database
    print("Database Created Successfully")

    conn.execute(
        "CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT,"  # sqlite syntax to create a table called users
        "first_name TEXT NOT NULL,"
        "last_name TEXT NOT NULL,"
        "email TEXT NOT NULL,"
        "cell_num INTEGER NOT NULL,"
        "password TEXT NOT NULL)")
    print("User Table Created Successfully")  # printing to the console
    conn.close()  # closing the connection


# function to create products table
def create_products():
    conn = sqlite3.connect('products.db')  # connecting to the database

    conn.execute(
        "CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY AUTOINCREMENT,"  # sqlite syntax for creating a table called products
        "product_name TEXT NOT NULL,"
        "product_type TEXT NOT NULL,"
        "product_price INTEGER NOT NULL,"
        "product_description TEXT NOT NULL,"
        "product_image TEXT NOT NULL)")
    print("Products Table Created Successfully")  # printing to the console
    conn.close()  # closing the connection


# calling the functions
create_users()
create_products()


# function to collect all the information from the users table
def fetch_users():
    with sqlite3.connect('products.db') as conn:  # connecting to the database
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")  # selecting all the data from the users table
        users = cursor.fetchall()  # fetching all the data

        new_data = []  # an empty list

        # looping through the data
        for data in users:
            new_data.append(User(data[0], data[3], data[5]))  # appending the data to the empty list
    return new_data


# calling the users function
users = fetch_users()

# looping through data to get peoples emails and passwords for logging in
username_table = {u.email: u for u in users}
user_id_table = {u.id: u for u in users}


# function to authenticate login
def authenticate(email, password):
    user = username_table.get(email, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'),
                                    password.encode('utf-8')):  # comparing the entered password and adding security
        return user


def identity(number):
    user_id = number['identity']
    return user_id_table.get(user_id, None)


# initialising flask app
app = Flask(__name__)
# web browser security
CORS(app)
app.config['SECRET_KEY'] = 'super-secret'
# flask send email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lca.pointofsale@gmail.com'
app.config['MAIL_PASSWORD'] = 'lifechoices2021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# date time variable
now = datetime.now()

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# route that lets someone register themselves
@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    response = {}  # an empty dictionary

    regex_email = request.form.get('email')  # getting the email from the form

    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'  # regular expression for validating email

    # verifying email address
    if re.search(regex, regex_email):
        pass
    else:
        raise Exception("Invalid Email Address, Please Try Again!")

    # error trapping/handling
    try:
        name = str(request.form.get('first_name'))
        surname = str(request.form.get('last_name'))
        number = int(request.form.get('cell_num'))
        new_num = request.form.get('cell_num')
        e_add = request.form.get('email')
        passwd = request.form.get('password')

        if len(name) == 0 or len(surname) == 0 or len(new_num) == 0 or len(e_add) == 0 or len(passwd) == 0:
            raise Exception("Please Fill In Each Section Correctly")
        elif len(new_num) < 10:
            raise Exception("Please Enter A 10 Digit Cell Number")
        elif type(name) == int or type(surname) == int:
            raise TypeError("Use Characters Only For Your Name Please")
        elif type(number) == str:
            raise TypeError("Use Digits Only For Your Cell Number Please")
        else:
            pass
    except ValueError:
        raise TypeError("Please Use The Correct Values For Each Section")

    # inserting data into the users table
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        cell_num = request.form['cell_num']
        password = request.form['password']

        # connecting to the database
        with sqlite3.connect('products.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user (first_name,"  # sqlite syntax for inserting into the users table
                           "last_name,"
                           "email,"
                           "cell_num,"
                           "password) VALUES (?, ?, ?, ?, ?)", (first_name, last_name, email, cell_num, password))
            # pushing the data to the database
            conn.commit()

            # initialising flask mail
            mail = Mail(app)

            # content of the email
            msg = Message("User Registration Details", sender='lca.pointofsale@gmail.com', recipients=[email])
            msg.body = "Thank You For Registering With Life Choices Point Of Sales!" + "\n" + "\n" + "Your Details Are As Follows:" + "\n" + "\n" + "Username:" + " " + \
                       email + "\n" + "Password:" + " " + password + "\n" + "\n" + "Thank You For Choosing Life Choices Point Of Sale! Please Enjoy The Experience!"

            # sending the email
            mail.send(msg)

            response["message"] = "Success"  # a message appended to the empty dictionary
            response["status_code"] = 201  # status code appended to the empty dictionary

        return response  # returning the response and if it is successful it will display the above code


# route for individual to check their profile
@app.route('/user-profile/<int:user_id>')
@cross_origin()
# @jwt_required()  # used as a security with token authorization
# function to retrieve someones profile
def user_profile(user_id):
    response = {}

    with sqlite3.connect('products.db') as conn:  # connecting to the database
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user WHERE user_id =" + str(user_id))  # selecting all the data where the id matches
        users = cursor.fetchone()  # fetching one user from the database

        response['data'] = users  # displaying the users data in json format
        response['status_code'] = 200
        response['message'] = "Successfully Viewed Profile"
    return response


# route for adding products
@app.route('/add-products', methods=["POST"])
@cross_origin()
# @jwt_required()
# function to add products
def add_products():
    add_db = UpdateProducts()  # calling the class
    response = {}

    # error trapping/handling
    try:
        name = str(request.form['product_name'])
        p_type = str(request.form['product_type'])
        price = str(request.form['product_price'])
        new_price = request.form['product_price']
        description = str(request.form['product_description'])
        image = str(request.form['product_image'])

        if len(name) == 0 or len(p_type) == 0 or len(new_price) == 0 or len(description) == 0 or len(image) == 0:
            raise Exception("Please Fill In Each Section Correctly")
        elif type(name) == int or type(p_type) == int:
            raise TypeError("Use Characters Only For Name and Type Please")
        elif type(price) == int:
            raise TypeError("Use Digits Only For Price Please")
        else:
            pass
    except ValueError:
        raise TypeError("Please Use The Correct Values For Each Section")

    if request.method == "POST":  # inserting data into the database
        product_name = request.form['product_name']
        product_type = request.form['product_type']
        product_price = request.form['product_price']
        product_description = request.form['product_description']
        product_image = request.form['product_image']

        values = (product_name, product_type, product_price, product_description,
                  product_image)  # values of what must go in the database

        add_db.add_product(values)
        add_db.commit()  # committing it to the database

        response['status_code'] = 200
        response['message'] = "Product Added Successfully"

        return response


# route to update your products
@app.route('/update-products/<int:product_id>', methods=['PUT'])
@cross_origin()
# @jwt_required()
# function to update products
def update_product(product_id):
    response = {}

    try:  # error trapping/handling
        name = str(request.form['product_name'])
        p_type = str(request.form['product_type'])
        price = int(request.form['product_price'])
        description = str(request.form['product_description'])
        image = str(request.form['product_image'])
        new_price = request.form['product_price']

        if len(name) == 0 or len(p_type) == 0 or len(new_price) == 0 or len(description) == 0 or len(image) == 0:
            raise Exception("Please Fill in Each Section Correctly")
        elif type(price) == str:
            raise KeyError("Please Use Digits for Price")
        elif type(name) == int or type(p_type) == int or type(description) == int or type(image) == int:
            raise KeyError("Please Use Characters For Name, Type, Description, and Image")
    except ValueError:
        raise ValueError("Incorrect Value Used For Sections")

    up_db = UpdateProducts()  # calling the class

    if request.method == "PUT":  # inserting data into the database
        product_name = request.json['product_name']
        product_type = request.json['product_type']
        product_price = request.json['product_price']
        product_description = request.json['product_description']
        product_image = request.json['product_image']

        values = (product_name, product_type, product_price, product_description,
                  product_image)  # values of what must go into the database

        up_db.update_product(values, product_id)

        up_db.commit()  # committing the data to the database

    response['message'] = "Updated Products"
    response['status_code'] = 200

    return response


# route to view the products
@app.route('/view-products')
@cross_origin()
# function to view products
def view_products():
    response = {}

    view_db = UpdateProducts()  # calling the class

    data = view_db.get_products()  # getting the data from the class function

    response['status_code'] = 200
    response['data'] = data

    return response


# route to delete product
@app.route('/delete-product/<int:product_id>', methods=["POST"])
@cross_origin()
# @jwt_required()
# function to delete the product
def delete_product(product_id):
    response = {}

    del_db = UpdateProducts()  # calling the class

    del_db.delete_product(product_id)  # selecting which data to be deleted based off of the class function

    del_db.commit()  # committing the changes to the database

    response['status_code'] = 200
    response['message'] = "Product Deleted Successfully"

    return response


# to run the program
if __name__ == '__main__':
    app.run(debug=True)