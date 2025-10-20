import re

class UserDatabaseService:
    def __init__(self, db, User):
        self.db = db
        self.User = User
        self.EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(com|rs|org)$")

    def insert_user(self, user, role):
        # check if any field is missing
        if 'forename' not in user or user['forename'] == '':
            return "Field forename is missing.", 400
        if 'surname' not in user or user['surname'] == '':
            return "Field surname is missing.", 400
        if 'email' not in user or user['email'] == '':
            return "Field email is missing.", 400
        if 'password' not in user or user['password'] == '':
            return "Field password is missing.", 400

        # check if email is in right format
        if not self.EMAIL_REGEX.match(user['email']):
            return "Invalid email.", 400

        # check if password is right length
        if len(user['password']) < 8:
            return "Invalid password.", 400

        # check if email already exists in the database
        if self.db.session.query(self.User).filter_by(email=user['email']).count() > 0:
            return "Email already exists.", 400

        # add user to the database
        self.db.session.add(self.User(
            email = user['email'],
            password = user['password'],
            role = role,
            forename = user['forename'],
            surname = user['surname'],
        ))
        self.db.session.commit()
        return "", 200

    def check_user(self, user):
        # check if any field is missing
        if 'email' not in user or user['email'] == '':
            return "Field email is missing.", 400
        if 'password' not in user or user['password'] == '':
            return "Field password is missing.", 400

        # check if email is in right format
        if not self.EMAIL_REGEX.match(user['email']):
            return "Invalid email.", 400

        # check if user with given email and password exists
        user_record = self.db.session.query(self.User).filter_by(email=user['email']).first()
        if not user_record or not (user_record.password == user['password']):
            return "Invalid credentials.", 400

        return user_record, 200

    def delete_user(self, user):
        # delete user and get number of rows affected
        rows_deleted = self.db.session.query(self.User).filter_by(email=user['email']).delete()
        self.db.session.commit()

        # check if user existed
        if rows_deleted == 0:
            return "Unknown user.", 400
        else:
            return "", 200