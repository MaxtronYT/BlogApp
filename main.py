from inspect import Attribute
from sqlite3 import IntegrityError
from flask import *
from flask_sqlalchemy import *
from datetime import datetime as dt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['secret_key'] = "I dont know maybe"
app.secret_key = "I dont know maybe"

db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(10), nullable=False)

    def __repr__(self) -> str:
        return f"Username : {self.username} Password : {self.password}"


class Messages(db.Model):
    user = db.Column(db.String, nullable=False, unique=True)
    time_uploaded = db.Column(db.DateTime, primary_key=True, nullable=False)
    message = db.Column(db.String(400), nullable=False)

    def __repr__(self) -> str:
        return f"Message : {self.message} \n Posted on : {self.time_uploaded} By : {self.message}"


@app.route('/', methods=["POST", "GET"])
def loginpage():
    if request.method == 'POST':
        _name = request.form['_name']
        _pass = request.form['_pass']
        if len(_name) != 0 and len(_pass) != 0:
            query = User.query.filter_by(username=_name).first()

            try:
                if _name == query.username and _pass == query.password:
                    session['loggedin'] = "Yes"
                    session["username"] = _name
                    return redirect(url_for('mainapp'))

                else:
                    flash("Check your credintials")
                return redirect(url_for("loginpage"))

            except AttributeError:
                flash("Account not found")
                return redirect(url_for("loginpage"))

        else:
            flash("Enter full credintials")
            return redirect(url_for("loginpage"))

    else:
        return render_template("login.html")


@app.route('/signup', methods=["POST", "GET"])
def signuppage():
    if request.method == 'POST':
        _name = request.form['_name']
        _pass = request.form['_pass']

        if len(_name) != 0 and len(_pass) != 0:
            query = User.query.filter_by(username=_name).first()

            try:
                if _name == query.username:
                    flash("Account already exists")
                    return redirect(url_for("loginpage"))

            except AttributeError:
                query1 = User()
                query1.username = _name
                query1.password = _pass
                db.session.add(query1)
                db.session.commit()
                flash("Account made successfully")
                return redirect(url_for("loginpage"))

        if len(_name) == 0 or len(_pass) == 0:
            flash("Enter credintials properly")
            return render_template('signup.html')

    else:
        return render_template("signup.html")


@app.route("/app", methods=["POST", "GET"])
def mainapp():
    if "loggedin" in session:
        if session["loggedin"] == 'Yes':
            if request.method == 'POST' and request.form['response'] == "Logout":
                session["loggedin"] = "No"
                session.pop("username", None)
                session.pop("loggedin", None)
                return redirect(url_for("loginpage"))

            if request.method == 'POST' and request.form['response'] == "Post":
                msg = request.form["message"]
                m1 = Messages()
                m1.message = msg
                m1.time_uploaded = dt.utcnow()
                m1.user = session['username']
                db.session.add(m1)
                db.session.commit()
                allmesages = Messages.query.all()
                return render_template("app.html", allmessages=allmesages)

            if session["loggedin"] == "No":
                return render_template("404.html")

            else:
                return render_template('app.html', username=session["username"])

    if request.method == 'GET':
        return render_template("404.html")


# @ app.route('/message')
# def showmessages():
#     if session["loggedin"] == "Yes":
#         allmesages = Messages.query.all()
#         return render_template("messages.html", allmessages=allmesages)

#     else:
#         return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
