import base64
import binascii
from operator import call
from sys import stdout

from algobio.judge0.model import (
    J0SubmissionBulk,
    J0SubmissionRequest,
    J0SubmissionResponse,
    J0SubmissionStatus,
)
from algobio.model.api import CodeRunPostRequest, CustomTestCase
from algobio.model.domain import Submission, TestCase

_LANG_ID = {"python": 71, "rust": 73}

_ENCODED_CALLBACK_FIELDS = ["stdout", "stderr", "compile_output"]


def to_lang_id(lang: str):
    return _LANG_ID[lang]


def to_token_url_string(tokens: list[str]):
    return ",".join(tokens)


def to_submission_bulk(
    submission: Submission, test_cases: list[TestCase], callback_url: str
) -> J0SubmissionBulk:
    j0_request: list[J0SubmissionRequest] = []

    j0_lang_id = to_lang_id(submission.language)

    for case in test_cases:
        j0_request.append(
            J0SubmissionRequest(
                source_code=submission.source_code,
                language_id=j0_lang_id,
                stdin=case.stdin,
                expected_output=case.expected_output,
                callback_url=callback_url
                + f"&test_case_id={case.id}&problem_id={case.problem_id}",
            )
        )

    return J0SubmissionBulk(submissions=j0_request)


def to_code_run_bulk(request: CodeRunPostRequest) -> J0SubmissionBulk:
    j0_request: list[J0SubmissionRequest] = []

    j0_lang_id = to_lang_id(request.language_id)

    for case in request.test_cases:
        j0_request.append(
            J0SubmissionRequest(
                source_code=request.source_code,
                language_id=j0_lang_id,
                stdin=case.stdin,
                expected_output=case.stdout,
            )
        )

    return J0SubmissionBulk(submissions=j0_request)


def from_tokendict(json) -> list[str]:
    token_list = []

    for tokendict in json:
        token_list.extend(tokendict.values())

    return token_list


def decode_base64_callback(callback: J0SubmissionResponse) -> J0SubmissionResponse:
    return J0SubmissionResponse(
        stdout=_decode_base64_to_utf8(callback.stdout or ""),
        stderr=_decode_base64_to_utf8(callback.stderr or "") or "",
        time=callback.time,
        memory=callback.memory,
        status=J0SubmissionStatus(
            id=callback.status.id,
            description=_decode_base64_to_utf8(callback.status.description),
        ),
    )


def _decode_base64_to_utf8(s: str) -> str:
    try:
        return base64.b64decode(s).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return s
