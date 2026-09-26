from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, TypeAdapter


class User(BaseModel):
    id: UUID | None = None
    email: str = Field(max_length=50)
    username: str = Field(max_length=50)


class Submission(BaseModel):
    id: UUID | None = None
    user_account_id: UUID
    problem_id: UUID
    source_code: str = Field(..., max_length=2000)
    memory: Decimal | None = Field(default=None, max_digits=7, decimal_places=2)
    time: Decimal | None = Field(default=None, max_digits=7, decimal_places=3)
    date: datetime
    language: str = Field(..., max_length=20)
    status: str = Field(..., max_length=20)
    stderr: str | None = Field(default=None, max_length=300)

    test_passed_number: int | None = None
    total_test_number: int | None = None

    failed_test_case_id: UUID | None = None
    failed_stdout: str | None = Field(default=None, max_length=100)


class TestCase(BaseModel):
    id: UUID
    stdin: str
    expected_output: str
    problem_id: UUID


test_case_list_adapter = TypeAdapter(list[TestCase])

submission_list_adapter = TypeAdapter(list[Submission])
