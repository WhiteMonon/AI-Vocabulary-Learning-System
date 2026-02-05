import apiClient from './client';
import {
    Vocabulary,
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyListResponse,
    VocabularyFilters
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
