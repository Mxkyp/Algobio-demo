import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from testcontainers.postgres import PostgresContainer

from algobio.dependencies import get_engine, get_j0_client
from main import app
from seed import seed_data


class MockJudge0Client:
    def post_submission(self, request):
        return json.loads("""[
      {
        "token": "db54881d-bcf5-4c7b-a2e3-d33fe7e25de7"
      },
      {
        "token": "ecc52a9b-ea80-4a00-ad50-4ab6cc3bb2a1"
      },
      {
        "token": "1b35ec3b-5776-48ef-b646-d5522bdeb2cc"
      }
    ]
    """)

    def get_submission(self, tokens):
        return json.loads("""
    {
  "submissions": [
    {
      "stdout": null,
      "time": null,
      "memory": null,
      "stderr": null,
      "token": "b648e847-c7b5-498b-8f43-8cf5e31fd176",
      "compile_output": null,
      "message": null,
      "status": {
        "id": 1,
        "description": "In Queue"
      }
    },
    {
      "stdout": null,
      "time": null,
      "memory": null,
      "stderr": null,
      "token": "c78a2a48-83bf-4d70-a36d-f00baeb2446a",
      "compile_output": null,
      "message": null,
      "status": {
        "id": 1,
        "description": "In Queue"
      }
    },
    {
      "stdout": null,
      "time": null,
      "memory": null,
      "stderr": null,
      "token": "eb7119eb-c722-48ec-b8f6-8d02f359d14d",
      "compile_output": null,
      "message": null,
      "status": {
        "id": 1,
        "description": "In Queue"
      }
    }
  ]
}
""")


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:18-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def test_engine(postgres_container: PostgresContainer):
    db_url = postgres_container.get_connection_url()

    project_root = Path(__file__).parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    migrations_dir = project_root / "migrations"

    alembic_cfg = AlembicConfig(str(alembic_ini_path))

    alembic_cfg.set_main_option("script_location", str(migrations_dir))

    engine = create_engine(db_url, echo=True)

    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    seed_data(engine)

    yield engine


@pytest.fixture(scope="module")
def client(test_engine: Engine):
    app.dependency_overrides[get_engine] = lambda: test_engine
    app.dependency_overrides[get_j0_client] = lambda: MockJudge0Client()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
