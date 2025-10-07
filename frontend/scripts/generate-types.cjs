#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BACKEND_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const SCHEMA_URL = `${BACKEND_URL}/api/schema/`;
const OUTPUT_DIR = path.join(__dirname, '..', 'src', 'types', 'api');

console.log('🔄 Generating TypeScript types from OpenAPI schema...');
console.log(`📡 Fetching schema from: ${SCHEMA_URL}`);

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

try {
  // Download the OpenAPI schema
  console.log('📥 Downloading OpenAPI schema...');
  const schemaPath = path.join(OUTPUT_DIR, 'schema.json');

  try {
    execSync(`curl -s "${SCHEMA_URL}" -o "${schemaPath}"`, { stdio: 'inherit' });
  } catch (error) {
    console.error('❌ Failed to download schema. Make sure the backend is running.');
    process.exit(1);
  }

  // Verify schema was downloaded
  if (!fs.existsSync(schemaPath)) {
    console.error('❌ Schema file not found after download');
    process.exit(1);
  }

  // Generate TypeScript types using OpenAPI Generator
  console.log('⚙️  Generating TypeScript types...');

  const generateCommand = `npx @openapitools/openapi-generator-cli generate ` +
    `-i "${schemaPath}" ` +
    `-g typescript-axios ` +
    `-o "${OUTPUT_DIR}" ` +
    `--additional-properties=` +
    `useSingleRequestParameter=true,` +
    `supportsES6=true,` +
    `modelPropertyNaming=camelCase,` +
    `enumPropertyNaming=UPPERCASE`;

  execSync(generateCommand, { stdio: 'inherit' });

  // Clean up temporary schema file
  fs.unlinkSync(schemaPath);

  console.log('✅ TypeScript types generated successfully!');
  console.log(`📁 Output directory: ${OUTPUT_DIR}`);

  // Create index file for easier imports
  const indexContent = `// Auto-generated API types
// Generated on: ${new Date().toISOString()}

export * from './api';
export * from './base';
export * from './common';
export * from './configuration';

// Re-export commonly used types
export type {
  User,
  Account,
  Transaction,
  Category,
  Budget,
  Goal,
} from './api';
`;

  fs.writeFileSync(path.join(OUTPUT_DIR, 'index.ts'), indexContent);
  console.log('📝 Created index.ts for easier imports');

} catch (error) {
  console.error('❌ Error generating types:', error.message);
  process.exit(1);
}