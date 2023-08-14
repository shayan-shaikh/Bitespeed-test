from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"
database = SQLAlchemy(app)


@app.route("/")
def test():
    return "This is at home route"


if __name__ == "__main__":
    app.run(debug=True)
