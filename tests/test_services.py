import uuid
from unittest.mock import Mock

import pytest

from algobio.services import ProblemService
from algobio.shared import SubmissionStatus


@pytest.fixture
def mock_repo():
    repo = Mock()
    # Mock total test cases to 5
    repo.get_test_cases.return_value = [Mock()] * 5
    return repo


@pytest.fixture
def problem_service(mock_repo):
    j0_client = Mock()
    callback_url = "http://test.local/submit/SAVED_SUB_ID?token=xyz"
    return ProblemService(mock_repo, j0_client, callback_url)


def test_update_submission_for_passed_test_not_final(problem_service: ProblemService, mock_repo):
    # GIVEN a successful judge0 callback response for a non-final test
    problem_id = uuid.uuid4()
    test_case_id = uuid.uuid4()
    submission_id = uuid.uuid4()
    
    from algobio.judge0.model import J0SubmissionResponse, J0SubmissionStatus
    from algobio.model.domain import Submission
    from datetime import datetime, UTC
    
    j0_response = J0SubmissionResponse(
        time=0.1,
        memory=1024,
        stdout="expected output",
        status=J0SubmissionStatus(id=3, description=SubmissionStatus.ACCEPTED),
    )

    updated_sub = Submission(
        id=submission_id,
        user_account_id=uuid.uuid4(),
        problem_id=problem_id,
        source_code="print()",
        date=datetime.now(UTC),
        language="python",
        status=SubmissionStatus.PROCESSING.value,
        test_passed_number=1,
        total_test_number=5,
    )
    mock_repo.record_successful_test.return_value = updated_sub

    # WHEN we update the submission
    result = problem_service.update_submission(submission_id, test_case_id, problem_id, j0_response)

    # THEN it delegates to record_successful_test
    mock_repo.record_successful_test.assert_called_once()
    assert result == updated_sub
    mock_repo.update_submission.assert_not_called()


def test_update_submission_for_failed_test(problem_service: ProblemService, mock_repo):
    # GIVEN a failed judge0 callback response
    problem_id = uuid.uuid4()
    test_case_id = uuid.uuid4()
    submission_id = uuid.uuid4()
    
    from algobio.judge0.model import J0SubmissionResponse, J0SubmissionStatus
    
    j0_response = J0SubmissionResponse(
        time=0.1,
        memory=1024,
        stdout="wrong output",
        status=J0SubmissionStatus(id=4, description=SubmissionStatus.WRONG_ANSWER),
    )

    # WHEN we update the submission
    problem_service.update_submission(submission_id, test_case_id, problem_id, j0_response)

    # THEN it delegates to record_failed_submission
    mock_repo.record_failed_submission.assert_called_once_with(
        submission_id,
        SubmissionStatus.WRONG_ANSWER,
        test_case_id,
        "wrong output",
        "",
        5
    )
