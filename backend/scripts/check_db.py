from sqlmodel import Session, select
from app.db.session import engine
from app.models.user import User

with Session(engine) as session:
    users = session.exec(select(User)).all()
    print(f"DEBUG: Found {len(users)} users")
    for u in users:
        print(f"DEBUG: User: {u.email}, active: {u.is_active}")
