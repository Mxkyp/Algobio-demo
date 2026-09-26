import uuid

from sqlalchemy import CursorResult, insert, select, update

from algobio.judge0.model import J0SubmissionResponse
from algobio.model.domain import (
    Submission,
    TestCase,
    User,
    submission_list_adapter,
    test_case_list_adapter,
)
from algobio.model.schema import submission_table, test_case_table, user_table
from algobio.shared import SubmissionStatus


class SQLRepository:
    def __init__(self, engine):
        self._engine = engine
        self._insert_submission = insert(submission_table).returning(submission_table)
        self._select_submission = select(submission_table)
        self._select_user = select(user_table)
        self._insert_user = insert(user_table).returning(user_table)
        self._select_submission_status = select(submission_table.c.status)
        self._select_test_case = select(test_case_table)

    def get_user(self, id: uuid.UUID) -> User:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._select_user.where(user_table.c.id == id)
            )

            row = result.mappings().one()

            return User.model_validate(row)

    def get_user_by_email(self, email: str) -> User:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._select_user.where(user_table.c.email == email)
            )

            row = result.mappings().one()

            return User.model_validate(row)

    def insert_user(self, user: User) -> User:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._insert_user, user.model_dump(exclude_unset=True)
            )

            row = result.mappings().one()

            return User.model_validate(row)

    def record_successful_test(
        self,
        submission_id: uuid.UUID,
        j0_test_result: J0SubmissionResponse,
        total_test_number: int,
    ) -> Submission:
        with self._engine.begin() as conn:
            stmt = (
                update(submission_table)
                .where(
                    submission_table.c.id == submission_id,
                    submission_table.c.status.in_(
                        [
                            SubmissionStatus.IN_QUEUE.value,
                            SubmissionStatus.PROCESSING.value,
                        ]
                    ),
                )
                .values(
                    test_passed_number=submission_table.c.test_passed_number + 1,
                    status=SubmissionStatus.PROCESSING.value,
                    memory=j0_test_result.memory,
                    time=j0_test_result.time,
                    total_test_number=total_test_number,
                )
                .returning(submission_table)
            )

            result = conn.execute(stmt)

            row = result.mappings().one()

            return Submission.model_validate(row)

    def update_submission(
        self, submission_id: uuid.UUID, new_state: SubmissionStatus
    ) -> Submission:
        with self._engine.begin() as conn:
            stmt = (
                update(submission_table)
                .where(
                    submission_table.c.id == submission_id,
                )
                .values(
                    status=new_state.value,
                )
                .returning(submission_table)
            )

            result = conn.execute(stmt)

            row = result.mappings().one()

            return Submission.model_validate(row)

    def record_failed_submission(
        self,
        submission_id: uuid.UUID,
        status: SubmissionStatus,
        test_case_id: uuid.UUID,
        failed_stdout: str,
        failed_stderr: str,
        total_test_number: int,
    ) -> Submission:
        with self._engine.begin() as conn:
            stmt = (
                update(submission_table)
                .where(
                    submission_table.c.id == submission_id,
                )
                .values(
                    status=status.value,
                    failed_test_case_id=test_case_id,
                    stderr=failed_stderr,
                    failed_stdout=failed_stdout,
                    total_test_number=total_test_number,
                )
                .returning(submission_table)
            )

            result = conn.execute(stmt)

            row = result.mappings().one()

            return Submission.model_validate(row)

    def save_submission(self, submission: Submission) -> Submission:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._insert_submission, submission.model_dump(exclude_unset=True)
            )

            row = result.mappings().one()

            return Submission.model_validate(row)

    def get_submission(self, submission_id: uuid.UUID) -> Submission:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._select_submission.where(submission_table.c.id == submission_id)
            )

            row = result.mappings().one()

            return Submission.model_validate(row)

    def get_user_submissions_for_problem(
        self,
        user_id: uuid.UUID,
        problem_id: uuid.UUID,
    ) -> list[Submission]:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._select_submission.where(
                    submission_table.c.user_account_id == user_id,
                    submission_table.c.problem_id == problem_id,
                )
            )

            all_rows = result.mappings().all()

            return submission_list_adapter.validate_python(all_rows)

    def get_test_cases(self, problem_id: uuid.UUID) -> list[TestCase]:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._select_test_case.where(test_case_table.c.problem_id == problem_id)
            )

            all_rows = result.mappings().all()

            return test_case_list_adapter.validate_python(all_rows)

    def get_test_case(self, test_case_id: uuid.UUID) -> TestCase:
        with self._engine.begin() as conn:
            result: CursorResult = conn.execute(
                self._select_test_case.where(test_case_table.c.id == test_case_id)
            )

            row = result.mappings().one()

            return TestCase.model_validate(row)
