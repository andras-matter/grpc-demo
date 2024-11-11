from concurrent import futures

import grpc

from core.dependencies import Container
from core.transport.user_manager_servicer import UserManagerServicer
from proto.v1 import user_manager_pb2_grpc


def main():
    container = Container()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=container.config().max_workers))

    user_manager_pb2_grpc.add_UserManagerServicer_to_server(UserManagerServicer(container), server)

    server.add_insecure_port(container.config().server_address)
    server.start()

    print("serving")

    try:
        server.wait_for_termination()
    finally:
        print("closing connection pool")
        container.engine().dispose()


if __name__ == "__main__":
    main()
