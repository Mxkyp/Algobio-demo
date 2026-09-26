from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from algobio.shared import SubmissionStatus


class SubmissionPostRequest(BaseModel):
    source_code: str
    language_id: str
    problem_id: UUID


class TokenList(BaseModel):
    tokens: list[str]


class CustomTestCase(BaseModel):
    stdin: str
    stdout: str


class CodeRunPostRequest(BaseModel):
    source_code: str
    language_id: str
    problem_id: UUID
    test_cases: list[CustomTestCase]


class CodeRunStatus(BaseModel):
    status: SubmissionStatus
    stdout: str
    stderr: str | None = None


class SubmissionPostResponse(BaseModel):
    id: UUID | None


class SubmissionGetResponse(BaseModel):
    source_code: str
    memory: Decimal | None = None
    time: Decimal | None = None
    date: datetime | None = None
    language: str
    status: str | None = None
    stderr: str | None
    test_passed_number: int | None = None
    total_test_number: int | None = None
    failed_test_case_id: UUID | None = None
    failed_stdout: str | None = None
