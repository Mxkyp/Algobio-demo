from functools import cache

from fastapi import Depends
from sqlalchemy import Engine, create_engine

from algobio.auth.services import AuthService
from algobio.judge0.client import Judge0Client
from algobio.repositories import SQLRepository
from algobio.services import ProblemService
from algobio.shared import Config


@cache
def get_config() -> Config:
    return Config()


@cache
def get_engine(config: Config = Depends(get_config)) -> Engine:
    database_uri = f"postgresql+psycopg2://{config.db_username}:{config.db_pass}@{config.db_host}:{config.db_port}/{config.db_name}"
    return create_engine(database_uri, echo=True)


@cache
def get_repository(engine: Engine = Depends(get_engine)) -> SQLRepository:
    return SQLRepository(engine)


@cache
def get_j0_client(config: Config = Depends(get_config)) -> Judge0Client:
    return Judge0Client(
        config.api_base_url,
        config.x_auth_token,
        config.x_auth_user,
    )


@cache
def get_problem_service(
    repository: SQLRepository = Depends(get_repository),
    j0_client: Judge0Client = Depends(get_j0_client),
    config: Config = Depends(get_config),
) -> ProblemService:
    judge0_callback_url = (
        f"{config.judge0_host}/judge0/submit/SAVED_SUB_ID?token={config.judge0_api_key}"
    )
    return ProblemService(repository, j0_client, judge0_callback_url)


@cache
def get_auth_service(
    repository: SQLRepository = Depends((get_repository)),
    config: Config = Depends(get_config),
):
    return AuthService(repository, config.jwt_secret_key)
