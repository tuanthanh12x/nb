import sys
import os
import getpass
import hashlib
import psycopg2

# --- Cấu hình đường dẫn để script có thể import các module của dự án ---
# Dòng này thêm thư mục gốc của dự án (your_project) vào Python path
# để chúng ta có thể import `db.db` thành công.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from db.db import get_conn


def hash_password(password):
    """Băm mật khẩu sử dụng SHA256, phải giống hệt hàm trong user_manager.py."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin_user():
    """Hàm chính để tạo người dùng admin qua dòng lệnh."""
    print("--- SCRIPT TẠO TÀI KHOẢN ADMIN ---")

    try:
        # 1. Lấy thông tin từ người dùng
        username = input("Nhập tên đăng nhập cho admin: ").strip()
        if not username:
            print("Lỗi: Tên đăng nhập không được để trống. Đã hủy.")
            return

        # Sử dụng getpass để nhập mật khẩu một cách an toàn (không hiển thị trên màn hình)
        password = getpass.getpass("Nhập mật khẩu: ")
        if not password:
            print("Lỗi: Mật khẩu không được để trống. Đã hủy.")
            return

        password_confirm = getpass.getpass("Xác nhận lại mật khẩu: ")

        if password != password_confirm:
            print("Lỗi: Mật khẩu không khớp. Đã hủy.")
            return

        # 2. Băm mật khẩu
        hashed_pw = hash_password(password)

        # 3. Kết nối và ghi vào cơ sở dữ liệu
        conn = None
        try:
            conn = get_conn()
            cursor = conn.cursor()

            # Sử dụng câu lệnh SQL có tham số (%s) để tránh lỗi SQL Injection
            # và tự động xử lý các ký tự đặc biệt.
            insert_query = """
                           INSERT INTO users (username, password_hash, role)
                           VALUES (%s, %s, 'Admin') \
                           """

            cursor.execute(insert_query, (username, hashed_pw))

            conn.commit()
            print(f"\n✅ Tạo tài khoản admin '{username}' thành công!")

        except psycopg2.errors.UniqueViolation:
            # Bắt lỗi nếu tên đăng nhập đã tồn tại
            print(f"\n❌ Lỗi: Tên đăng nhập '{username}' đã tồn tại trong hệ thống.")
            if conn:
                conn.rollback()  # Hoàn tác lại bất kỳ thay đổi nào
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi khi tương tác với cơ sở dữ liệu: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    except KeyboardInterrupt:
        print("\nThao tác đã bị hủy bởi người dùng.")


if __name__ == "__main__":
    create_admin_user()