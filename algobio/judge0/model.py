from pydantic import BaseModel

from algobio.shared import SubmissionStatus


class J0SubmissionRequest(BaseModel):
    source_code: str
    language_id: int
    stdin: str
    expected_output: str
    callback_url: str | None = None


class J0SubmissionResponse(BaseModel):
    stdout: str | None = None
    stderr: str | None = None
    time: float
    memory: int
    compile_output: str | None = None
    status: J0SubmissionStatus


class J0SubmissionStatus(BaseModel):
    id: int
    description: str


class J0SubmissionBulk(BaseModel):
    submissions: list[J0SubmissionRequest]
