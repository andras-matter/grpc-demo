from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_address: str = "[::]:50051"
    max_workers: int = 10
    db_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/user"
