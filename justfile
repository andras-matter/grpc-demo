default:
    just --list

generate:
    python -m grpc_tools.protoc \
        -I. \
        --python_out=. \
        --pyi_out=. \
        --grpc_python_out=. \
        ./proto/v1/*.proto

start-db:
    docker compose -f ./docker/docker-compose.yaml up -d

stop-db:
    docker compose -f ./docker/docker-compose.yaml down

run-server: start-db
    uv run python -m core.main

run-api:
    uv run python -m api.main