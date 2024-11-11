import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import grpc
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from proto.v1 import user_manager_pb2
from proto.v1.user_manager_pb2_grpc import UserManagerStub


class Settings(BaseSettings):
    grpc_addres: str = "[::]:50051"
    host: str = "0.0.0.0"
    port: int = 8000


class UserManagerClient:
    def __init__(self, stub: UserManagerStub):
        self._stub = stub

    def CreateUser(self, request: user_manager_pb2.CreateUserRequest, timeout: float = 10.0) -> user_manager_pb2.User:
        return self._stub.CreateUser(request, timeout=timeout)


class CreateUserDTO(BaseModel):
    name: str
    age: int


class CreatedUserDTO(BaseModel):
    id: uuid.UUID
    name: str
    age: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_proto(cls, user_proto: user_manager_pb2.User) -> "CreatedUserDTO":
        return cls(
            id=uuid.UUID(bytes=user_proto.id),
            name=user_proto.name,
            age=user_proto.age,
            created_at=user_proto.created_at.ToDatetime(),
            updated_at=user_proto.updated_at.ToDatetime(),
        )


class Dependencies:
    _settings: Settings

    _channel: grpc.Channel
    _stub: UserManagerStub

    _user_manager_client: UserManagerClient

    @classmethod
    def start(cls):
        cls._settings = Settings()
        cls._channel = grpc.insecure_channel(cls._settings.grpc_addres)
        cls._stub = UserManagerStub(channel=cls._channel)
        cls._user_manager_client = UserManagerClient(stub=cls._stub)

    @classmethod
    def stop(cls):
        if cls._channel:
            cls._channel.close()

    @classmethod
    def settings(cls) -> Settings:
        if cls._settings is None:
            cls.start()
        return cls._settings

    @classmethod
    def user_manager_client(cls) -> UserManagerClient:
        if cls._user_manager_client is None:
            cls.start()
        return cls._user_manager_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    Dependencies.start()
    yield
    Dependencies.stop()


def create_application():
    app = FastAPI(lifespan=lifespan)

    @app.get("/", response_class=PlainTextResponse)
    def root():
        return "Hello matter"

    @app.post("/user", response_model=CreatedUserDTO)
    def create_user(
        payload: CreateUserDTO,
        user_manager_client: UserManagerClient = Depends(Dependencies.user_manager_client),
    ):
        try:
            user_proto = user_manager_client.CreateUser(
                request=user_manager_pb2.CreateUserRequest(name=payload.name, age=payload.age)
            )
            return CreatedUserDTO.from_proto(user_proto=user_proto)
        except grpc.RpcError as rpc_error:
            logging.error(f"RPC failed with code: {rpc_error.code()}")

            status_code = {
                grpc.StatusCode.INVALID_ARGUMENT: 400,
                grpc.StatusCode.NOT_FOUND: 404,
                grpc.StatusCode.ALREADY_EXISTS: 409,
                grpc.StatusCode.PERMISSION_DENIED: 403,
                grpc.StatusCode.UNAUTHENTICATED: 401,
                grpc.StatusCode.INTERNAL: 500,
            }.get(rpc_error.code(), 500)

            error_message = (
                str(rpc_error.details()) if rpc_error.details() else "An error occurred processing your request"
            )
            raise HTTPException(status_code=status_code, detail=error_message)

    return app


if __name__ == "__main__":
    settings = Settings()
    app = create_application()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )
