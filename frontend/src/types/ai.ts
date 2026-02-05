export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
    id: string;
    role: MessageRole;
    content: string;
    timestamp: Date;
}

export interface AIChatRequest {
    messages: Array<{
        role: MessageRole;
        content: string;
    }>;
    vocab_id?: string;
    practice_type?: string;
}

export interface ChatState {
    messages: ChatMessage[];
    isLoading: boolean;
    error: string | null;
}
