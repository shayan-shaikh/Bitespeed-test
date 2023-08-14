# necessary imports
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Setting up the connection
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.database"
database = SQLAlchemy(app)


# Using a class to mimick objects that will be filled in the database
class Contact(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    phoneNumber = database.Column(database.String(100))
    email = database.Column(database.String(100))
    linkedId = database.Column(database.Integer)
    linkPrecedence = database.Column(database.String)
    createdAt = database.Column(database.DateTime)
    updatedAt = database.Column(database.DateTime)
    deletedAt = database.Column(database.DateTime)


# define the /identify endpoint and it's functionality
@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json()
    email = data.get("email")
    phoneNumber = data.get("phoneNumber")
    if not email or not phoneNumber:
        return jsonify({"error": "Need to give atleast an email or a Phone Number."})


@app.route("/")
def test():
    return "This is at home route"


if __name__ == "__main__":
    app.run(debug=True)
