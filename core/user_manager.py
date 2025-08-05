import bcrypt  # Sử dụng bcrypt thay vì hashlib
from db.db import get_conn  # Dùng file db.py đã tạo từ trước


# Hàm hash_password không còn cần thiết vì logic sẽ được tích hợp trực tiếp.

def add_user(username, password, role):
    """
    Thêm người dùng mới vào CSDL SQLite với mật khẩu được mã hóa bằng bcrypt.
    """
    # 1. Mã hóa mật khẩu bằng bcrypt
    # - password.encode('utf-8'): Chuyển chuỗi mật khẩu thành bytes
    # - bcrypt.gensalt(): Tạo ra một "salt" ngẫu nhiên
    # - bcrypt.hashpw(...): Băm mật khẩu với salt
    # - .decode('utf-8'): Chuyển kết quả bytes trở lại chuỗi để lưu vào CSDL
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    sql_check = "SELECT id FROM users WHERE username = ?"
    sql_insert = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"

    try:
        # Sử dụng 'with' để đảm bảo kết nối được đóng tự động
        with get_conn() as conn:
            cursor = conn.cursor()

            # Kiểm tra người dùng đã tồn tại chưa (dùng placeholder '?')
            cursor.execute(sql_check, (username,))
            if cursor.fetchone():
                return False, "Tên người dùng đã tồn tại"

            # Thêm người dùng mới
            cursor.execute(sql_insert, (username, hashed_pw, role))
            conn.commit()
            return True, "Thêm người dùng thành công"

    except Exception as e:
        return False, f"Lỗi khi thêm người dùng: {e}"


def delete_user(username):
    """Xóa người dùng khỏi CSDL bằng tên đăng nhập."""
    sql = "DELETE FROM users WHERE username = ?"
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (username,))
            conn.commit()
        return True, "Xóa người dùng thành công."
    except Exception as e:
        return False, f"Lỗi khi xóa người dùng: {e}"


def validate_user(username, password):
    """
    Xác thực thông tin đăng nhập của người dùng.
    So sánh mật khẩu người dùng nhập với hash đã lưu trong CSDL bằng bcrypt.
    """
    sql = "SELECT password_hash, role FROM users WHERE username = ?"
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (username,))
            result = cursor.fetchone()

            if not result:
                return False, None  # Người dùng không tồn tại

            stored_hash = result[0]
            role = result[1]

            # 2. So sánh mật khẩu bằng bcrypt.checkpw
            # - Nó sẽ tự động lấy salt từ stored_hash để so sánh
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return True, role  # Mật khẩu chính xác, trả về vai trò
            else:
                return False, None  # Sai mật khẩu

    except Exception as e:
        print(f"Lỗi khi xác thực người dùng: {e}")
        return False, None


def get_all_users():
    """
    Lấy danh sách tất cả người dùng (id, username, role).
    Hàm này đã tương thích, không cần sửa đổi nhiều.
    """
    users_list = []
    sql = "SELECT id, username, role FROM users ORDER BY username"
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            users_data = cursor.fetchall()
            for u_id, u_name, u_role in users_data:
                users_list.append({"id": u_id, "username": u_name, "role": u_role})
    except Exception as e:
        print(f"Lỗi khi lấy danh sách người dùng: {e}")
    return users_list


def update_user_password(user_id, new_password):
    """Cập nhật mật khẩu mới cho người dùng theo ID."""
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    sql = "UPDATE users SET password_hash = ? WHERE id = ?"
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (hashed_pw, user_id))
            conn.commit()
        return True, "Cập nhật mật khẩu thành công."
    except Exception as e:
        return False, f"Lỗi khi cập nhật mật khẩu: {e}"

