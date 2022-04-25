from flask import Flask, render_template, request, json, flash, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_access_cookies, set_access_cookies, unset_jwt_cookies

# -----------------------
# use console, python
# import secrets
# secrets.token_hex(16)  # to generate some random hex


app = Flask(__name__)
app.secret_key = 'adb24bb904544d1f488714d369c9de83'
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config["JWT_SECRET_KEY"] = 'adb24bb904544d1f488714d369c9de83'
# only in production
app.config["JWT_COOKIE_SECURE"] = False

jwt = JWTManager(app)

lab3database = 'mongodb+srv://myadmin:QHEKhh4gnAGz4Vm@cluster0.xowry.mongodb.net/lab3'
mongo1 = PyMongo(app, uri=lab3database)
resturaunts = mongo1.db.Resturaunts  # collection for restaurants
users = mongo1.db.Users  # collection for the users


@app.route("/")
@app.route("/index")
@app.route("/home")
# decorate functions to reload our routers
def index():
    return render_template("index.html")

# Signing Up new Users


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']

        if users.find_one({'email': email}):
            return jsonify(message="Email already exists, please login"), 401
        else:
            user = {}
            user['email'] = email
            user['username'] = data['username']
            user['password'] = generate_password_hash(
                data['password'], method='sha256')
            users.insert_one(user)  # Register the user in databse

            # Generate access token after signup
            access_token = create_access_token(identity=email)
            response = jsonify(message="sign up successfull")
            set_access_cookies(response, access_token)
            return response

    # if GET request, render the sign up page
    else:
        return render_template("signup.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']

        if users.find_one({'email': email}):
            check_email = users.find_one({'email': email})
            # check the password against the email
            if check_password_hash(check_email['password'], password):
                response = jsonify(message="login successfull")
                access_token = create_access_token(identity=email)
                set_access_cookies(response, access_token)
                return response
            else:
                return jsonify(message="wrong email or password"), 401
        else:
            return jsonify(message='wrong email or password'), 401
    # if GET request, render the sign up page
    else:
        return render_template("login.html")

# Logout route to unset the cookies


@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

# route for handling restaurant request


@app.route("/restaurant", methods=['GET'])
@jwt_required(optional=True)
def restaurant():
    current_user = get_jwt_identity()
    if current_user:
        return render_template("restaurant.html", resp=current_user)
    else:
        return redirect(url_for('login'))

# route for posting new favourite restaurant


@app.route('/createRestaurant', methods=['POST'])
def createRestaurant():
    resturaunt = {}
    resturaunt["name"] = request.form.get("rest")
    resturaunt["location"] = request.form.get("loc")
    resturaunt["food"] = request.form.get("food")
    oID = resturaunts.insert_one(resturaunt)
    print(oID)
    theResturaunts = list(resturaunts.find({}))
    return "<h1>Submitted Successfully</h1>"


@app.route('/view', methods=['GET'])
@jwt_required()
def view():
    current_user = get_jwt_identity()
    user = users.find_one({"email": current_user})
    if user:
        output = list(resturaunts.find({}, {"_id": 0}))
        return jsonify(resturaunts=output), 200
    else:
        return jsonify(message="sorry no restaurant was found"), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
