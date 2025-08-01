# database.py

import sys
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PyQt5.QtWidgets import QMessageBox

# --- CẤU HÌNH KẾT NỐI ---
# Thay thế các giá trị này bằng thông tin của bạn
DB_USER = "postgres"  # Tên người dùng postgres của bạn
DB_PASSWORD = "your_password" # Mật khẩu của bạn
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "app_vanban" # Tên cơ sở dữ liệu

# Chuỗi kết nối theo định dạng của SQLAlchemy
DATABASE_URL = f"postgresql+psycopg2://neondb_owner:npg_XVaJUO4dTz0m@ep-divine-cell-a1ra9c1d-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# --- THIẾT LẬP SQLALCHEMY ---
try:
    # Tạo một "engine" kết nối đến cơ sở dữ liệu
    engine = create_engine(DATABASE_URL)

    # Tạo một "Session" để quản lý các giao dịch với DB
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Base class cho các mô hình ORM
    Base = declarative_base()

except Exception as e:
    # Hiển thị lỗi nếu không kết nối được và thoát
    QMessageBox.critical(None, "Lỗi kết nối CSDL", f"Không thể kết nối đến PostgreSQL:\n{e}")
    sys.exit(1)


# --- ĐỊNH NGHĨA MÔ HÌNH (MODEL) ---

# Tạo một sequence để tự động tăng ID, tương thích với PostgreSQL
user_id_seq = Sequence('user_id_seq')

class User(Base):
    """
    Mô hình đại diện cho bảng 'users' trong cơ sở dữ liệu.
    """
    __tablename__ = "users"

    id = Column(Integer, user_id_seq, primary_key=True, server_default=user_id_seq.next_value())
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False) # Sẽ lưu mật khẩu đã được băm
    role = Column(String(20), nullable=False, default='guest') # VD: 'admin', 'guest'
    full_name = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

# --- HÀM TIỆN ÍCH ---
def create_tables():
    """
    Tạo tất cả các bảng trong cơ sở dữ liệu nếu chúng chưa tồn tại.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("Đã tạo bảng thành công (hoặc bảng đã tồn tại).")
    except Exception as e:
        print(f"Lỗi khi tạo bảng: {e}")

def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        # Chú ý: trong ứng dụng desktop, bạn thường sẽ đóng session
        # khi hoàn thành một tác vụ cụ thể, không phải ngay lập tức như trong web.
        # db.close() # Tạm thời không đóng ở đây
        pass

if __name__ == '__main__':
    print("Đang tạo bảng trong cơ sở dữ liệu...")
    create_tables()