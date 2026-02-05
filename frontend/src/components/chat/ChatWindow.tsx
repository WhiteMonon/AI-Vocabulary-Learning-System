import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage as ChatMessageType } from '../../types/ai';
import ChatMessage from './ChatMessage';

interface ChatWindowProps {
    messages: ChatMessageType[];
    isLoading: boolean;
    onSendMessage: (content: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading, onSendMessage }) => {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            onSendMessage(input.trim());
            setInput('');
        }
    };

    return (
        <div className="flex flex-col h-[700px] bg-white rounded-3xl overflow-hidden border border-gray-100 shadow-2xl relative">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 md:px-0 bg-white">
                <div className="max-w-3xl mx-auto py-8">
                    {messages.length === 0 ? (
                        <div className="h-[400px] flex flex-col items-center justify-center text-center space-y-6 animate-in fade-in duration-700">
                            <div className="w-20 h-20 bg-indigo-600 rounded-2xl flex items-center justify-center text-3xl shadow-lg shadow-indigo-100 transform -rotate-6">
                                🤖
                            </div>
                            <div className="space-y-2">
                                <h4 className="text-2xl font-bold text-gray-800">Cùng luyện tập nào!</h4>
                                <p className="text-gray-500 max-w-sm mx-auto">
                                    Tôi là AI Teacher, luôn sẵn sàng giúp bạn làm chủ từ vựng thông qua những cuộc hội thoại thú vị.
                                </p>
                            </div>
                            <div className="flex flex-wrap gap-2 justify-center pt-4">
                                {['Chào bạn!', 'Giải thích từ "procrastinate"', 'Đặt câu với "resilient"'].map(hint => (
                                    <button
                                        key={hint}
                                        onClick={() => onSendMessage(hint)}
                                        className="px-4 py-2 bg-gray-50 text-gray-600 rounded-full text-xs font-medium border border-gray-100 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-100 transition-all"
                                    >
                                        {hint}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}
                        </div>
                    )}
                    {isLoading && !messages[messages.length - 1]?.content && (
                        <div className="flex justify-start mb-8 pl-11">
                            <div className="flex space-x-2">
                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area - Floats and wider at bottom */}
            <div className="p-6 bg-gradient-to-t from-white via-white/90 to-transparent">
                <form
                    onSubmit={handleSubmit}
                    className="max-w-3xl mx-auto"
                >
                    <div className="relative flex items-center bg-white border border-gray-200 rounded-2xl p-1.5 pl-4 shadow-sm focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-50 transition-all duration-300">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Hỏi AI về từ vựng..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-gray-800 py-3 text-sm"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className={`p-3 rounded-xl transition-all duration-300 ${!input.trim() || isLoading
                                    ? 'bg-gray-50 text-gray-300'
                                    : 'bg-indigo-600 text-white shadow-lg shadow-indigo-100 hover:bg-indigo-700 active:scale-95'
                                }`}
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                                />
                            </svg>
                        </button>
                    </div>
                    <p className="text-[10px] text-center text-gray-400 mt-3">
                        Hệ thống AI có thể tạo ra thông tin không chính xác. Hãy kiểm tra lại nếu cần thiết.
                    </p>
                </form>
            </div>
        </div>
    );
};

export default ChatWindow;
