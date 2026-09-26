import uuid

import ecs_logging
import sqlalchemy.exc as sql_exception
from fastapi import Depends, FastAPI, HTTPException, status

from algobio.auth.callback import router as auth_router
from algobio.auth.security import get_current_user
from algobio.dependencies import get_problem_service
from algobio.judge0.callback import router as judge0_callback_router
from algobio.model.api import (
    CodeRunPostRequest,
    SubmissionGetResponse,
    SubmissionPostRequest,
    SubmissionPostResponse,
    TokenList,
)
from algobio.model.domain import TestCase, User
from algobio.services import ProblemService
from algobio.shared import ErrorCode, get_logger

app = FastAPI(debug=True)
app.include_router(judge0_callback_router)
app.include_router(auth_router)

logger = get_logger(__name__, ecs_logging.StdlibFormatter())


@app.get("/users/me")
def get_me(current_user=Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email}


@app.post(
    "/submit",
    status_code=status.HTTP_201_CREATED,
    response_model=SubmissionPostResponse,
)
async def create_submission(
    request: SubmissionPostRequest,
    problem_service: ProblemService = Depends(get_problem_service),
    current_user=Depends(get_current_user),
):
    response = problem_service.run_submission(request, current_user)

    return response


@app.post("/run", status_code=status.HTTP_201_CREATED, response_model=TokenList)
async def run_code(
    request: CodeRunPostRequest,
    problem_service: ProblemService = Depends(get_problem_service),
    current_user=Depends(get_current_user),
):
    return problem_service.run_code(request)


@app.get(
    "/run/{token}",
    status_code=status.HTTP_201_CREATED,
)
async def get_run_result(
    token: str,
    problem_service: ProblemService = Depends(get_problem_service),
    current_user=Depends(get_current_user),
):
    return problem_service.get_code_run_from_j0(token)


@app.get(
    "/submit/{submission_id}",
    status_code=status.HTTP_200_OK,
    response_model=SubmissionGetResponse,
)
async def get_submission(
    submission_id: uuid.UUID,
    problem_service: ProblemService = Depends(get_problem_service),
    current_user=Depends(get_current_user),
):
    try:
        result = problem_service.get_submission(submission_id)
    except sql_exception.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.SUBMISSION_NOT_FOUND.value,
                "message": f"No submission found for ID {submission_id}",
            },
        )

    return result


@app.get(
    "/submit/{problem_id}/me",
    status_code=status.HTTP_200_OK,
    response_model=list[SubmissionGetResponse],
)
async def get_user_submissions(
    problem_id: uuid.UUID,
    problem_service: ProblemService = Depends(get_problem_service),
    current_user: User = Depends(get_current_user),
):
    try:
        result = problem_service.get_user_submission_for_problem(
            current_user.id,  # ty: ignore[invalid-argument-type]
            problem_id,
        )
    except sql_exception.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.SUBMISSION_NOT_FOUND.value,
                "message": f"No submissios found for user_id {current_user.id} and problem_id {problem_id}",
            },
        )

    return result


@app.get(
    "/test/{id}",
    status_code=status.HTTP_200_OK,
    response_model=TestCase,
)
async def get_test_case(
    id: uuid.UUID,
    problem_service: ProblemService = Depends(get_problem_service),
    current_user: User = Depends(get_current_user),
):
    try:
        result = problem_service.get_test_case(id)
    except sql_exception.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.SUBMISSION_NOT_FOUND.value,
                "message": f"No test_case found for test_case_id {id}",
            },
        )

    return result
