from sqlmodel import Session, select
from app.db.session import engine
from app.models.user import User
from app.core import security

def create_initial_user():
    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.email == "test@example.com")
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"User with email test@example.com already exists.")
            return

        new_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=security.get_password_hash("password123"),
            full_name="Test User",
            is_active=True
        )
        session.add(new_user)
        session.commit()
        print(f"Successfully created user: test@example.com / password123")

if __name__ == "__main__":
    create_initial_user()
