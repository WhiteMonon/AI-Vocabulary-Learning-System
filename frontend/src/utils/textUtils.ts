/**
 * Loại bỏ các khối suy nghĩ của AI (nằm trong thẻ <think>...</think>) từ văn bản.
 * Xử lý cả thẻ đóng đầy đủ và thẻ không đóng (unclosed tags).
 * Logic này cần được đồng bộ với hàm strip_reasoning trong backend/app/ai/utils.py
 * 
 * @param text Văn bản đầu vào
 * @returns Văn bản đã được làm sạch
 */
export const stripThinkTags = (text: string): string => {
    if (!text) return '';

    // Bước 1: Loại bỏ cặp thẻ <think>...</think> đầy đủ
    // Sử dụng [\s\S] để match cả ký tự xuống dòng (dotAll equivalent)
    let cleaned = text.replace(/<think>[\s\S]*?<\/think>/g, '');

    // Bước 2: Loại bỏ thẻ <think> không đóng (unclosed)
    // Nếu còn <think> mà không có </think>, xóa từ <think> đến cuối chuỗi
    cleaned = cleaned.replace(/<think>[\s\S]*$/g, '');

    return cleaned.trim();
};
