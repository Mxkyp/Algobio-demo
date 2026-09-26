import base64

from algobio.judge0.adapter import decode_base64_callback
from algobio.judge0.model import J0SubmissionResponse, J0SubmissionStatus


def test_callback_to_decoded_base64_dict_decodes_fields():
    # GIVEN a judge0 response with base64 encoded stdout and status description
    encoded_stdout = base64.b64encode(b"hello world").decode("utf-8")
    encoded_status = base64.b64encode(b"Accepted").decode("utf-8")

    response = J0SubmissionResponse(
        time=0.1,
        memory=1024,
        stdout=encoded_stdout,
        stderr=None,
        compile_output=None,
        status=J0SubmissionStatus(id=3, description=encoded_status),
    )

    # WHEN we decode
    result = decode_base64_callback(response)

    # THEN the specific fields are decoded correctly
    assert result.stdout == "hello world"
    assert result.status.description == "Accepted"

    # THEN fields that are missing/None default correctly
    assert result.stderr == ""
    assert result.compile_output is None

    # THEN numeric fields are untouched
    assert result.time == 0.1
    assert result.memory == 1024


def test_callback_to_decoded_base64_dict_handles_invalid_base64():
    # GIVEN a judge0 response where fields are somehow NOT valid base64
    response = J0SubmissionResponse(
        time=0.1,
        memory=1024,
        stdout="not_valid_base64_!!!",
        stderr=None,
        compile_output=None,
        status=J0SubmissionStatus(id=3, description="plain text status"),
    )

    # WHEN we decode
    result = decode_base64_callback(response)

    # THEN it falls back to the original string gracefully
    assert result.stdout == "not_valid_base64_!!!"
    assert result.status.description == "plain text status"
