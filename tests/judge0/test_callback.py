import uuid
from unittest.mock import Mock

from fastapi import status
from sqlalchemy.exc import NoResultFound

from algobio.dependencies import get_problem_service
from main import app


def test_orphaned_webhook_returns_appropriate_status(client):
    """
    If Judge0 sends a callback for a submission ID that doesn't exist 
    in our database (e.g. it was deleted or rolled back),
    we should not return a 500 error, as that causes Judge0 to retry pointlessly.
    """
    # GIVEN a problem service that raises NoResultFound when looking up the submission
    mock_problem_service = Mock()
    mock_problem_service.get_submission.side_effect = NoResultFound()
    
    mock_config = Mock()
    mock_config.judge0_api_key = "test_token"
    
    app.dependency_overrides[get_problem_service] = lambda: mock_problem_service
    # Import get_config to override it
    from algobio.dependencies import get_config
    app.dependency_overrides[get_config] = lambda: mock_config

    non_existent_submission_id = str(uuid.uuid4())
    test_case_id = str(uuid.uuid4())
    problem_id = str(uuid.uuid4())
    
    payload = {
        "time": 0.1,
        "memory": 1024,
        "status": {"id": 3, "description": "Accepted"}
    }
    
    # WHEN the webhook hits the endpoint
    # Note: we need the correct token so verify_callback_token passes
    # The config fixture isn't mocked here, but if we need to mock config, we should.
    # We will assume config is loaded or we can mock get_config if needed.
    
    response = client.put(
        f"/judge0/submit/{non_existent_submission_id}?test_case_id={test_case_id}&problem_id={problem_id}&token=test_token",
        json=payload
    )

    # Clean up override
    app.dependency_overrides.pop(get_problem_service, None)
    app.dependency_overrides.pop(get_config, None)

    # THEN it should return a 404 Not Found (or 204 No Content), but definitely NOT a 500
    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_204_NO_CONTENT]
