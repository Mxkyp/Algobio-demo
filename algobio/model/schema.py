from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Column,
    ForeignKey,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Table,
    text,
)

metadata = MetaData()

user_table = Table(
    "user_account",
    metadata,
    Column("id", UUID(as_uuid=True), server_default=text("uuidv7()"), primary_key=True),
    Column("email", String(length=50), nullable=False),
    Column("username", String(length=50), nullable=False),
)

problem_table = Table(
    "problem",
    metadata,
    Column("id", UUID(as_uuid=True), server_default=text("uuidv7()"), primary_key=True),
    Column("name", String(length=100), nullable=False),
    Column("desc", String(length=2000), nullable=False),
)

test_case_table = Table(
    "test_case",
    metadata,
    Column("id", UUID(as_uuid=True), server_default=text("uuidv7()"), primary_key=True),
    Column("stdin", String(length=100), nullable=False),
    Column("expected_output", String(length=100), nullable=False),
    Column("problem_id", UUID(as_uuid=True), ForeignKey("problem.id"), nullable=False),
)

submission_table = Table(
    "submission",
    metadata,
    Column("id", UUID(as_uuid=True), server_default=text("uuidv7()"), primary_key=True),
    Column(
        "user_account_id",
        UUID(as_uuid=True),
        ForeignKey("user_account.id"),
        nullable=False,
    ),
    Column("problem_id", UUID(as_uuid=True), ForeignKey("problem.id"), nullable=False),
    Column("source_code", String(length=2000), nullable=False),
    Column("memory", Numeric(precision=7, scale=2), nullable=True),
    Column("time", Numeric(precision=7, scale=3), nullable=True),
    Column("date", TIMESTAMP(timezone=True), nullable=True),
    Column("language", String(length=20), nullable=False),
    Column("status", String(length=20), nullable=False),
    Column("stderr", String(length=300), nullable=True),
    Column("test_passed_number", SmallInteger, nullable=True),
    Column("total_test_number", SmallInteger, nullable=True),
    Column(
        "failed_test_case_id",
        UUID(as_uuid=True),
        ForeignKey("test_case.id"),
        nullable=True,
    ),
    Column("failed_stdout", String(length=100), nullable=True),
)
