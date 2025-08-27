import sys
import os
import shutil

def is_frozen():
    """Kiểm tra xem có đang chạy từ file exe đóng gói không."""
    return getattr(sys, 'frozen', False)

def get_app_base_path():
    """Trả về đường dẫn bundle (khi chạy exe) hoặc None (khi chạy dev)."""
    if is_frozen():
        return sys._MEIPASS
    return None

def copy_db_from_bundle():
    """Chỉ copy data.db khi chạy từ file exe. Bỏ qua khi chạy dev."""
    base_path = get_app_base_path()

    if base_path is None:
        print("🛠️ Dev mode - Không cần copy data.db")
        return

    try:
        source = os.path.join(base_path, "data.db")
        target = os.path.join(os.getcwd(), "data.db")

        if not os.path.exists(target):
            shutil.copyfile(source, target)
            print("✅ Đã copy data.db từ bundle.")
        else:
            print("ℹ️ data.db đã tồn tại.")
    except Exception as e:
        print(f"❌ Lỗi khi copy data.db: {e}")
