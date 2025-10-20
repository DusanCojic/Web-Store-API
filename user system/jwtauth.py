import os
import jwt
import datetime

class JWTAuth:

    SECRET_KEY = os.getenv("JWT", "")
    ALGORITHM = 'HS256'
    EXPIRATION = 60

    @staticmethod
    def generate_token(data):
        payload = {}

        now = datetime.datetime.now(datetime.UTC)
        payload['sub'] = data['email']
        payload['password'] = data['password']
        payload['forename'] = data['forename']
        payload['surname'] = data['surname']
        payload['roles'] = data['role']
        payload['type'] = 'access'
        payload['iat'] = int(now.timestamp())
        payload['nbf'] = int(now.timestamp())
        payload['exp'] = int((now + datetime.timedelta(minutes=JWTAuth.EXPIRATION)).timestamp())

        token = jwt.encode(payload, JWTAuth.SECRET_KEY, algorithm=JWTAuth.ALGORITHM)
        return token

    @staticmethod
    def validate_token(token: str):
        try:
            decoded = jwt.decode(token, JWTAuth.SECRET_KEY, algorithms=[JWTAuth.ALGORITHM])
            return decoded['sub']
        except jwt.ExpiredSignatureError:
            print("Token expired.")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token.")
            return None