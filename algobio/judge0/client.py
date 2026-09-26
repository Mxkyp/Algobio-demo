import uuid

import ecs_logging
import httpx
from pydantic import validate_call

from algobio.judge0.model import J0SubmissionBulk
from algobio.shared import get_logger


class Judge0Client:
    def __init__(self, api_base_url, x_auth_token, x_auth_user) -> None:
        self.logger = get_logger(self.__class__.__name__, ecs_logging.StdlibFormatter())
        self.api_base = api_base_url
        self.headers = {
            "X-Auth-Token": x_auth_token,
            "X-Auth-User": x_auth_user,
            "Content-Type": "application/json",
        }

    @validate_call
    def post_submission(self, request: J0SubmissionBulk) -> dict:

        response = httpx.post(
            f"{self.api_base}/submissions/batch",
            headers=self.headers,
            data=request.model_dump_json(),
        )

        response.raise_for_status()

        return response.json()

    def get_submission(self, tokens_url_string: str):

        response = httpx.get(
            f"{self.api_base}/submissions/batch/?tokens={tokens_url_string}",
            headers=self.headers,
        )

        response.raise_for_status()

        return response.json()
