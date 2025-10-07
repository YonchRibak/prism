// Auto-generated API helper types
// Generated on: 2025-10-07T14:21:28.076Z

import type { paths, components } from './api-schema';

// Extract schema types
export type ApiSchema = components['schemas'];

// Extract specific model types
export type User = ApiSchema['User'];
export type Account = ApiSchema['Account'];
export type Transaction = ApiSchema['Transaction'];
export type Category = ApiSchema['Category'];
export type Budget = ApiSchema['Budget'];
export type Goal = ApiSchema['Goal'];

// Auth types
export type LoginRequest = ApiSchema['LoginRequest'];
export type RegisterRequest = ApiSchema['RegisterRequest'];
export type TokenRefresh = ApiSchema['TokenRefresh'];

// Extract API path types
export type ApiPaths = paths;

// Helper type for extracting response types
export type ApiResponse<T extends keyof ApiPaths, M extends keyof ApiPaths[T]> =
  ApiPaths[T][M] extends { responses: { 200: { content: { 'application/json': infer R } } } }
    ? R
    : never;

// Helper type for extracting request body types
export type ApiRequestBody<T extends keyof ApiPaths, M extends keyof ApiPaths[T]> =
  ApiPaths[T][M] extends { requestBody: { content: { 'application/json': infer R } } }
    ? R
    : never;

// Common API response wrapper types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: any;
}

// Re-export everything from api-schema
export * from './api-schema';
