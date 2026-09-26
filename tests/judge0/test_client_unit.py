import json
import unittest
from cmath import exp

import httpretty
import pytest
from pydantic import ValidationError

from algobio.judge0.client import Judge0Client
from algobio.judge0.model import J0SubmissionBulk, J0SubmissionRequest
from algobio.shared import Config


class Judge0ClientUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Config()
        self.judge0_client = Judge0Client(
            self.settings.api_base_url,
            self.settings.x_auth_token,
            self.settings.x_auth_user,
        )

    @httpretty.activate(verbose=True, allow_net_connect=True)
    def test_should_return_200_when_correct_request(self):

        # given
        correct_body = J0SubmissionRequest(
            source_code="abc", language_id=48, stdin="world", expected_output="25", callback_url="http://test.com/webhook"
        )

        expected_response = '{"token": "1234567"}'

        httpretty.register_uri(
            httpretty.POST,
            "http://localhost:2358/submissions/batch",
            body=expected_response,
        )

        # when
        response = self.judge0_client.post_submission(
            J0SubmissionBulk(submissions=[correct_body])
        )

        # then
        assert response["token"] == "1234567"

    @httpretty.activate(verbose=True, allow_net_connect=True)
    def test_should_return_400_when_incorrect_body(self):

        # given
        incorrect_body = "Incorrect body"

        expected_response = None

        httpretty.register_uri(
            httpretty.POST,
            "http://localhost:2358/submissions/batch",
            body=expected_response,
        )

        # when & then
        with pytest.raises(ValidationError):
            self.judge0_client.post_submission(incorrect_body)


if __name__ == "__main__":
    unittest.main()
