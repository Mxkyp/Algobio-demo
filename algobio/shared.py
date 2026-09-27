import logging
from enum import StrEnum, auto

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    x_auth_token: str
    x_auth_user: str
    api_base_url: str
    db_username: str
    db_pass: str
    db_port: str
    db_host: str
    db_name: str
    judge0_api_key: str | None = None
    judge0_host: str
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    jwt_secret_key: str
    frontend_url: str = "http://localhost:5173"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True
    )


def get_logger(name: str, stdlibFormatter: logging.Formatter) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setFormatter(stdlibFormatter)
    logger.addHandler(handler)
    return logger


class ErrorCode(StrEnum):
    SUBMISSION_NOT_FOUND = auto()


class SubmissionStatus(StrEnum):
    IN_QUEUE = "In Queue"
    PROCESSING = "Processing"
    ACCEPTED = "Accepted"
    WRONG_ANSWER = "Wrong Answer"
    TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"
    COMPILATION_ERROR = "Compilation Error"
    RUNTIME_ERROR_SIGSEGV = "Runtime Error (SIGSEGV)"
    RUNTIME_ERROR_SIGXFSZ = "Runtime Error (SIGXFSZ)"
    RUNTIME_ERROR_SIGFPE = "Runtime Error (SIGFPE)"
    RUNTIME_ERROR_SIGABRT = "Runtime Error (SIGABRT)"
    RUNTIME_ERROR_NZEC = "Runtime Error (NZEC)"
    RUNTIME_ERROR_OTHER = "Runtime Error (Other)"
    INTERNAL_ERROR = "Internal Error"
    EXEC_FORMAT_ERROR = "Exec Format Error"
