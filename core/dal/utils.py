from google.protobuf.timestamp_pb2 import Timestamp

from core.dal import models
from proto.v1 import user_manager_pb2


def user_model_to_user_proto(user_model: models.User) -> user_manager_pb2.User:
    """
    Converts a SQLAlchemy User model to a Protobuf User message.

    Args:
        user_model: The source User model from SQLAlchemy

    Returns:
        A Protobuf User message
    """
    proto_user = user_manager_pb2.User()

    proto_user.id = user_model.id.bytes
    proto_user.name = user_model.name
    proto_user.age = user_model.age

    if user_model.created_at:
        created_at = Timestamp()
        created_at.FromDatetime(user_model.created_at)
        proto_user.created_at.CopyFrom(created_at)

    if user_model.updated_at:
        updated_at = Timestamp()
        updated_at.FromDatetime(user_model.updated_at)
        proto_user.updated_at.CopyFrom(updated_at)

    return proto_user
