import { authClient } from './client';
import type { LoginCredentials, LoginResponse } from '../types/auth';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    // Send as JSON, not form data
    const response = await authClient.post<LoginResponse>('/api/auth/login', {
      email: credentials.username, // maxplatform expects 'email' field
      password: credentials.password,
    });
    return response.data;
  },
};