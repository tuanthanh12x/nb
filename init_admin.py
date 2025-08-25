import hashlib

from db.db import get_conn


def init_dbx():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("--- BẮT ĐẦU QUÁ TRÌNH KHỞI TẠO DATABASE ---")

        # ... phần tạo bảng y như bạn đã có ...

        conn.commit()

        conn.commit()
        print("✅ Tạo bảng xong.")

        # ====== THÊM DỮ LIỆU MẶC ĐỊNH ======
        print("➡️ Đang thêm dữ liệu mặc định...")

        # Loại văn bản
        loai_van_ban_list = [
            ("Báo cáo", "BC"),
            ("Công văn", "CV"),
            ("Kế hoạch", "KH"),
            ("Tờ trình", "TTr"),
            ("Thông báo", "TB"),
            ("Phương án", "PA"),
            ("Hướng dẫn", "HD"),
            ("Quyết định", "QD"),
            ("Giấy mời", "GM"),
            ("Phiếu chuyển", "PC"),
        ]
        for ten, ma in loai_van_ban_list:
            cursor.execute("""
                           INSERT INTO loai_van_ban (ten, ma_viet_tat)
                           VALUES (%s, %s) ON CONFLICT (ten) DO NOTHING
                           """, (ten, ma))

        # Độ mật
        for ten in ["Mật", "Tối mật", "Tuyệt mật"]:
            cursor.execute("""
                           INSERT INTO do_mat (ten)
                           VALUES (%s) ON CONFLICT (ten) DO NOTHING
                           """, (ten,))

        # Lãnh đạo ký
        for ten in ["Nguyễn Tiến Thắng", "Ngô Xuân Hải", "Nguyễn Chí Cường", "Nguyễn Đức Tuấn", "Hoàng Cao Toàn"]:
            cursor.execute("""
                           INSERT INTO lanh_dao (ten)
                           VALUES (%s) ON CONFLICT (ten) DO NOTHING
                           """, (ten,))

        # Đơn vị soạn thảo / lưu trữ
        don_vi_list = [("Đ1", "Đ1"), ("Đ2", "Đ2"), ("Đ3", "Đ3"), ("Đ4", "Đ4"), ("Đ5", "Đ5"), ("Đ6", "Đ6")]
        for ten, ma in don_vi_list:
            cursor.execute("""
                           INSERT INTO don_vi (ten, ma_viet_tat)
                           VALUES (%s, %s) ON CONFLICT (ten) DO NOTHING
                           """, (ten, ma))
        noi_nhan_list = [
            "Đ1",
            "Đ2",
            "Đ3",
            "Đ4",
            "Đ5",
            "Đ6"
        ]
        for ten in noi_nhan_list:
            cursor.execute("""
                           INSERT INTO noi_nhan (ten)
                           VALUES (%s) ON CONFLICT (ten) DO NOTHING
                           """, (ten,))
        password_plain = "123456"
        password_hash = hashlib.sha256(password_plain.encode("utf-8")).hexdigest()

        cursor.execute("SELECT id FROM users WHERE username = %s", ("admin",))
        existing = cursor.fetchone()

        if not existing:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                """,
                ("admin", password_hash, "Admin"),
            )
            print("✅ Đã thêm user admin (username=admin, pass=123456)")
        else:
            print("ℹ️ User admin đã tồn tại, bỏ qua.")

        conn.commit()

        print("\n--- ✅ QUÁ TRÌNH KHỞI TẠO DATABASE THÀNH CÔNG ---")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("--- Đã đóng kết nối cơ sở dữ liệu ---")