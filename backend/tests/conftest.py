"""Test configuration và fixtures."""
import pytest
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_db


# In-memory SQLite database cho testing
@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Tạo database session cho testing.
    Sử dụng in-memory SQLite.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Tạo test client với database session override.
    """
    def get_session_override():
        return session
    
    app.dependency_overrides[get_db] = get_session_override
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()
