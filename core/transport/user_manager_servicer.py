import grpc

from core.dependencies import Container
from proto.v1 import user_manager_pb2, user_manager_pb2_grpc


# UserManagerService provides an implementation of the methods of the UserManager service.
class UserManagerServicer(user_manager_pb2_grpc.UserManagerServicer):
    def __init__(self, container: Container):
        super().__init__()
        self._user_service = container.user_service()

    def CreateUser(  # type: ignore[return]
        self,
        payload: user_manager_pb2.CreateUserRequest,
        context: grpc.ServicerContext,
    ) -> user_manager_pb2.User:
        print(f"Creating user {payload}")

        try:
            user = self._user_service.create_user(name=payload.name, age=payload.age)
            print(f"Created user {user}")
            return user
        except ValueError as e:
            context.abort(code=grpc.StatusCode.INVALID_ARGUMENT, details=str(e))
        except Exception as e:
            context.abort(
                code=grpc.StatusCode.INTERNAL,
                details=f"Internal server error: {str(e)}",
            )
