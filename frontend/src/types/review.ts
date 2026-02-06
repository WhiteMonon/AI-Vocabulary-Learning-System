// Review System Types
export enum QuestionType {
    // Function word types
    FILL_BLANK = 'fill_blank',
    MULTIPLE_CHOICE = 'multiple_choice',

    // Content word types
    WORD_FROM_MEANING = 'word_from_meaning',
    MEANING_FROM_WORD = 'meaning_from_word',
    DICTATION = 'dictation',
    SYNONYM_ANTONYM_MCQ = 'synonym_antonym_mcq',
    DEFINITION_MCQ = 'definition_mcq',

    // Legacy
    MEANING_INPUT = 'meaning_input',
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
    audio_url?: string;
    word?: string; // For MEANING_FROM_WORD display
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
