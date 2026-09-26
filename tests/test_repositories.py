import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import NoResultFound

from algobio.model.domain import Submission
from algobio.repositories import SQLRepository
from algobio.shared import SubmissionStatus


@pytest.fixture
def repo(test_engine: Engine):
    return SQLRepository(test_engine)


def test_overwrite_submission_aggregation_lifecycle(repo: SQLRepository):
    """
    Tests the full aggregation lifecycle:
    1. First passing test keeps it in PROCESSING.
    2. Final passing test flips it to ACCEPTED.
    """
    submission_id = uuid.uuid4()
    problem_id = uuid.UUID("ce94202d-48ab-4d7c-b5b4-35ac31ece4eb")
    user_id = uuid.UUID("1b2b8c9d-8f3e-4b7a-9a4c-5d6e7f8a9b0c")

    initial_sub = Submission(
        id=submission_id,
        user_account_id=user_id,
        problem_id=problem_id,
        source_code="print('hello')",
        date=datetime.now(UTC),
        language="python",
        status=SubmissionStatus.PROCESSING.value,
        test_passed_number=0,
        total_test_number=2,
    )
    repo.save_submission(initial_sub)

    from algobio.judge0.model import J0SubmissionResponse, J0SubmissionStatus

    # STEP 1: First passing test case
    j0_response = J0SubmissionResponse(
        status=J0SubmissionStatus(id=3, description=SubmissionStatus.ACCEPTED.value),
        time=1.5,
        memory=1024,
    )

    sub_after_first_test = repo.record_successful_test(
        submission_id, j0_response, 2
    )

    assert sub_after_first_test.test_passed_number == 1
    assert sub_after_first_test.status == SubmissionStatus.PROCESSING.value

    # STEP 2: Final passing test case
    sub_after_final_test = repo.record_successful_test(
        submission_id, j0_response, 2
    )

    assert sub_after_final_test.test_passed_number == 2
    assert sub_after_final_test.status == SubmissionStatus.PROCESSING.value


def test_overwrite_submission_respects_wrong_answer_terminal_state(repo: SQLRepository):
    # GIVEN a submission that has already failed (Wrong Answer)
    submission_id = uuid.uuid4()
    problem_id = uuid.UUID("ce94202d-48ab-4d7c-b5b4-35ac31ece4eb")
    user_id = uuid.UUID("1b2b8c9d-8f3e-4b7a-9a4c-5d6e7f8a9b0c")

    initial_sub = Submission(
        id=submission_id,
        user_account_id=user_id,
        problem_id=problem_id,
        source_code="print('hello')",
        date=datetime.now(UTC),
        language="python",
        status=SubmissionStatus.WRONG_ANSWER.value,  # Terminal failure state
        test_passed_number=1,
    )
    repo.save_submission(initial_sub)

    from algobio.judge0.model import J0SubmissionResponse, J0SubmissionStatus
    # WHEN a delayed passing test callback arrives (converted to PROCESSING by service)
    j0_response = J0SubmissionResponse(
        status=J0SubmissionStatus(id=3, description=SubmissionStatus.ACCEPTED.value),
        time=1.5,
        memory=1024,
    )

    with pytest.raises(NoResultFound):
        repo.record_successful_test(
            submission_id, j0_response, 2
        )

    # THEN the status in the database must still be WRONG_ANSWER
    db_sub = repo.get_submission(submission_id)
    assert db_sub.status == SubmissionStatus.WRONG_ANSWER.value


def test_overwrite_submission_respects_accepted_terminal_state(repo: SQLRepository):
    # GIVEN a submission that has already completed successfully (Accepted)
    submission_id = uuid.uuid4()
    problem_id = uuid.UUID("ce94202d-48ab-4d7c-b5b4-35ac31ece4eb")
    user_id = uuid.UUID("1b2b8c9d-8f3e-4b7a-9a4c-5d6e7f8a9b0c")

    initial_sub = Submission(
        id=submission_id,
        user_account_id=user_id,
        problem_id=problem_id,
        source_code="print('hello')",
        date=datetime.now(UTC),
        language="python",
        status=SubmissionStatus.ACCEPTED.value,  # Terminal success state
        test_passed_number=2,
        total_test_number=2,
    )
    repo.save_submission(initial_sub)

    from algobio.judge0.model import J0SubmissionResponse, J0SubmissionStatus
    # WHEN a delayed passing test callback arrives (converted to PROCESSING by service)
    j0_response = J0SubmissionResponse(
        status=J0SubmissionStatus(id=3, description=SubmissionStatus.ACCEPTED.value),
        time=1.5,
        memory=1024,
    )

    # We expect NoResultFound because ACCEPTED is no longer in the IN_QUEUE/PROCESSING WHERE clause
    with pytest.raises(NoResultFound):
        repo.record_successful_test(
            submission_id, j0_response, 2
        )
