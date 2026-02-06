export enum WordType {
    FUNCTION_WORD = 'function_word',
    CONTENT_WORD = 'content_word'
}

export enum ApplicationType {
    WEB = 'web',
    MOBILE = 'mobile',
    EXTENSION = 'extension',
    Desktop = 'desktop' // Legacy support if needed
}

export enum ReviewQuality {
    AGAIN = 0,
    HARD = 1,
    GOOD = 2,
    EASY = 3,
}

export interface Meaning {
    id: number;
    definition: string;
    example_sentence: string | null;
    meaning_source: string; // 'manual', 'ai', 'dictionary'
    is_auto_generated: boolean;
    created_at: string;
    updated_at: string;
}

export interface MeaningCreate {
    definition: string;
    example_sentence?: string;
}

export interface Vocabulary {
    id: number;
    user_id: number;
    word: string;
    word_type: WordType;
    is_word_type_manual: boolean;
    meanings: Meaning[];

    // SRS fields
    easiness_factor: number;
    interval: number;
    repetitions: number;
    next_review_date: string;

    // Timestamps
    created_at: string;
    updated_at: string;
}

export interface VocabularyCreate {
    word: string;
    word_type?: WordType;
    meanings: MeaningCreate[];
}

export interface VocabularyFilters {
    page?: number;
    page_size?: number;
    search?: string;
    word_type?: WordType;
    status?: 'LEARNED' | 'LEARNING' | 'DUE';
}

export interface VocabularyUpdate {
    word?: string;
    word_type?: WordType;
    meanings?: MeaningCreate[];
}

export interface VocabularyReview {
    review_quality: ReviewQuality;
    time_spent_seconds: number;
}

export interface VocabularyListResponse {
    items: Vocabulary[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface VocabularyStats {
    total_vocabularies: number;
    due_today: number;
    learned: number;
    learning: number;
    by_word_type: Record<string, number>;
}

export interface QuizQuestion {
    id: number;
    word: string;
    question_text: string;
    options: Record<string, string>;
    correct_answer: string;
    explanation: string;
    grammar_explanation?: string;
}

export interface QuizSessionResponse {
    questions: QuizQuestion[];
}

export interface QuizSubmit {
    vocabulary_id: number;
    is_correct: boolean;
    time_spent_seconds: number;
}

// Import/Export Types
export interface ImportResultResponse {
    total_processed: number;
    new_words: number;
    merged_meanings: number;
    auto_generated_count: number;
    failed_auto_meaning: string[];
    warnings: string[];
    errors: string[];
}

export interface VocabularyImportRequest {
    content: string;
    auto_fetch_meaning: boolean;
}
