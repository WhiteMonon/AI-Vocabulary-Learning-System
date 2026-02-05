import React, { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatWindow from '../components/chat/ChatWindow';
import { ChatMessage, ChatState } from '../types/ai';
import { streamAIChat } from '../api/ai';

const AIPractice: React.FC = () => {
    const [chatState, setChatState] = useState<ChatState>({
        messages: [],
        isLoading: false,
        error: null,
    });

    const handleSendMessage = useCallback(async (content: string) => {
        // 1. Add user message
        const userMessage: ChatMessage = {
            id: uuidv4(),
            role: 'user',
            content,
            timestamp: new Date(),
        };

        setChatState((prev) => ({
            ...prev,
            messages: [...prev.messages, userMessage],
            isLoading: true,
            error: null,
        }));

        // 2. Prepare for AI response
        const assistantId = uuidv4();
        const assistantMessage: ChatMessage = {
            id: assistantId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
        };

        setChatState((prev) => ({
            ...prev,
            messages: [...prev.messages, assistantMessage],
        }));

        try {
            const messagesForAI = [...chatState.messages, userMessage].map((m) => ({
                role: m.role,
                content: m.content,
            }));

            await streamAIChat(
                { messages: messagesForAI },
                (chunk) => {
                    setChatState((prev) => {
                        const newMessages = prev.messages.map((m) => {
                            if (m.id === assistantId) {
                                return { ...m, content: m.content + chunk };
                            }
                            return m;
                        });
                        return { ...prev, messages: newMessages };
                    });
                }
            );
        } catch (err: any) {
            setChatState((prev) => ({
                ...prev,
                error: err.message || 'Có lỗi xảy ra khi kết nối với AI',
            }));
        } finally {
            setChatState((prev) => ({ ...prev, isLoading: false }));
        }
    }, [chatState.messages]);

    const handleRetry = () => {
        // Basic retry: re-send the last user message
        const lastUserMsg = [...chatState.messages].reverse().find(m => m.role === 'user');
        if (lastUserMsg) {
            // Remove the failed assistant message if it exists
            setChatState(prev => {
                const filteredMessages = prev.messages.filter(m => m.id !== prev.messages[prev.messages.length - 1].id || m.role !== 'assistant');
                return { ...prev, messages: filteredMessages };
            });
            handleSendMessage(lastUserMsg.content);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-8 px-4">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Luyện tập cùng AI</h1>
                <p className="text-gray-600 mt-2">
                    Thảo luận về các từ vựng bạn đã học để ghi nhớ lâu hơn.
                </p>
            </div>

            {chatState.error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-red-700">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm font-medium">{chatState.error}</span>
                    </div>
                    <button
                        onClick={handleRetry}
                        className="text-sm font-semibold text-red-700 hover:text-red-800 underline"
                    >
                        Thử lại
                    </button>
                </div>
            )}

            <ChatWindow
                messages={chatState.messages}
                isLoading={chatState.isLoading}
                onSendMessage={handleSendMessage}
            />

            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100">
                    <h4 className="font-bold text-indigo-900 mb-1">Mẹo nhỏ 💡</h4>
                    <p className="text-xs text-indigo-700 leading-relaxed">
                        Bạn có thể yêu cầu AI giải thích nghĩa của từ, đặt câu ví dụ hoặc sửa lỗi ngữ pháp.
                    </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-xl border border-purple-100">
                    <h4 className="font-bold text-purple-900 mb-1">Thách thức 🎯</h4>
                    <p className="text-xs text-purple-700 leading-relaxed">
                        Hãy cố gắng sử dụng ít nhất 3 từ vựng mới trong mỗi câu trả lời của bạn.
                    </p>
                </div>
                <div className="p-4 bg-green-50 rounded-xl border border-green-100">
                    <h4 className="font-bold text-green-900 mb-1">Tự do 🚀</h4>
                    <p className="text-xs text-green-700 leading-relaxed">
                        Đừng quá lo lắng về lỗi, quan trọng nhất là việc thực hành hội thoại tự nhiên.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AIPractice;
