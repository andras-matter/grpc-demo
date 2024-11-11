import uuid
from collections.abc import Iterator

from core.dal.models import User
from core.dal.query import Querier
from core.dal.utils import user_model_to_user_proto
from proto.v1 import user_manager_pb2


class UserService:
    def __init__(self, querier: Querier):
        self._querier = querier

    def create_user(self, name: str, age: int) -> user_manager_pb2.User:
        if age < 0:
            raise ValueError("Age cannot be negative")
        if not name.strip():
            raise ValueError("Name cannot be empty")

        user = self._querier.create_user(name=name, age=age)
        if user is None:
            raise RuntimeError("Failed to create user")
        user_proto = user_model_to_user_proto(user)
        return user_proto

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self._querier.get_user_by_id(id=user_id)
        if user is None:
            raise ValueError(f"User with id {user_id} not found")
        return user

    def list_users(self) -> Iterator[User]:
        return self._querier.list_users()

    def update_user(self, user_id: uuid.UUID, name: str, age: int) -> User:
        if not self._querier.get_user_by_id(id=user_id):
            raise ValueError(f"User with id {user_id} not found")

        if age < 0:
            raise ValueError("Age cannot be negative")
        if not name.strip():
            raise ValueError("Name cannot be empty")

        user = self._querier.update_user(id=user_id, name=name, age=age)
        if user is None:
            raise RuntimeError("Failed to update user")
        return user

    def delete_user(self, user_id: uuid.UUID) -> None:
        if not self._querier.get_user_by_id(id=user_id):
            raise ValueError(f"User with id {user_id} not found")

        self._querier.delete_user(id=user_id)
