import uuid

import sqlalchemy.exc as sql_exception
from fastapi import APIRouter, Depends, HTTPException, status

from algobio.dependencies import get_config, get_problem_service
from algobio.judge0.model import J0SubmissionResponse
from algobio.model.domain import Submission
from algobio.services import ProblemService
from algobio.shared import Config, ErrorCode, SubmissionStatus


def verify_callback_token(token: str, config: Config = Depends(get_config)):
    if token != config.judge0_api_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "wrong_judge0_token")


router = APIRouter(
    prefix="/judge0",
    tags=["webhooks", "internal"],
    dependencies=[Depends(verify_callback_token)],
)


@router.put(
    "/submit/{submission_id}",
    status_code=status.HTTP_200_OK,
)
async def judge0_update_submission(
    submission_id: uuid.UUID,
    test_case_id: uuid.UUID,
    problem_id: uuid.UUID,
    run_result: J0SubmissionResponse,
    problem_service: ProblemService = Depends(get_problem_service),
) -> Submission:

    try:
        submission = problem_service.get_submission(submission_id)
    except sql_exception.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.SUBMISSION_NOT_FOUND.value,
                "message": f"No submission found for ID {submission_id}",
            },
        )

    if submission.status not in [
        SubmissionStatus.IN_QUEUE,
        SubmissionStatus.PROCESSING,
        SubmissionStatus.ACCEPTED,
    ]:
        raise HTTPException(status.HTTP_204_NO_CONTENT, "submission_already_failed")

    try:
        return problem_service.update_submission(
            submission_id, test_case_id, problem_id, run_result
        )
    except sql_exception.NoResultFound:
        raise HTTPException(status.HTTP_204_NO_CONTENT, "submission_already_failed")
