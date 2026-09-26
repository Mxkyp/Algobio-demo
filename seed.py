import uuid

from sqlalchemy import Engine, insert

from algobio.dependencies import get_config, get_engine
from algobio.model.schema import (
    problem_table,
    submission_table,
    test_case_table,
    user_table,
)


def seed_data(engine: Engine = get_engine(get_config())):

    with engine.begin() as conn:
        conn.execute(test_case_table.delete())
        conn.execute(problem_table.delete())
        conn.execute(submission_table.delete())
        conn.execute(user_table.delete())

        two_sum_id = "ce94202d-48ab-4d7c-b5b4-35ac31ece4eb"
        user_id = "1b2b8c9d-8f3e-4b7a-9a4c-5d6e7f8a9b0c"

        conn.execute(
            insert(user_table).values(
                {
                    "id": user_id,
                    "email": "test@example.com",
                    "username": "testuser",
                }
            )
        )

        conn.execute(
            insert(problem_table).values(
                {
                    "id": two_sum_id,
                    "name": "Two Sum",
                    "desc": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
                }
            )
        )

        conn.execute(
            insert(test_case_table).values(
                [
                    {
                        "id": uuid.uuid4(),
                        "problem_id": two_sum_id,
                        "stdin": "[2, 7, 11, 15]\n9",
                        "expected_output": "[0, 1]",
                    },
                    {
                        "id": uuid.uuid4(),
                        "problem_id": two_sum_id,
                        "stdin": "[3, 2, 4]\n6",
                        "expected_output": "[1, 2]",
                    },
                    {
                        "id": uuid.uuid4(),
                        "problem_id": two_sum_id,
                        "stdin": "[3, 3]\n6",
                        "expected_output": "[0, 1]",
                    },
                    {
                        "id": uuid.uuid4(),
                        "problem_id": two_sum_id,
                        "stdin": "[-1, -2, -3, -4, -5]\n-8",
                        "expected_output": "[2, 4]",
                    },
                    {
                        "id": uuid.uuid4(),
                        "problem_id": two_sum_id,
                        "stdin": "[0, 4, 3, 0]\n0",
                        "expected_output": "[0, 3]",
                    },
                    {
                        "id": uuid.uuid4(),
                        "problem_id": two_sum_id,
                        "stdin": "[-5, 2, 5, 10]\n0",
                        "expected_output": "[0, 2]",
                    },
                ]
            )
        )

        print("Database successfully seeded with Two Sum and test cases!")


if __name__ == "__main__":
    seed_data()
