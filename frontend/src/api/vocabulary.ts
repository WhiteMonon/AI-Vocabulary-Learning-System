import apiClient from './client';
import {
    Vocabulary,
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyListResponse,
    VocabularyFilters,
    VocabularyReview,
    QuizSessionResponse,
    QuizSubmit
} from '../types/vocabulary';

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
