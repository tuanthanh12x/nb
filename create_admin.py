# create_admin.py

import bcrypt
from db.database import get_db_session, User


def create_admin_user():
    """Tạo người dùng admin nếu chưa tồn tại."""
    db = get_db_session()

    # Kiểm tra xem admin đã tồn tại chưa
    admin_exists = db.query(User).filter(User.username == 'admin').first()

    if not admin_exists:
        print("Đang tạo người dùng 'admin'...")

        # Mật khẩu gốc là 'admin'
        password = b'admin'

        # Băm mật khẩu
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Tạo đối tượng User mới
        new_admin = User(
            username='admin',
            password_hash=hashed_password.decode('utf-8'),  # Lưu dưới dạng chuỗi
            role='admin'
        )

        # Thêm vào session và commit
        db.add(new_admin)
        db.commit()

        print("Đã tạo người dùng 'admin' với mật khẩu 'admin' thành công.")
    else:
        print("Người dùng 'admin' đã tồn tại.")

    db.close()


if __name__ == '__main__':
    create_admin_user()