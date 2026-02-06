import apiClient from './client';
import {
    ReviewSessionCreate,
    ReviewSessionResponse,
    BatchSubmitRequest,
    BatchSubmitResponse,
} from '../types/review';

/**
 * Tạo review session mới
 */
export const createReviewSession = async (
    sessionData: ReviewSessionCreate = {}
): Promise<ReviewSessionResponse> => {
    const { data } = await apiClient.post<ReviewSessionResponse>(
        '/api/v1/reviews/sessions',
        sessionData
    );
    return data;
};

/**
 * Lấy thông tin review session
 */
export const getReviewSession = async (sessionId: number): Promise<ReviewSessionResponse> => {
    const { data } = await apiClient.get<ReviewSessionResponse>(
        `/api/v1/reviews/sessions/${sessionId}`
    );
    return data;
};

/**
 * Submit batch answers cho review session
 */
export const submitReviewAnswers = async (
    sessionId: number,
    submitData: BatchSubmitRequest
): Promise<BatchSubmitResponse> => {
    const { data } = await apiClient.post<BatchSubmitResponse>(
        `/api/v1/reviews/sessions/${sessionId}/submit`,
        submitData
    );
    return data;
};
