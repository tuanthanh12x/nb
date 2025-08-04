from db.db import get_conn


def init_db():
    """
    Khởi tạo và chuẩn hóa cơ sở dữ liệu.
    Tạo các bảng danh mục và bảng chính với các mối quan-hệ.
    """
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("--- BẮT ĐẦU QUÁ TRÌNH KHỞI TẠO DATABASE ---")

        # --- CÁC BẢNG DANH MỤC (LOOKUP TABLES) ---
        # Đây là các bảng chứa danh sách để người dùng lựa chọn.

        print("1. Đang tạo bảng 'don_vi' (Units)...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS don_vi
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           ten
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           ma_viet_tat TEXT UNIQUE NOT NULL
                       )
                       """)

        print("2. Đang tạo bảng 'lanh_dao' (Leaders)...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS lanh_dao
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           ten
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           chuc_vu
                           TEXT
                       )
                       """)

        print("3. Đang tạo bảng 'loai_van_ban' (Document Types)...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS loai_van_ban
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           ten
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           ma_viet_tat
                           TEXT
                           UNIQUE -- Ví dụ: 'CV' cho 'Công văn'
                       )
                       """)

        print("4. Đang tạo bảng 'do_mat' (Security Levels)...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS do_mat
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           ten
                           TEXT
                           UNIQUE
                           NOT
                           NULL
                       )
                       """)

        print("5. Đang tạo bảng 'noi_nhan' (Recipients)...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS noi_nhan
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           ten
                           TEXT
                           UNIQUE
                           NOT
                           NULL
                       )
                       """)

        # --- CÁC BẢNG CHÍNH ---

        print("6. Đang tạo bảng 'users'...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password_hash
                           TEXT
                           NOT
                           NULL,
                           role
                           TEXT
                           NOT
                           NULL
                           DEFAULT
                           'Guest'
                       )
                       """)

        print("7. Đang tạo bảng 'documents' đã chuẩn hóa...")
        # Bảng này giờ sẽ chứa các 'foreign key' trỏ đến các bảng danh mục
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS documents
                       (
                           id
                           SERIAL
                           PRIMARY
                           KEY,
                           so_van_ban
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           ngay_ban_hanh
                           DATE
                           NOT
                           NULL,
                           trich_yeu
                           TEXT
                           NOT
                           NULL,
                           so_luong_ban
                           INTEGER,
                           trang_thai
                           TEXT
                           NOT
                           NULL
                           DEFAULT
                           'Chờ xác nhận',

                           -- Foreign Keys - Thay thế các trường TEXT cũ
                           loai_so
                           TEXT
                           NOT
                           NULL, -- 'mat' hoặc 'thuong'
                           loai_van_ban_id
                           INTEGER
                           REFERENCES
                           loai_van_ban
                       (
                           id
                       ),
                           do_mat_id INTEGER REFERENCES do_mat
                       (
                           id
                       ),
                           lanh_dao_id INTEGER REFERENCES lanh_dao
                       (
                           id
                       ),
                           don_vi_soan_thao_id INTEGER REFERENCES don_vi
                       (
                           id
                       ),
                           don_vi_luu_tru_id INTEGER REFERENCES don_vi
                       (
                           id
                       ),
                           nguoi_tao_id INTEGER REFERENCES users
                       (
                           id
                       ),

                           ngay_tao_record TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                                                         )
                       """)

        # --- BẢNG LIÊN KẾT (JUNCTION TABLE) CHO QUAN HỆ NHIỀU-NHIỀU ---

        print("8. Đang tạo bảng liên kết 'document_noi_nhan'...")
        # Một văn bản có thể gửi đến NHIỀU nơi nhận
        # Một nơi nhận có thể nhận NHIỀU văn bản
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS document_noi_nhan
                       (
                           document_id
                           INTEGER
                           NOT
                           NULL
                           REFERENCES
                           documents
                       (
                           id
                       ) ON DELETE CASCADE,
                           noi_nhan_id INTEGER NOT NULL REFERENCES noi_nhan
                       (
                           id
                       )
                         ON DELETE CASCADE,
                           PRIMARY KEY
                       (
                           document_id,
                           noi_nhan_id
                       )
                           )
                       """)

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


if __name__ == "__main__":
    init_db()