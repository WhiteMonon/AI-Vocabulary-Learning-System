// Review System Types
export enum QuestionType {
    MEANING_INPUT = 'meaning_input',
    FILL_BLANK = 'fill_blank',
    MULTIPLE_CHOICE = 'multiple_choice',
    ERROR_DETECTION = 'error_detection',
}

export enum QuestionDifficulty {
    EASY = 'easy',
    MEDIUM = 'medium',
    HARD = 'hard',
}

export interface QuestionResponse {
    question_instance_id: string;
    vocabulary_id: number;
    question_type: QuestionType;
    difficulty: QuestionDifficulty;
    question_text: string;
    options?: string[];
    context_sentence?: string;
    confusion_pair_group?: string;
}

export interface QuestionSubmission {
    question_instance_id: string;
    user_answer: string;
    time_spent_ms: number;
    answer_change_count: number;
}

export interface ReviewSessionCreate {
    mode?: string; // 'due' | 'new'
    max_questions?: number;
}

export interface ReviewSessionResponse {
    session_id: number;
    status: string;
    total_questions: number;
    questions: QuestionResponse[];
    started_at: string;
}

export interface BatchSubmitRequest {
    submissions: QuestionSubmission[];
}

export interface SubmitResponse {
    question_instance_id: string;
    is_correct: boolean;
    correct_answer: string;
    explanation?: string;
}

export interface BatchSubmitResponse {
    results: SubmitResponse[];
    session_summary: {
        session_id: number;
        total_questions: number;
        correct_count: number;
        accuracy: number;
        total_time_seconds: number;
        completed_at: string;
    };
}
