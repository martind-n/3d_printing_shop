import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date

from helpers import apology, login_required, usd

# File uploading info
UPLOAD_FOLDER = './static/files'

# Configure application
app = Flask(__name__)

# Set up file uploading app
    # File upload path
app.config['UPLOAD_PATH'] = UPLOAD_FOLDER
    # File max size
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # File extensions allowed
app.config['UPLOAD_EXTENSIONS'] = ['.stl']

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///threedprinting.db")


@app.route("/")
#@login_required
def index():
    """Show 3d printing homepage"""

    printers = db.execute("SELECT * FROM products WHERE category='printer'")

    for printer in printers:
        printer["price_usd"] = usd(printer["price"])

    # Display user's name in case user is registered
    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Redirect user to home page
            return render_template("index.html", name=session["name"], cart_count=0, printers=printers)


        # Redirect user to home page
        return render_template("index.html", name=session["name"], cart_count=cart_count[0]["SUM (quantity)"], printers=printers)

    else:
        return render_template("index.html", printers=printers)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        email = request.form.get("email")
        name = request.form.get("name")
        last_name = request.form.get("last_name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure email was submitted
        if not email:
            return apology("must provide email", 403)

        # Ensure name was submitted
        if not name:
            return apology("must provide name", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Ensure confirmation pasword has been submitted
        elif not confirmation:
            return apology("must confirm password", 403)

        # Ensure password and confirmation match
        elif (confirmation != password):
            return apology("Password and confirmation do not match", 403)

        # Check email is available
        status = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        # If email is already taken, query will return one row for that username, so status will have a value
        if status:
            return apology("email already registered", 403)

        # If email is not taken, query will return null
        else:
            # Hash user's password
            password_hash = generate_password_hash(password)

            # Insert new user name
            db.execute("INSERT INTO users (email, hash, name, last_name) VALUES (:email, :password, :name, :last_name)",
                email=email, password=password_hash, name=name, last_name=last_name)

        # Query database for id
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember user name
        session["name"] = rows[0]["name"]

        # Show an alert to the user letting him/her registration was successful
        flash('Registered!')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember user name
        session["name"] = rows[0]["name"]


        # Show an alert to welcome the user back
        flash('Welcome back!')

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def Change_Password():
    """Change user password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Ensure Old Password was submitted
        if not old_password:
            return apology("must provide old password", 403)

        # Ensure password was submitted
        elif not new_password:
            return apology("must provide password", 403)

        # Ensure confirmation pasword has been submitted
        elif not confirmation:
            return apology("must confirm password", 403)

        # Ensure password and confirmation match
        elif (confirmation != new_password):
            return apology("Password and confirmation do not match", 403)

        # Check if old password is OK ->

        # Get ID from users table for current session
        user_id = session["user_id"]

        # Get current password
        old_hash_password = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=user_id)

        # Check if old password matches with user input
        if check_password_hash(old_hash_password[0]["hash"], old_password):

            # Hash user's new password
            password_hash = generate_password_hash(new_password)

            # Update user's password to the new password
            db.execute("UPDATE users SET hash=:password WHERE id=:user_id", password=password_hash, user_id=user_id)

        # If doesn't match
        else:
            return apology("Old Password is not valid", 403)

        # Show an alert to the user letting him/her know password has been changed
        flash('Password changed!')

        # Redirect user to home page
        return render_template("index.html", name=old_hash_password[0]["name"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        # Get user name
        username = db.execute("SELECT name FROM users WHERE id=:user_id", user_id=session["user_id"])

        return render_template("change_password.html", name=session["name"])


@app.route("/search", methods=["POST"])
def search():
    """Search for products"""

    # Get the string to search
    keyword = '%' + request.form.get("search") + '%'

    # Search te DB for terms like keyword
    products = db.execute("SELECT * FROM products WHERE description LIKE (:keyword) OR title LIKE (:keyword)", keyword=keyword)

    print(products)

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if not products:

            if cart_count[0]["SUM (quantity)"] == None:

                # Show no results page
                return render_template("prompts.html", name=session["name"], missing="products", cart_count=0)

            else:
                return render_template("prompts.html",name=session["name"], missing="products", cart_count=cart_count[0]["SUM (quantity)"])

        else:

            # Get price in USD
            for product in products:
                product["price_usd"] = usd(product["price"])

            if cart_count[0]["SUM (quantity)"] == None:

                # Show no results page
                return render_template("shop.html", name=session["name"], products=products, cart_count=0)

            else:
                return render_template("shop.html", name=session["name"], products=products, cart_count=cart_count[0]["SUM (quantity)"])
    else:
        if not products:

            # Show no results page
            return render_template("prompts.html", missing="products")

        else:

            # Get price in USD
            for product in products:
                product["price_usd"] = usd(product["price"])

            return render_template("shop.html", products=products)


@app.route("/shop_all", methods=["GET"])
#@login_required
def shop_all():
    """Show all the items"""

    if session:

            # Get cart status for the active user
            cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

            # Get all the products in the DB
            products = db.execute("SELECT * FROM products WHERE id <> 0" )

            # Convert price to USD format
            for product in products:
                product["price_usd"] = usd(product["price"])

            if cart_count[0]["SUM (quantity)"] == None:

                # Display info
                return render_template("shop.html", products=products, name=session["name"], cart_count=0)

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the products in the DB
        products = db.execute("SELECT * FROM products WHERE id <> 0" )

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/shop", methods=["GET"])
#@login_required
def shop():
    """Show all the items but filaments"""

    if session:

            # Get cart status for the active user
            cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

            # Get all the "extruders" in the DB
            products = db.execute("SELECT * FROM products WHERE category<>'filament ABS' AND category<>'filament PLA' AND category<>'filament PETG' AND category<>'filament nylon' AND category<>'filament TPU' AND category<>'filament support' AND id<>0" )

            # Convert price to USD format
            for product in products:
                product["price_usd"] = usd(product["price"])

            if cart_count[0]["SUM (quantity)"] == None:

                # Display info
                return render_template("shop.html", products=products, name=session["name"], cart_count=0)

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category<>'filament ABS' AND category<>'filament PLA' AND category<>'filament PETG' AND category<>'filament nylon' AND category<>'filament TPU' AND category<>'filament support' AND id<>0" )

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/extruders", methods=["GET"])
#@login_required
def extruders():
    """List all the extruders"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='extruder'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='extruder'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/hotends", methods=["GET"])
#@login_required
def hotends():
    """List all the hotends"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='hotend'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='hotend'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/nozzles", methods=["GET"])
#@login_required
def nozzles():
    """List all the nozzles"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='nozzle'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='nozzle'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/controllers", methods=["GET"])
#@login_required
def controllers():
    """List all the controllers"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='controller'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='controller'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/filament", methods=["GET"])
#@login_required
def filament():
    """List all the filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category LIKE 'filament%'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category LIKE 'filament%'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/pla", methods=["GET"])
#@login_required
def pla():
    """List all the PLA filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament PLA'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament PLA'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/abs", methods=["GET"])
#@login_required
def abs_():
    """List all the ABS filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament ABS'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament ABS'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/petg", methods=["GET"])
#@login_required
def petg():
    """List all the PETG filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament PETG'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament PETG'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/nylon", methods=["GET"])
#@login_required
def nylon():
    """List all the nylon filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament nylon'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament nylon'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/tpu", methods=["GET"])
#@login_required
def tpu():
    """List all the TPU filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament TPU'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament TPU'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/support_materials", methods=["GET"])
#@login_required
def support_materials():
    """List all the support filaments"""

    if session:

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament support'")
        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Display info
            return render_template("shop.html", products=products, name=session["name"], cart_count=0)

        # Display info
        return render_template("shop.html", products=products, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:

        # Get all the "extruders" in the DB
        products = db.execute("SELECT * FROM products WHERE category='filament support'")

        # Convert price to USD format
        for product in products:
            product["price_usd"] = usd(product["price"])

        # Display info
        return render_template("shop.html", products=products)


@app.route("/details/<product_sku>", methods=["GET", "POST"])
#@login_required
def details(product_sku):
    """List item details"""

    if request.method == "GET":

        if session:

            # Get cart status for the active user
            cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

            if float(product_sku) > 1000:

                # Get produt detailed info
                product = db.execute("SELECT * FROM products WHERE sku=:item", item=product_sku)

                # Get product specs
                specs = db.execute("SELECT * FROM specs WHERE prod_id=:prod_id", prod_id=product[0]["id"])

                # Convert price to USD format
                product[0]["price_usd"] = usd(product[0]["price"])

            else:

                # Get print detailed info
                product = db.execute("SELECT * FROM print WHERE sku=:item AND user_id=:user_id", item=product_sku, user_id=session["user_id"])

                # Adding missing files in "print" table, in order to correctly render info in "details" page
                product[0]["title"] = "Printing Job"
                product[0]["description"] = "We print your files!"
                product[0]["link"] = "/static/images/printing_job.jpg"

                # Get print specs
                specs = db.execute("SELECT * FROM print WHERE user_id=:user_id AND sku=:sku", user_id=session["user_id"], sku=product_sku)

                # Convert price to USD format
                product[0]["price_usd"] = usd(product[0]["total"])

            if cart_count[0]["SUM (quantity)"] == None:

                # Display info
                return render_template("details.html", name=session["name"], product=product, specs=specs, cart_count=0)

            # Display the info
            return render_template("details.html", name=session["name"], product=product, specs=specs, cart_count=cart_count[0]["SUM (quantity)"])

        else:

            # Get produt detailed info
            product = db.execute("SELECT * FROM products WHERE sku=:item", item=product_sku)

            #Get the specs for the item selected
            specs = db.execute("SELECT * FROM specs WHERE prod_id=:prod_id", prod_id=product[0]["id"])

            # Convert price to USD format
            product[0]["price_usd"] = usd(product[0]["price"])

            # Display the info
            return render_template("details.html", product=product, specs=specs)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    """Add items into cart from product details"""

    # Make sure cart exists
    if "cart" not in session:
        session["cart"]=[]

    if request.method == "POST":

        quantity = float(request.form.get("prod_stock_2"))

        id = request.form.get("id")

        if id:
            session["cart"].append(id)

        # Get product details
        product = db.execute("SELECT * FROM products WHERE id=:prod_id", prod_id=id)

        # Check if item is already in cart
        item = db.execute("SELECT quantity FROM cart WHERE prod_id=:prod_id", prod_id=id)

        if not item:

            # Insert new items to cart
            db.execute("INSERT INTO cart (user_id, prod_id, title, price, quantity, link, total, sku) VALUES (:user_id, :prod_id, :title, :price, :quantity, :link, :total, :sku)",
            user_id=session["user_id"], prod_id=product[0]["id"], title=product[0]["title"], price=product[0]["price"], quantity=quantity, link=product[0]["link"],
            total=quantity*float(product[0]["price"]), sku=product[0]["sku"])

        # Update items into the cart
        else:
            item[0]["quantity"] += quantity


            db.execute("UPDATE cart SET quantity=:quantity, total=:total WHERE user_id=:user_id AND prod_id=:prod_id ",  user_id=session["user_id"], prod_id=product[0]["id"],
            quantity=item[0]["quantity"], total=item[0]["quantity"]*product[0]["price"])

        return redirect("/cart")

    else:

         # Get elements in cart
        cart = db.execute("SELECT * FROM products JOIN cart ON id=prod_id WHERE id IN (SELECT prod_id FROM cart WHERE user_id=:user_id)", user_id=session["user_id"])

        # Get elements in cart count
        cart_count = db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

        # Get total amount in cart
        cart_amount = db.execute("SELECT SUM (total) FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Show cart page
            return render_template("prompts.html", name=session["name"], missing="cart", cart_count=0)

        # Show cart page
        for item in cart:
            item["total_usd"] = usd(item["total"])

        return render_template("cart.html", name=session["name"], cart=cart, cart_count=cart_count[0]["SUM (quantity)"], cart_amount=usd(cart_amount[0]["SUM (total)"]))


@app.route("/update_cart", methods=["POST"])
@login_required
def update_cart():
    """update items into cart"""

    # Get product ID
    id = request.form.get("id")

    # If product ID is print job, just delete it from cart
    if id == "print":

        # Get print job id
        job_id = request.form.get("sku")

        # Delete print job from cart
        db.execute("DELETE FROM cart WHERE sku=:sku AND user_id=:user_id",  sku=job_id[0], user_id=session["user_id"])

        # Delete print job from print queue
        db.execute("DELETE FROM print WHERE sku=:sku AND user_id=:user_id",  sku=job_id[0], user_id=session["user_id"])

        return redirect("/cart")

    # If product is not print_job
    else:

        #Concatenate the the word "quantity" in order to get new product stock text box name (quantity1, quantity2, quantityX)
        quantity = 'quantityhidden' + id

        # Casting result from the text box into float
        new_quantity = float(request.form.get(quantity))

        if new_quantity > 0:

            # Get product details
            product = db.execute("SELECT * FROM products WHERE id=:prod_id", prod_id=id)

            # Update new prod quantity to cart
            db.execute("UPDATE cart SET quantity=:quantity, total=:total WHERE user_id=:user_id AND prod_id=:prod_id ",  user_id=session["user_id"], prod_id=product[0]["id"],
            quantity=new_quantity, total=new_quantity*product[0]["price"])

            return redirect("/cart")

        else:

            # Get product details
            product = db.execute("SELECT * FROM products WHERE id=:prod_id", prod_id=id)

            # Delete product from cart
            db.execute("DELETE FROM cart WHERE user_id=:user_id AND prod_id=:prod_id ",  user_id=session["user_id"], prod_id=product[0]["id"])

            return redirect("/cart")


@app.route("/empty_cart", methods=["GET"])
@login_required
def empty_cart():
    """delete cart items"""

    #Delete all the items in the cart
    product = db.execute("DELETE FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

    # Delete all from print queue
    db.execute("DELETE FROM print WHERE user_id=:user_id", user_id=session["user_id"])

    # Show an alert to the user letting him/her cart got empty
    flash('Your cart is empty!')

    return redirect("/")


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """Checkout cart items"""

    if request.method == "POST":

        # Get elements in cart
        cart = db.execute("SELECT * FROM products JOIN cart ON id=prod_id WHERE id IN (SELECT prod_id FROM cart WHERE user_id=:user_id)", user_id=session["user_id"])

        # Get total amount in cart
        cart_amount = db.execute("SELECT SUM (total) FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

        # Get info from form
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address1 = request.form.get("address")
        address2 = request.form.get("address2")
        country = request.form.get("country")
        state = request.form.get("state")
        zipcode = request.form.get("zipcode")
        billing_address = request.form.get("billing_address")
        save_info = request.form.get("save_info")
        payment = request.form.get("paymentMethod")
        discount = float(request.form.get("discount"))

        today = str(date.today())

        # Insert order into "orders" table
        db.execute("INSERT INTO orders (user_id, first_name, last_name, email, phone, address1, address2, country, state, zip, date, total, payment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        session["user_id"], first_name, last_name, email, phone, address1, address2, country, state, zipcode, today, cart_amount[0]["SUM (total)"]-discount, payment)

        # Get the latest order_id. Ordering DESC will return latest value in position [0]
        order_id = db.execute("SELECT order_id FROM orders WHERE user_id=:user_id ORDER BY order_id DESC", user_id=session["user_id"])

        # Insert products in order_products/update product stock
        for item in cart:

            # Update product stock
            stock_actual = db.execute("SELECT stock FROM products WHERE id=:prod_id", prod_id=item["prod_id"])
            db.execute("UPDATE products SET stock=:stock WHERE id=:prod_id", stock=int(stock_actual[0]["stock"])-int(item["quantity"]), prod_id=item["prod_id"])

            # Insert product into order_products
            db.execute("INSERT INTO order_products (order_id, sku, quantity) VALUES (?, ?, ?)", int(order_id[0]["order_id"]), int(item["sku"]), int(item["quantity"]))

            # Update print job status
            db.execute("UPDATE print SET status='Accepted' WHERE sku=:sku", sku=int(item["sku"]))

        # Empty cart after placing the order
        db.execute("DELETE FROM cart where user_id=:user_id", user_id=session["user_id"])

        # Render "Order placed" message
        return render_template("prompts.html", name=session["name"], missing="order_placed", cart_count=0)

    else:

        name = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:
            return render_template("prompts.html", name=session["name"], missing="cart", cart_count=0)

        # Get elements in cart
        cart = db.execute("SELECT * FROM products JOIN cart ON id=prod_id WHERE id IN (SELECT prod_id FROM cart WHERE user_id=:user_id)", user_id=session["user_id"])

        # Get total amount in cart
        cart_amount = db.execute("SELECT SUM (total) FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

        # Format TOTAL as USD
        for item in cart:
            item["total_usd"] = usd(item["total"])

        return render_template("checkout.html", name=session["name"], user=name, cart=cart, cart_count=cart_count[0]["SUM (quantity)"],
            cart_amount=usd(cart_amount[0]["SUM (total)"]))


@app.route("/promo", methods=["POST"])
def promo():
    """redeems cupoons"""
    promo = request.form.get("promo-code")

    discount = 10

    # If promo code is CS50, discount $10 from cart total
    if promo == "CS50":

        name = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:
            return render_template("prompts.html", name=session["name"], missing="cart", cart_count=0)

        # Get elements in cart
        cart = db.execute("SELECT * FROM products JOIN cart ON id=prod_id WHERE id IN (SELECT prod_id FROM cart WHERE user_id=:user_id)", user_id=session["user_id"])

        # Get total amount in cart
        cart_amount = db.execute("SELECT SUM (total) FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

        # Format TOTAL as USD
        for item in cart:
            item["total_usd"] = usd(item["total"])

        # Render check out. Promo=10 is the discount applied
        return render_template("checkout.html", name=session["name"], user=name, cart=cart, cart_count=cart_count[0]["SUM (quantity)"],
        cart_amount=usd(cart_amount[0]["SUM (total)"]), cart_amount_discount=usd(float(cart_amount[0]["SUM (total)"])-discount), discount=discount, promo=usd(discount))


@app.route("/my_orders", methods=["GET"])
def my_orders():
    """render user's orders"""

    # Get orders for current user
    orders = db.execute("SELECT * FROM orders WHERE user_id=:user_id", user_id=session["user_id"])

    # Get cart status for the active user
    cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

    if not orders:
        if cart_count[0]["SUM (quantity)"] == None:
            return render_template("prompts.html", name=session["name"], missing="orders", cart_count=0)

        else:
            return render_template("prompts.html", name=session["name"], missing="orders", cart_count=cart_count[0]["SUM (quantity)"])

    else:
        for order in orders:

            # Get # of items in the order
            order_items = db.execute("SELECT SUM (quantity) FROM order_products WHERE order_id=:order_id", order_id=order["order_id"])

            # Adding "_" after items because "items" is private python word
            order["items_"] = int(order_items[0]["SUM (quantity)"])

            # Add USD format to total
            order["total_usd"] = usd(float(order["total"]))


        if cart_count[0]["SUM (quantity)"] == None:
            return render_template("orders.html", orders=orders, name=session["name"], cart_count=0)

        else:
            return render_template("orders.html", orders=orders, name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])


@app.route("/order_details/<order_id>", methods=["GET"])
def order_details(order_id):
    """render user's order details"""

    # Get every product that is included in any order placed
    products = db.execute("SELECT * FROM products JOIN order_products ON products.sku=order_products.sku WHERE products.sku IN (SELECT sku FROM order_products WHERE order_id=:order_id)", order_id=order_id)

    for product in products:
        product["price_usd"] = usd(product["price"])

    # Get every print job, if any
    prints = db.execute ("SELECT * FROM print JOIN order_products ON print.sku=order_products.sku WHERE print.sku IN (SELECT sku FROM order_products WHERE order_id=:order_id)", order_id=order_id)

    for print_ in prints:
        print_["total_usd"] = usd(print_["total"])

    # Get cart status for the active user
    cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

    if cart_count[0]["SUM (quantity)"] == None:
        return render_template("order_details.html", products=products, name=session["name"], prints=prints, cart_count=0)

    else:
        return render_template("order_details.html", products=products, name=session["name"], prints=prints, cart_count=cart_count[0]["SUM (quantity)"])


@app.route("/print_new", methods=["GET", "POST"])
@login_required
def print_new():
    """Submit new printing job"""

    # Base cost for printing
    cost = 3

    # Base cost per material
    materials = {
        'PLA': 1,
        'ABS': 1,
        'PETG': 1.2,
        'TPU': 1.5
    }

    if request.method == "POST":

        quotation = request.form.get("prod_quotation")

        # if user is quoting
        if not quotation:

            # Quotate printing job
            new_file = request.files["file"]
            material = request.form.get("material")
            color = request.form.get("color")
            quantity = float(request.form.get("quantity"))
            comments = request.form.get("comments")

            # Secure the file
            filename = secure_filename(new_file.filename)

            # If no file has been submitted
            if not new_file:
                # Render apology
                return apology("Please upload a file", 400)

            # Check the file and its extension
            if filename != '':

                # Get the extension
                file_ext = os.path.splitext(filename)[1]

                # If file is not in the allowed file types (.stl in this case)
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:

                    # Render apology
                    return apology("Invalid File Type", 400)

                # Save the file into the projcet's folder
                new_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

            # Get file path
            path = app.config['UPLOAD_PATH'] + '/' + filename

            # Get size of the file in order to quotate
            size = os.stat(path).st_size

            # Compute quotation as (base cost + materials) * (size of the file/9000) * quantity of pieces to print. Formula is "just because..."
            quotation = round(float(cost + materials[material]) * float(size/9000) * quantity, 2)

            # Store the printing job in temp data base
            db.execute("INSERT INTO temp (user_id, file, quotation, quantity, total, comments, material, color) VALUES (:user_id, :file, :quotation, :quantity, :total, :comments, :material, :color)",
            user_id=session["user_id"], file=filename, quotation=quotation, quantity=quantity, total=quotation*quantity, comments=comments, material=material, color=color)

            # Get cart status for the active user
            cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

            if cart_count[0]["SUM (quantity)"] == None:

                # Redirect user to home page
                return render_template("print_submit.html", quotation=usd(quotation), name=session["name"], cart_count=0)

            return render_template("print_submit.html", quotation=usd(quotation), name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

        # Printing job already quoted and adding to the cart
        else:

            printing_job = db.execute("SELECT * FROM temp WHERE user_id=:user_id", user_id=session["user_id"])

            # Store the printing job in the data base
            db.execute("INSERT INTO print (user_id, file, quotation, quantity, total, comments, material, color, status) VALUES (:user_id, :file, :quotation, :quantity, :total, :comments, :material, :color, :status)",
            user_id=session["user_id"], file=printing_job[0]["file"], quotation=round(float(printing_job[0]["quotation"])/printing_job[0]["quantity"], 2), quantity=printing_job[0]["quantity"],
            total=round(float(printing_job[0]["quotation"]), 2), comments=printing_job[0]["comments"], material=printing_job[0]["material"],
            color=printing_job[0]["color"], status="Pending Payment")

            # Get print_id (will be SKU in cart). Ordering DESC to ensure the [0] will always be the latest addition
            print_id = db.execute("SELECT sku FROM print WHERE user_id=:user_id ORDER BY sku DESC", user_id=session["user_id"])

            # Add printing job into cart
            db.execute("INSERT INTO cart (user_id, prod_id, title, price, quantity, link, total, sku, file) VALUES (:user_id, :prod_id, :title, :price, :quantity, :link, :total, :sku, :file)",
            user_id=session["user_id"], prod_id=0, title="Printing Job", price=printing_job[0]["quotation"], quantity=1, link="/static/images/printing_job.jpg",
            total=printing_job[0]["quotation"], sku=print_id[0]["sku"], file=printing_job[0]["file"])

            # Delete printing job from temp data base
            db.execute("DELETE FROM temp WHERE user_id=:user_id", user_id=session["user_id"])

            # Get cart status for the active user
            cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

            # Get total amount in cart
            cart_amount = db.execute("SELECT SUM (total) FROM cart WHERE user_id=:user_id", user_id=session["user_id"])

            # Get elements in cart
            cart = db.execute("SELECT * FROM products JOIN cart ON id=prod_id WHERE id IN (SELECT prod_id FROM cart WHERE user_id=:user_id)", user_id=session["user_id"])

            # Get print jobs for user
            print_job = db.execute("SELECT * FROM print WHERE user_id=:user_id", user_id=session["user_id"])

            # Format TOTAL as USD
            for item in cart:
                item["total_usd"] = usd(item["total"])

            # Show cart page
            return render_template("cart.html", name=session["name"], cart=cart, cart_count=cart_count[0]["SUM (quantity)"], cart_amount=usd(cart_amount[0]["SUM (total)"]),
            print_job=print_job)

    else:

        if session:

            # Get cart status for the active user
            cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

            if cart_count[0]["SUM (quantity)"] == None:

                # Show cart page
                return render_template("print_submit.html", name=session["name"], cart_count=0)

            # Show cart page
            return render_template("print_submit.html", name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

        else:
            return render_template("print_submit.html")


@app.route("/print_status", methods=["GET"])
@login_required
def print_status():
    """Check printing jobs status """

    # Get print jobs for the active user
    print_jobs=db.execute("SELECT * FROM print WHERE user_id=:session_id", session_id=session["user_id"])

    # Get cart status for the active user
    cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

    if not print_jobs:

        if cart_count[0]["SUM (quantity)"] == None:

            # Show print_status page
            return render_template("prompts.html", name=session["name"], missing="print_jobs", cart_count=0)

        else:

            # Show print_status page
            return render_template("prompts.html", name=session["name"], missing="print_jobs", cart_count=cart_count[0]["SUM (quantity)"])

    else:

        if cart_count[0]["SUM (quantity)"] == None:

            # Show print_status page
            return render_template("print_status.html", name=session["name"], print_jobs=print_jobs, cart_count=0)

        else:

            # Show print_status page
            return render_template("print_status.html", name=session["name"], print_jobs=print_jobs, cart_count=cart_count[0]["SUM (quantity)"])


@app.route("/privacy", methods=["GET"])
def privacy():
    """Shows privacy agreement"""

    if session:
        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Show privacy page
            return render_template("privacy.html", name=session["name"], cart_count=0)

        else:

            # Show privacy page
            return render_template("privacy.html", name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:
        # Show privacy page
        return render_template("privacy.html")


@app.route("/terms", methods=["GET"])
def terms():
    """Shows terms and conditions"""

    #Get terms
    terms_conditions = db.execute ("SELECT * FROM terms")

    if session:
        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Show privacy page
            return render_template("terms.html", terms=terms_conditions[0]["terms_conditions"], name=session["name"], cart_count=0)

        else:

            # Show privacy page
            return render_template("terms.html", terms=terms_conditions[0]["terms_conditions"], name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:
        # Show privacy page
        return render_template("terms.html", terms=terms_conditions[0]["terms_conditions"])


@app.route("/printing_types", methods=["GET"])
def printing_types():
    """Shows 3D printing types and info"""
    if session:
        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Show privacy page
            return render_template("printing_types.html", name=session["name"], cart_count=0)

        else:

            # Show privacy page
            return render_template("printing_types.html", name=session["name"], cart_count=cart_count[0]["SUM (quantity)"])

    else:
        # Show privacy page
        return render_template("printing_types.html")


@app.route("/filament_info", methods=["GET"])
def filament_info():
    """Shows filaments types and info"""

    standard_fs = db.execute("SELECT * FROM filament_info WHERE type='STANDARD'")
    composite_fs = db.execute("SELECT * FROM filament_info WHERE type='COMPOSITE'")
    flexible_fs = db.execute("SELECT * FROM filament_info WHERE type='FLEXIBLE'")
    specialty_fs = db.execute("SELECT * FROM filament_info WHERE type='SPECIALTY'")
    support_fs = db.execute("SELECT * FROM filament_info WHERE type='SUPPORT'")

    if session:
        # Get cart status for the active user
        cart_count=db.execute("SELECT SUM (quantity) FROM cart WHERE user_id=:session_id", session_id=session["user_id"])

        if cart_count[0]["SUM (quantity)"] == None:

            # Show privacy page
            return render_template("filament_info.html", name=session["name"], cart_count=0, standard=standard_fs, composite=composite_fs, flexible=flexible_fs,
            specialty=specialty_fs, support=support_fs)

        else:

            # Show privacy page
            return render_template("filament_info.html", name=session["name"], cart_count=cart_count[0]["SUM (quantity)"], standard=standard_fs, composite=composite_fs,
            flexible=flexible_fs, specialty=specialty_fs, support=support_fs)

    else:
        # Show privacy page
        return render_template("filament_info.html", standard=standard_fs, composite=composite_fs, flexible=flexible_fs,
            specialty=specialty_fs, support=support_fs)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)