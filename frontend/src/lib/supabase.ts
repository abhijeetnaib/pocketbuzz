import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// API helper
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
        ...options,
    });

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch (e) {
            errorData = { detail: response.statusText };
        }
        const message = errorData.detail || response.statusText;
        throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
    }

    return response.json();
}

// Campaign API
export const campaignApi = {
    get: (id: string) => apiRequest<Campaign>(`/api/campaigns/${id}`),
    approve: (id: string, data?: CampaignApproval) =>
        apiRequest(`/api/campaigns/${id}/approve`, {
            method: 'POST',
            body: JSON.stringify(data || {}),
        }),
    send: (id: string) =>
        apiRequest(`/api/campaigns/${id}/send`, { method: 'POST' }),
    reject: (id: string) =>
        apiRequest(`/api/campaigns/${id}/reject`, { method: 'POST' }),
    regenerateImage: (id: string, manualPrompt?: string) =>
        apiRequest<{ image_url: string }>(`/api/campaigns/${id}/regenerate-image`, {
            method: 'POST',
            body: JSON.stringify({ manual_prompt: manualPrompt })
        }),
    create: (data: any) =>
        apiRequest<Campaign>('/api/campaigns/', {
            method: 'POST',
            body: JSON.stringify(data)
        }),
    getSuggestions: (restaurantId: string) =>
        apiRequest<any[]>(`/api/campaigns/suggestions?restaurant_id=${restaurantId}`, { method: 'GET' }),
};

// Auth API
export const authApi = {
    verify: (token: string) => apiRequest<AuthResponse>(`/api/auth/verify/${token}`),
    getRestaurant: (token: string) =>
        apiRequest<Restaurant>(`/api/auth/restaurant/${token}`),
};

// Types
export interface Campaign {
    id: string;
    restaurant_id: string;
    strategy_type: 'BEST_SELLER' | 'DEAD_STOCK' | 'CHURN_RECOVERY' | 'SLOW_DAY' | 'CUSTOM';
    insight_text: string;
    generated_image_url: string;
    generated_caption: string;
    status: 'PENDING' | 'APPROVED' | 'SENT' | 'FAILED';
    created_at: string;
}

export interface CampaignApproval {
    modified_caption?: string;
    modified_image_url?: string;
}

export interface AuthResponse {
    authenticated: boolean;
    restaurant_id: string;
    restaurant_name: string;
}

export interface Restaurant {
    id: string;
    name: string;
}
