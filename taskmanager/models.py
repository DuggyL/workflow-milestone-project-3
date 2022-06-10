from taskmanager import db

class Users(db.Model):
    #schema
    id = db.Column(db.Interger, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(260), nullable=False)

    def __repr__(self):
        return self.user_name