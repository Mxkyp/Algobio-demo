import uuid
from datetime import UTC, datetime

import ecs_logging

from algobio.judge0 import adapter
from algobio.judge0.client import Judge0Client
from algobio.judge0.model import J0SubmissionResponse
from algobio.model.api import (
    CodeRunPostRequest,
    CodeRunStatus,
    SubmissionPostRequest,
    TokenList,
)
from algobio.model.domain import Submission, TestCase, User
from algobio.repositories import SQLRepository
from algobio.shared import SubmissionStatus, get_logger


class ProblemService:
    def __init__(
        self,
        repository: SQLRepository,
        j0_client: Judge0Client,
        j0_callback_url: str,
    ):
        self.repo = repository
        self.logger = get_logger(__name__, ecs_logging.StdlibFormatter())
        self.j0_client = j0_client
        self.j0_callback_url = j0_callback_url

    def update_submission(
        self,
        submission_id: uuid.UUID,
        test_case_id: uuid.UUID,
        problem_id: uuid.UUID,
        run_result: J0SubmissionResponse,
    ) -> Submission:
        decoded_run_result: J0SubmissionResponse = adapter.decode_base64_callback(
            run_result
        )

        total_test_number = len(self.repo.get_test_cases(problem_id))

        if decoded_run_result.status.description != SubmissionStatus.ACCEPTED:
            return self.repo.record_failed_submission(
                submission_id,
                decoded_run_result.status.description,
                test_case_id,
                decoded_run_result.stdout,
                decoded_run_result.stderr,
                total_test_number,
            )

        updated_sub: Submission = self.repo.record_successful_test(
            submission_id, decoded_run_result, total_test_number
        )

        if updated_sub.test_passed_number == total_test_number:
            return self.repo.update_submission(submission_id, SubmissionStatus.ACCEPTED)

        return updated_sub

    def run_submission(
        self, submission: SubmissionPostRequest, user: User
    ) -> Submission:
        initial_submission = Submission(
            user_account_id=user.id,  # ty: ignore[invalid-argument-type]
            problem_id=submission.problem_id,
            date=datetime.now(UTC),
            test_passed_number=0,
            source_code=submission.source_code,
            language=submission.language_id,
            status=SubmissionStatus.IN_QUEUE.value,
        )

        saved_submission = self.repo.save_submission(initial_submission)

        test_cases = self.repo.get_test_cases(submission.problem_id)

        callback_url = self.j0_callback_url.replace(
            "SAVED_SUB_ID", str(saved_submission.id)
        )

        j0_request = adapter.to_submission_bulk(
            saved_submission, test_cases, callback_url
        )

        self.j0_client.post_submission(j0_request)

        return saved_submission

    def run_code(self, request: CodeRunPostRequest) -> TokenList:
        j0_request = adapter.to_code_run_bulk(request)

        token_list = adapter.from_tokendict(self.j0_client.post_submission(j0_request))

        return TokenList(tokens=token_list)

    def get_code_run_from_j0(self, token: str):
        j0_submission_response = self.j0_client.get_submission(token)

        status = j0_submission_response["submissions"][0]["status"]["description"]
        stdout = j0_submission_response["submissions"][0]["stdout"]
        stderr = j0_submission_response["submissions"][0]["stderr"]

        return CodeRunStatus(status=status, stdout=stdout, stderr=stderr)

    def get_submission(self, submission_id: uuid.UUID) -> Submission:
        return self.repo.get_submission(submission_id)

    def get_user_submission_for_problem(
        self, user_id: uuid.UUID, problem_id: uuid.UUID
    ) -> list[Submission]:
        return self.repo.get_user_submissions_for_problem(user_id, problem_id)

    def get_test_case(self, test_case_id: uuid.UUID) -> TestCase:
        return self.repo.get_test_case(test_case_id)
