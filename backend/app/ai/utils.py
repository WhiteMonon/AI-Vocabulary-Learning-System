import re

def strip_reasoning(text: str) -> str:
    """
    Loại bỏ các khối suy nghĩ của AI (nằm trong thẻ <think>...</think>) từ văn bản.
    Xử lý cả thẻ đóng đầy đủ và thẻ không đóng (unclosed tags).
    
    Args:
        text: Văn bản cần xử lý
        
    Returns:
        Văn bản đã được lọc sạch
    """
    if not text:
        return ""
    
    # Bước 1: Loại bỏ cặp thẻ <think>...</think> đầy đủ
    # Sử dụng re.DOTALL để khớp với cả xuống dòng
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text)
    
    # Bước 2: Loại bỏ thẻ <think> không đóng (unclosed)
    # Nếu còn <think> mà không có </think>, xóa từ <think> đến cuối chuỗi
    cleaned = re.sub(r'<think>[\s\S]*$', '', cleaned)
    
    # Xóa khoảng trắng thừa ở đầu và cuối
    return cleaned.strip()
