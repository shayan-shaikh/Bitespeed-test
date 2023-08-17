# necessary imports
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Setting up the connection
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contacts.db"
db = SQLAlchemy(app)


# defining the model for Contact table
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    linkedId = db.Column(db.Integer, nullable=True)
    linkPrecedence = db.Column(db.String(10), nullable=False)
    createdAt = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    updatedAt = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
    deletedAt = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Contact {self.id}>"


def find_and_link_contact(email=None, phoneNumber=None):
    if not email and not phoneNumber:
        return None

    # query the database for existing contacts with the same email or phone number
    contact_query = Contact.query.filter(
        (Contact.email == email) | (Contact.phoneNumber == phoneNumber)
    )

    # if no existing contact is found, create a new one and mark it as primary
    if contact_query.count() == 0:
        new_contact = Contact(
            email=email, phoneNumber=phoneNumber, linkPrecedence="primary"
        )
        db.session.add(new_contact)
        db.session.commit()
        return new_contact

    # if one existing contact is found, return it
    elif contact_query.count() == 1:
        return contact_query.first()

    # if more than one existing contacts are found, link them together and return the primary one
    else:
        contacts = contact_query.all()
        primary_contact = None

        # loop through the contacts and find the primary one
        for contact in contacts:
            if contact.linkPrecedence == "primary":
                primary_contact = contact
                break

        # if no primary contact is found, mark the first one as primary
        if not primary_contact:
            primary_contact = contacts[0]
            primary_contact.linkPrecedence = "primary"

        # loop through the contacts again and link them to the primary one
        for contact in contacts:
            if contact != primary_contact:
                contact.linkedId = primary_contact.id
                contact.linkPrecedence = "secondary"

        # commit the changes to the database
        db.session.commit()

        return primary_contact


def get_contact_response(contact):
    # check if contact is valid
    if not contact:
        return None

    # initialize the response dictionary
    contact_response = {
        "primarycontactid": contact.id,
        "emails": [contact.email],
        "phoneNumbers": [contact.phoneNumber]
        if contact.phoneNumber
        else [contact.phoneNumber],
        "secondarycontactids": [],
    }

    # query the database for secondary contacts linked to the primary one
    secondary_contacts = Contact.query.filter(Contact.linkedId == contact.id).all()
    print("Secondary contacts : " + str(secondary_contacts))
    print("hi")

    # loop through the secondary contacts and add their information to the consolidated contact dictionary
    for secondary_contact in secondary_contacts:
        contact_response["emails"].append(secondary_contact.email)
        contact_response["phoneNumbers"].append(secondary_contact.phoneNumber)
        contact_response["secondarycontactids"].append(secondary_contact.id)

    return contact_response


@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json()
    email = data.get("email")
    phoneNumber = data.get("phoneNumber")

    # find and link the contact based on the email and phone number
    contact = find_and_link_contact(email, phoneNumber)

    # get the response of contact information based on the contact object
    contact_response = get_contact_response(contact)

    # return a JSON response with the consolidated contact information
    return jsonify({"contact": contact_response})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
