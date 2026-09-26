import uuid
from datetime import datetime, timedelta

import jwt
from sqlalchemy.exc import NoResultFound

from algobio.auth.model import NormalizedOAuth2Profile
from algobio.model.domain import User
from algobio.repositories import SQLRepository


class AuthService:
    def __init__(self, repo: SQLRepository, jwt_secret_key: str):
        self.key = jwt_secret_key
        self.repo = repo

    def get_user(self, id: uuid.UUID) -> User | None:
        try:
            return self.repo.get_user(id)
        except NoResultFound:
            return None

    def get_user_by_email(self, email: str) -> User | None:
        try:
            return self.repo.get_user_by_email(email)
        except NoResultFound:
            return None

    def create_user(self, profile: NormalizedOAuth2Profile) -> User:
        return self.repo.insert_user(User(email=profile.email, username=profile.name))

    def create_jwt(self, user: User):
        payload = {
            "sub": str(user.id),
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(days=1),
        }

        return jwt.encode(payload, self.key, algorithm="HS256")

    def decode_jwt(self, token: str):
        return jwt.decode(token, self.key, algorithms=["HS256"])
