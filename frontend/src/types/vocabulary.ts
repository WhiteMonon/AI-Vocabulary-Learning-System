export enum DifficultyLevel {
    EASY = 'easy',
    MEDIUM = 'medium',
    HARD = 'hard',
}

export enum ReviewQuality {
    AGAIN = 0,
    HARD = 1,
    GOOD = 2,
    EASY = 3,
}

export interface VocabularyReview {
    review_quality: ReviewQuality;
    time_spent_seconds: number;
}

export interface Vocabulary {
    id: number;
    user_id: number;
    word: string;
    definition: string;
    example_sentence: string | null;
    difficulty_level: DifficultyLevel;
    easiness_factor: number;
    interval: number;
    repetitions: number;
    next_review_date: string;
    created_at: string;
    updated_at: string;
}

export interface VocabularyCreate {
    word: string;
    definition: string;
    example_sentence?: string;
    difficulty_level?: DifficultyLevel;
}

export interface VocabularyUpdate {
    word?: string;
    definition?: string;
    example_sentence?: string;
    difficulty_level?: DifficultyLevel;
}

export interface VocabularyListResponse {
    items: Vocabulary[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface VocabularyFilters {
    page?: number;
    page_size?: number;
    difficulty?: DifficultyLevel;
    status?: 'LEARNED' | 'LEARNING' | 'DUE';
    search?: string;
}
