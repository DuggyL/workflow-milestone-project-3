from taskmanager import db

class Customer(db.Model):
    # schema for the customer model
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    contact_no = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)

    def __repr__(self):
    # __repr__ to represent itself in the form of a string
        return self.company_name