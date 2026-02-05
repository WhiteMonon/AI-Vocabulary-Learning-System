"""Test configuration và fixtures."""
import pytest
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

# Mock environment variables BEFORE any application code is imported
import os
os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "test"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["SECRET_KEY"] = "test_secret_key"

import app.db.session as db_session
import app.db.init_db as db_init
# We need to monkeypatch app.main.init_db specifically
import app.main as app_main_module

# Import FastAPI instance with an alias to avoid shadowing package 'app'
from app.main import app as fastapi_app

# Import models at top level for typing
from app.models.user import User
from app.models.vocabulary import Vocabulary
from app.models.review_history import ReviewHistory
from app.models.ai_practice_log import AIPracticeLog

# Tạo một shared engine cho testing (session-scoped)
# Dùng StaticPool để in-memory DB tồn tại suốt vòng đời engine
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Khởi tạo tables một lần duy nhất cho toàn bộ session
    SQLModel.metadata.create_all(engine)
    
    # Override global engine và init_db
    db_session.engine = engine
    db_init.init_db = lambda: None
    app_main_module.init_db = lambda: None
    
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """
    Tạo database session cho testing.
    Dọn dẹp data sau mỗi test.
    """
    with Session(engine) as session:
        yield session
        # Dọn dẹp dữ liệu để các test case độc lập
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Tạo test client với database session override.
    """
    def get_session_override():
        return session
    
    from app.api.deps import get_db
    fastapi_app.dependency_overrides[get_db] = get_session_override
    
    with TestClient(fastapi_app) as client:
        yield client
    
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(name="normal_user")
def normal_user_fixture(session: Session) -> User:
    """Tạo một user mẫu trong database."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_client")
def auth_client_fixture(client: TestClient, normal_user: User) -> TestClient:
    """Tạo client đã được mock authenticate."""
    from app.api.deps import get_current_user
    def get_current_user_override():
        return normal_user
    
    fastapi_app.dependency_overrides[get_current_user] = get_current_user_override
    yield client
    fastapi_app.dependency_overrides.pop(get_current_user, None)
