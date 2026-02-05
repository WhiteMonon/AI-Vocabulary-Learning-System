from app.db.session import engine
from sqlalchemy import text

def cleanup():
    with engine.connect() as conn:
        print("Đang xóa các types: userrole, difficultylevel, reviewquality, practicetype...")
        conn.execute(text('DROP TYPE IF EXISTS userrole, difficultylevel, reviewquality, practicetype'))
        conn.commit()
        print("Dọn dẹp hoàn tất!")

if __name__ == "__main__":
    cleanup()
