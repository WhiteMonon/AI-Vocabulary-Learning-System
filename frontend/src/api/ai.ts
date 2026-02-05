import { AIChatRequest } from '../types/ai';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Gửi yêu cầu chat đến AI và stream kết quả.
 * @param request AIChatRequest
 * @param onChunk Callback được gọi khi có một chunk mới từ stream
 * @returns Promise<void>
 */
export const streamAIChat = async (
    request: AIChatRequest,
    onChunk: (chunk: string) => void
): Promise<void> => {
    const token = localStorage.getItem('token');

    const response = await fetch(`${API_URL}/api/v1/ai-practice/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Lỗi khi kết nối với AI');
    }

    if (!response.body) {
        throw new Error('ReadableStream không khả dụng');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
    }
};
