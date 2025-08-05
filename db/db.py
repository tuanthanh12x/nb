# file: db/db.py
import sqlite3
import os
import bcrypt  # Cần cài đặt: pip install bcrypt

# Tên file CSDL SQLite sẽ được tạo ra trong cùng thư mục
DB_FILE = "vanban_database.sqlite"


def get_conn():
    """
    Tạo và trả về một kết nối đến CSDL SQLite.
    Hàm này chỉ đơn giản là kết nối, không khởi tạo.
    """
    return sqlite3.connect(DB_FILE)


def initialize_database_if_needed():
    """
    Hàm chính để kiểm tra và khởi tạo CSDL.
    Hàm này sẽ được gọi một lần duy nhất khi ứng dụng bắt đầu.
    - Nếu file CSDL chưa tồn tại, nó sẽ tạo file, tạo bảng, và chèn dữ liệu mẫu.
    - Nếu file đã tồn tại, nó sẽ không làm gì cả.
    """
    # 1. KIỂM TRA XEM FILE CSDL ĐÃ TỒN TẠI CHƯA
    if os.path.exists(DB_FILE):
        return  # Nếu có, thoát ngay lập tức

    print(f"--- Database file '{DB_FILE}' not found. Initializing new database... ---")
    conn = None
    try:
        # 2. TẠO KẾT NỐI (Thao tác này sẽ tự động tạo ra file .sqlite rỗng)
        conn = get_conn()
        cursor = conn.cursor()

        # 3. TẠO CẤU TRÚC BẢNG (SCHEMA) - Đã dịch từ PostgreSQL sang SQLite
        # Sự khác biệt chính:
        # - SERIAL PRIMARY KEY -> INTEGER PRIMARY KEY AUTOINCREMENT
        # - TIMESTAMP WITH TIME ZONE -> DATETIME
        sql_schema = """
                     -- Bảng 'don_vi' (Units)
                     CREATE TABLE don_vi \
                     ( \
                         id          INTEGER PRIMARY KEY AUTOINCREMENT, \
                         ten         TEXT NOT NULL UNIQUE, \
                         ma_viet_tat TEXT NOT NULL UNIQUE
                     );

                     -- Bảng 'lanh_dao' (Leaders)
                     CREATE TABLE lanh_dao \
                     ( \
                         id      INTEGER PRIMARY KEY AUTOINCREMENT, \
                         ten     TEXT NOT NULL UNIQUE, \
                         chuc_vu TEXT
                     );

                     -- Bảng 'loai_van_ban' (Document Types)
                     CREATE TABLE loai_van_ban \
                     ( \
                         id          INTEGER PRIMARY KEY AUTOINCREMENT, \
                         ten         TEXT NOT NULL UNIQUE, \
                         ma_viet_tat TEXT UNIQUE
                     );

                     -- Bảng 'do_mat' (Security Levels)
                     CREATE TABLE do_mat \
                     ( \
                         id  INTEGER PRIMARY KEY AUTOINCREMENT, \
                         ten TEXT NOT NULL UNIQUE
                     );

                     -- Bảng 'noi_nhan' (Recipients)
                     CREATE TABLE noi_nhan \
                     ( \
                         id  INTEGER PRIMARY KEY AUTOINCREMENT, \
                         ten TEXT NOT NULL UNIQUE
                     );

                     -- Bảng 'users'
                     CREATE TABLE users \
                     ( \
                         id            INTEGER PRIMARY KEY AUTOINCREMENT, \
                         username      TEXT NOT NULL UNIQUE, \
                         password_hash TEXT NOT NULL, \
                         role          TEXT NOT NULL DEFAULT 'Guest'
                     );

                     -- Bảng chính 'documents'
                     CREATE TABLE documents \
                     ( \
                         id                  INTEGER PRIMARY KEY AUTOINCREMENT, \
                         so_van_ban          TEXT NOT NULL UNIQUE, \
                         ngay_ban_hanh       DATE NOT NULL, \
                         trich_yeu           TEXT NOT NULL, \
                         so_luong_ban        INTEGER, \
                         trang_thai          TEXT NOT NULL DEFAULT 'Chờ xác nhận', \
                         loai_so             TEXT NOT NULL, \
                         loai_van_ban_id     INTEGER REFERENCES loai_van_ban (id), \
                         do_mat_id           INTEGER REFERENCES do_mat (id), \
                         lanh_dao_id         INTEGER REFERENCES lanh_dao (id), \
                         don_vi_soan_thao_id INTEGER REFERENCES don_vi (id), \
                         don_vi_luu_tru_id   INTEGER REFERENCES don_vi (id), \
                         nguoi_tao_id        INTEGER REFERENCES users (id), \
                         ngay_tao_record     DATETIME      DEFAULT CURRENT_TIMESTAMP
                     );

                     -- Bảng liên kết 'document_noi_nhan'
                     CREATE TABLE document_noi_nhan \
                     ( \
                         document_id INTEGER NOT NULL REFERENCES documents (id) ON DELETE CASCADE, \
                         noi_nhan_id INTEGER NOT NULL REFERENCES noi_nhan (id) ON DELETE CASCADE, \
                         PRIMARY KEY (document_id, noi_nhan_id)
                     ); \
                     """
        print("1. Đang tạo cấu trúc các bảng...")
        cursor.executescript(sql_schema)

        # 4. CHÈN DỮ LIỆU MẪU (SAMPLE DATA)
        print("2. Đang chèn dữ liệu mẫu vào các bảng danh mục...")

        # Dữ liệu cho các bảng danh mục
        don_vi_data = [('Phòng Tham mưu', 'PTM'), ('Phòng An ninh', 'PA01'), ('Phòng Cảnh sát', 'PC01'),
                       ('Đội Tổng hợp', 'DTH')]
        lanh_dao_data = [('Đ/c Giám đốc', 'Giám đốc'), ('Đ/c Phó Giám đốc A', 'Phó Giám đốc'),
                         ('Đ/c Phó Giám đốc B', 'Phó Giám đốc')]
        loai_vb_data = [('Báo cáo', 'BC'), ('Công văn', 'CV'), ('Tờ trình', 'TTr'), ('Kế hoạch', 'KH'),
                        ('Quyết định', 'QĐ')]
        do_mat_data = [('Thường',), ('Mật',), ('Tối mật',), ('Tuyệt mật',)]
        noi_nhan_data = [('Công an Tỉnh',), ('Bộ Công an',), ('Các phòng ban liên quan',), ('Lưu: VT',)]

        # Chèn dữ liệu người dùng mẫu
        # Mã hóa mật khẩu trước khi lưu
        admin_pass = b'123456'
        guest_pass = b'guest123'
        hashed_admin_pass = bcrypt.hashpw(admin_pass, bcrypt.gensalt())
        hashed_guest_pass = bcrypt.hashpw(guest_pass, bcrypt.gensalt())
        users_data = [('admin', hashed_admin_pass.decode('utf-8'), 'Admin'),
                      ('guest', hashed_guest_pass.decode('utf-8'), 'Guest')]

        cursor.executemany("INSERT INTO don_vi (ten, ma_viet_tat) VALUES (?, ?)", don_vi_data)
        cursor.executemany("INSERT INTO lanh_dao (ten, chuc_vu) VALUES (?, ?)", lanh_dao_data)
        cursor.executemany("INSERT INTO loai_van_ban (ten, ma_viet_tat) VALUES (?, ?)", loai_vb_data)
        cursor.executemany("INSERT INTO do_mat (ten) VALUES (?)", do_mat_data)
        cursor.executemany("INSERT INTO noi_nhan (ten) VALUES (?)", noi_nhan_data)
        cursor.executemany("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", users_data)

        # Lưu các thay đổi vào file
        conn.commit()
        print("\n--- ✅ QUÁ TRÌNH KHỞI TẠO DATABASE THÀNH CÔNG ---")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi trong quá trình khởi tạo: {e}")
        if conn:
            conn.rollback()
        # Nếu có lỗi, xóa file rỗng đã tạo để có thể thử lại lần sau
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
    finally:
        # Luôn đóng kết nối
        if conn:
            conn.close()
            print("--- Đã đóng kết nối cơ sở dữ liệu ---")


