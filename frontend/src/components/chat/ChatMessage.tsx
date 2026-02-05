import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage as ChatMessageType } from '../../types/ai';

interface ChatMessageProps {
    message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
    const isAI = message.role === 'assistant';

    // Filter out <think> blocks for a cleaner display
    const displayContent = message.content.replace(/<think>[\s\S]*?<\/think>/g, '').trim();

    // Extract and potentially show thinking in a subtle way (optional, but requested to fix "ugly text")
    const isThinking = message.content.includes('<think>') && !message.content.includes('</think>');

    if (!displayContent && !isThinking) return null;

    return (
        <div className={`flex w-full mb-8 ${isAI ? 'justify-start' : 'justify-end'}`}>
            <div className={`flex max-w-[85%] md:max-w-[75%] ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm shadow-sm ${isAI ? 'bg-indigo-600 text-white mr-3' : 'bg-gray-200 text-gray-600 ml-3'
                    }`}>
                    {isAI ? 'AI' : 'U'}
                </div>

                {/* Message Bubble */}
                <div className="flex flex-col">
                    <div
                        className={`rounded-2xl px-5 py-3 ${isAI
                                ? 'bg-transparent text-gray-800'
                                : 'bg-indigo-600 text-white shadow-md shadow-indigo-100'
                            }`}
                    >
                        <div className={`prose prose-sm max-w-none ${isAI ? 'text-gray-800' : 'text-white'}`}>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {displayContent}
                            </ReactMarkdown>
                        </div>

                        {isThinking && isAI && (
                            <div className="mt-2 flex items-center space-x-1 text-gray-400 italic text-xs">
                                <div className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-pulse"></div>
                                <span>AI đang suy nghĩ...</span>
                            </div>
                        )}
                    </div>

                    <div className={`mt-1 text-[10px] text-gray-400 px-2 ${!isAI ? 'text-right' : ''}`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
