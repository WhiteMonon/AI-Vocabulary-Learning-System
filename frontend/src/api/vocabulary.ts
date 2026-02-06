import apiClient from './client';
import {
    Vocabulary,
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyListResponse,
    VocabularyReview,
    QuizSessionResponse,
    QuizSubmit,
    VocabularyImportRequest,
    ImportResultResponse,
    WordType
} from '../types/vocabulary';

export interface VocabularyFilters {
    page?: number;
    page_size?: number;
    word_type?: WordType;
    status?: 'LEARNED' | 'LEARNING' | 'DUE';
    search?: string;
}

export const getVocabularies = async (filters: VocabularyFilters = {}): Promise<VocabularyListResponse> => {
    const { data } = await apiClient.get<VocabularyListResponse>('/api/v1/vocabulary/', {
        params: filters,
    });
    return data;
};

export const getVocabulary = async (id: number): Promise<Vocabulary> => {
    const { data } = await apiClient.get<Vocabulary>(`/api/v1/vocabulary/${id}`);
    return data;
};

export const createVocabulary = async (vocab: VocabularyCreate): Promise<Vocabulary> => {
    const { data } = await apiClient.post<Vocabulary>('/api/v1/vocabulary/', vocab);
    return data;
};

export const updateVocabulary = async (id: number, vocab: VocabularyUpdate): Promise<Vocabulary> => {
    const { data } = await apiClient.patch<Vocabulary>(`/api/v1/vocabulary/${id}`, vocab);
    return data;
};

export const deleteVocabulary = async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/vocabulary/${id}`);
};

export const reviewVocabulary = async (id: number, review: VocabularyReview): Promise<Vocabulary> => {
    const { data } = await apiClient.post<Vocabulary>(`/api/v1/vocabulary/${id}/review`, review);
    return data;
};

export const getQuizSession = async (limit: number = 10): Promise<QuizSessionResponse> => {
    const { data } = await apiClient.get<QuizSessionResponse>('/api/v1/vocabulary/quiz-session', {
        params: { limit },
    });
    return data;
};

export const submitQuizAnswer = async (submit: QuizSubmit): Promise<Vocabulary> => {
    const { data } = await apiClient.post<Vocabulary>('/api/v1/vocabulary/quiz-submit-single', submit);
    return data;
};

export const importVocabulary = async (data: VocabularyImportRequest): Promise<ImportResultResponse> => {
    const response = await apiClient.post<ImportResultResponse>('/api/v1/vocabulary/import', data);
    return response.data;
};

export const exportVocabulary = async (format: 'json' | 'txt' | 'csv'): Promise<Blob> => {
    const response = await apiClient.get('/api/v1/vocabulary/export', {
        params: { format },
        responseType: 'blob',
    });
    return response.data;
};
