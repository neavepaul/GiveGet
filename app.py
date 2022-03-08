#the brain
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finale_refined.db")

@app.route("/")
def home():
    """Render home page"""
    return render_template("home.html")


#registration {step 1}
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("user_name"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # hash the password and insert a new user in the database
        if not request.form.get("preferences") and request.form.get("user_type") == "receive":
            return apology("Receiver should select at least one item type", 400)
        hash = generate_password_hash(request.form.get("password"))
        new_user_id = db.execute("INSERT INTO User (user_name, name, password, address_line1, address_line2, city, pincode, state, country, user_type, email_id) VALUES(:user_name, :name, :hash, :address_line1, :address_line2, :city, :pincode, :state, :country, :user_type, :email_id)",
                                 user_name=request.form.get("user_name"),
                                 name=request.form.get("name"),
                                 hash=hash,
                                 address_line1=request.form.get("address_line1"),
                                 address_line2=request.form.get("address_line2"),
                                 city=request.form.get("city"),
                                 pincode=request.form.get("pincode"),
                                 state=request.form.get("state"),
                                 country=request.form.get("country"),
                                 user_type=request.form.get("user_type"),
                                 email_id=request.form.get("email"))
        # unique username constraint violated?
        if not new_user_id:
            return apology("username taken", 400)




        if request.form.get("preferences"):

            preferences = map(int, request.form.get("preferences").split(','))
            for item_id in preferences:

                db.execute("INSERT INTO Preference (user_id, item_id, create_date) VALUES(:user_id, :item_id, :create_date)",
                                     user_id=new_user_id,
                                     item_id=item_id,
                                     create_date=datetime.now())


        # Remember which user has logged in
        session["user_id"] = new_user_id
        session["user_name"] = request.form.get("user_name")
        session["user_type"] = request.form.get("user_type")


        # Display a flash message
        flash("Registered!")

        # Redirect user to home page
        return redirect(url_for("home"))

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
        if not request.form.get("user_name"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM User WHERE user_name = :user_name",
                          user_name=request.form.get("user_name"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["user_name"]
        session["user_type"] = rows[0]["user_type"]

        # Redirect user to home page
        if session["user_type"] == "donate":
            return redirect(url_for("donations",user_id=session["user_id"]))
        else:
            return redirect(url_for("view_open_donations_receiver",user_id=session["user_id"] ))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("home"))


@app.route("/users/<int:user_id>/donations", methods=["GET", "POST"])
@login_required
def donations(user_id):
    """Donate"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        itemtype_id = request.form.get("itemtype_id")
        title = request.form.get("title")
        note = request.form.get("note")
        intended_receipients = map(int, request.form.get("intended_receipients").split(','))

        # Ensure item was submitted
        if not request.form.get("itemtype_id"):
            return apology("must provide item type", 403)

        # Ensure description was submitted
        elif not request.form.get("title"):
            return apology("must provide title", 403)

        # Ensure recipient was selected <NOT WORKING>
        elif not request.form.get("intended_receipients"):
            return apology("must select atleast one receipient", 403)

        # Query database for username
        donation_id = db.execute("INSERT INTO Donation (user_id, title, note, item_id, status, create_date, modified_date) VALUES(:user_id, :title, :note, :item_id, :status, :create_date, :modified_date)",
                   user_id=user_id,
                   title=title,
                   note=note,
                   item_id=itemtype_id,
                   status="Open",
                   create_date=datetime.now(),
                   modified_date=datetime.now()
                   )

        for rank,receipient_id in enumerate(intended_receipients):
            db.execute("INSERT INTO IntendedReceipients (donation_id, rank, status, user_id, create_date, modified_date) VALUES(:donation_id, :rank, :status, :user_id,:create_date, :modified_date)",
                   donation_id=donation_id,
                   rank=rank,
                   status="Close" if rank > 0 else "Open",
                   user_id=receipient_id,
                   create_date=datetime.now(),
                   modified_date=datetime.now()
                   )

        flash("Donated!")

        return redirect(url_for("home"))

    else:
        return render_template("donations.html")

@app.route("/timeline_give")
@login_required
def timeline_give():
    """Show history of Donation"""

    donations = db.execute(
    """SELECT
        u.name AS user_name,
        d.id AS donation_id,
        d.title AS donation_title,
        d.note AS donation_instructions,
        d.create_date AS donation_create_date,
        d.modified_date AS donation_last_modified_date,
        d.status AS donation_status,it.title AS item_type
    FROM
        user AS u inner JOIN donation d on d.user_id = u.id
        And d.status IN ('Complete', 'Rejected')AND u.id=:user_id
        inner JOIN ItemType AS it on it.id=d.item_id
    ORDER BY d.modified_date DESC""",user_id=session["user_id"])

    return render_template("timeline_give.html", donations=donations)


@app.route("/users/<int:user_id>/new-donations")
@login_required
def view_open_donations_receiver(user_id):
    """Show Open donations to receivers"""

    # Place View Donations SQL Here
    donations = db.execute("""
    SELECT
    u.name AS user_name,
    u.address_line1 AS address_line1,
    u.city AS user_city,
    u.pincode AS user_pincode,
    d.id AS donation_id,
    d.title AS donation_title,
    d.note AS donation_instructions,
    d.create_date AS donation_create_date,
    d.modified_date AS donation_modified_date,
    d.status AS donation_status,
    ir.status AS recipient_status,
    ir.modified_date AS recipient_modified_date_date
FROM
    user AS u inner JOIN donation d on d.user_id = u.id And d.status='Open'
    left outer join IntendedReceipients as ir on d.id = ir.donation_id AND ir.status='Open'
    inner join user as iru on ir.user_id = iru.id AND iru.id=:user_id
ORDER BY d.modified_date DESC""",
            user_id=user_id)
    print(donations)
    return render_template("view_open_donations_receiver.html", donations=donations)


@app.route("/users/<int:user_id>/pending-donations")
@login_required
def view_pending_donations_receiver(user_id):
    """Show Pending donations to receivers"""

    donations = db.execute("""
        SELECT
        u.name AS user_name,
        u.address_line1 AS address_line1,
        u.city AS user_city,
        u.pincode AS user_pincode,
        d.id AS donation_id,
        d.title AS donation_title,
        d.note AS donation_instructions,
        d.create_date AS donation_create_date,
        d.modified_date AS donation_modified_date,
        d.status AS donation_status,
        ir.status AS recipient_status,
        ir.modified_date AS recipient_modified_date_date
    FROM
        user AS u inner JOIN donation d on d.user_id = u.id And d.status='Open'
        left outer join IntendedReceipients as ir on d.id = ir.donation_id AND ir.status='Accept'
        inner join user as iru on ir.user_id = iru.id AND iru.id=:user_id
    ORDER BY d.modified_date DESC""",
            user_id=user_id)
    return render_template("view_pending_donations_receiver.html", donations=donations)


@app.route("/users/<int:user_id>/complete-donations")
@login_required
def view_complete_donations_receiver(user_id):
    """Show Complete donations to receivers"""

    donations = db.execute("""
    SELECT
    u.name AS user_name,
    u.address_line1 AS address_line1,
    u.city AS user_city,
    u.pincode AS user_pincode,
    d.id AS donation_id,
    d.title AS donation_title,
    d.note AS donation_instructions,
    d.create_date AS donation_create_date,
    d.modified_date AS donation_modified_date,
    d.status AS donation_status,
    ir.status AS recipient_status,
    ir.modified_date AS recipient_modified_date_date
FROM
    user AS u inner JOIN donation d on d.user_id = u.id And d.status='Complete'
    left outer join IntendedReceipients as ir on d.id = ir.donation_id AND ir.status='Accept'
    inner join user as iru on ir.user_id = iru.id AND iru.id=:user_id
ORDER BY d.modified_date DESC""",
            user_id=user_id)
    return render_template("view_complete_donations_receiver.html", donations=donations)



@app.route("/users/<int:user_id>/donations/<int:donation_id>/accept", methods=["POST"])
@login_required
def accept_donation(user_id, donation_id):
    # NGO accept
    if request.method == "POST":
        db.execute("UPDATE IntendedReceipients SET modified_date=current_timestamp, status='Accept' WHERE id=(SELECT id FROM IntendedReceipients WHERE status='Open' and donation_id= :donation_id and user_id = :user_id)", user_id=user_id, donation_id=donation_id)
        return jsonify({"message":"Accept Succesful."})


@app.route("/users/<int:user_id>/donations/<int:donation_id>/complete", methods=["POST"])
@login_required
def complete_donation(user_id, donation_id):
    # NGO receives and marks donation complete
    if request.method == "POST":
        db.execute("UPDATE Donation SET modified_date=current_timestamp, status='Complete' WHERE id= :donation_id", donation_id=donation_id)
        return jsonify({"message":"Complete Succesful."})

@app.route("/users/<int:user_id>/donations/<int:donation_id>/reject", methods=["POST"])
@login_required
def reject_donation(user_id, donation_id):
    # NGO reject
    if request.method == "POST":
        result_set = db.execute("SELECT id, rank FROM IntendedReceipients WHERE donation_id=:donation_id and user_id = :user_id", user_id=user_id, donation_id=donation_id)
        if not result_set:
            #TODO
            pass
        intended_receipient_id, rank = result_set[0].values()

        db.execute("UPDATE IntendedReceipients SET modified_date=current_timestamp, status='Reject' WHERE id= :intended_receipient_id",intended_receipient_id=intended_receipient_id)
        rank = rank+1
        update_row_count = db.execute("""
        UPDATE IntendedReceipients set modified_date=current_timestamp, status='Open' WHERE id = (
        SELECT id FROM IntendedReceipients WHERE rank=:new_rank AND donation_id=:donation_id and status='Close')
        """, new_rank=rank, donation_id=donation_id)

        if not update_row_count:
            db.execute("""
            UPDATE Donation set modified_date=current_timestamp, status='Abort' WHERE id=:donation_id
            """, donation_id=donation_id)
            return jsonify({"message":"Reject with Abort Succesful."})

        # db.execute("UPDATE Donation SET status='Accept' WHERE id= :donation_id", donation_id=donation_id)
        return jsonify({"message":"Reject Succesful."})


@app.route("/users/<int:user_id>/active-donations")
@login_required
def active_donations(user_id):

    if request.method == "GET":

        donations = db.execute("""
        SELECT
            d.title AS donation_title,
            d.note AS donation_instructions,
            d.create_date AS donation_create_date,
            ir.status AS recipient_status,
            ir.modified_date AS recipient_modified_date,
            iru.name AS recipient
        FROM
            user AS u inner JOIN donation d on d.user_id = u.id And d.status='Open' AND u.id=:user_id
            left outer join IntendedReceipients as ir on d.id = ir.donation_id AND ir.status IN ('Open', 'Accept')
            inner join user as iru on ir.user_id = iru.id
        ORDER BY ir.modified_date DESC
        """, user_id=user_id)

        return render_template("view_active_donations.html", donations=donations)

@app.route("/users/<int:user_id>/donations-history")
@login_required
def donations_history(user_id):

    if request.method == "GET":

        donations = db.execute("""
        SELECT
            d.title AS donation_title,
            d.note AS donation_instructions,
            d.create_date AS donation_create_date,
            d.modified_date AS donation_modified_date,
            d.status AS donation_status,
            ir.status AS recipient_status,
            ir.modified_date AS recipient_modified_date,
            iru.name AS recipient
        FROM
            user AS u inner JOIN donation d on d.user_id = u.id And d.status IN ('Complete','Abort') AND u.id=:user_id
            left outer join IntendedReceipients as ir on d.id = ir.donation_id AND ir.status IN ('Accept')
            left outer join user as iru on ir.user_id = iru.id
        ORDER BY d.modified_date DESC
        """, user_id=user_id)

        return render_template("view_donations_history.html", donations=donations)


@app.route("/item-types")
def item_types():
    """
    Return Item Types
    """

    item_types = db.execute("SELECT * FROM ItemType WHERE is_active= :is_active", is_active='t')
    return jsonify(item_types)



@app.route("/receipients")
def receipients_by_type():
    item_type = request.args.get('itemType')
    receipients = db.execute(
        "SELECT * FROM User as user INNER JOIN Preference as preference on user.id=preference.user_id and preference.item_id in (SELECT id FROM ItemType WHERE title = :title)", title = item_type
        )
    return jsonify(receipients)