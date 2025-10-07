#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BACKEND_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const SCHEMA_URL = `${BACKEND_URL}/api/schema/`;
const OUTPUT_DIR = path.join(__dirname, '..', 'src', 'types');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'api-schema.ts');

console.log('🔄 Generating TypeScript types from OpenAPI schema...');
console.log(`📡 Fetching schema from: ${SCHEMA_URL}`);

async function generateTypes() {
  try {
    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    console.log('⚙️  Generating TypeScript types with openapi-typescript...');

    // Use openapi-typescript to generate types directly from URL
    const command = `npx openapi-typescript "${SCHEMA_URL}" --output "${OUTPUT_FILE}"`;

    execSync(command, {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });

    console.log('✅ TypeScript types generated successfully!');
    console.log(`📁 Output file: ${OUTPUT_FILE}`);

    // Create helper types file
    const helperContent = `// Auto-generated API helper types
// Generated on: ${new Date().toISOString()}

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
`;

    const helperFile = path.join(OUTPUT_DIR, 'api-types.ts');
    fs.writeFileSync(helperFile, helperContent);
    console.log('📝 Created api-types.ts with helper types');

  } catch (error) {
    console.error('❌ Error generating types:', error.message);
    process.exit(1);
  }
}

generateTypes();