import apiClient from './client';

export interface UserOut {
    id: number;
    email: string;
    username: string;
    full_name: string | null;
    is_active: boolean;
}

export interface Token {
    access_token: string;
    token_type: string;
}

export const loginApi = async (formData: FormData): Promise<Token> => {
    const params = new URLSearchParams();
    formData.forEach((value, key) => {
        params.append(key, value as string);
    });

    const { data } = await apiClient.post<Token>('/api/v1/auth/login', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });
    return data;
};

export const registerApi = async (userData: any): Promise<UserOut> => {
    const { data } = await apiClient.post<UserOut>('/api/v1/auth/register', userData);
    return data;
};

export const getMeApi = async (): Promise<UserOut> => {
    const { data } = await apiClient.get<UserOut>('/api/v1/auth/me');
    return data;
};
