#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const codegen = require('swagger-typescript-codegen').CodeGen;

const BACKEND_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const SCHEMA_URL = `${BACKEND_URL}/api/schema/`;
const OUTPUT_DIR = path.join(__dirname, '..', 'src', 'types');

console.log('🔄 Generating TypeScript types using swagger-typescript-codegen...');
console.log(`📡 Fetching schema from: ${SCHEMA_URL}`);

async function generateTypes() {
  try {
    // Ensure output directory exists
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Download the OpenAPI schema
    console.log('📥 Downloading OpenAPI schema...');
    const schemaPath = path.join(OUTPUT_DIR, 'temp-schema.json');

    try {
      execSync(`curl -s "${SCHEMA_URL}" -o "${schemaPath}"`, { stdio: 'inherit' });
    } catch (error) {
      console.error('❌ Failed to download schema. Make sure the backend is running.');
      process.exit(1);
    }

    // Read and parse the schema
    const schemaContent = fs.readFileSync(schemaPath, 'utf8');
    let swagger;

    try {
      swagger = JSON.parse(schemaContent);
    } catch (error) {
      // Try YAML parsing if JSON fails
      const yaml = require('js-yaml');
      swagger = yaml.load(schemaContent);
    }

    // Generate TypeScript code
    console.log('⚙️  Generating TypeScript types...');

    const tsCode = codegen.getTypescriptCode({
      swagger: swagger,
      moduleName: 'PrismAPI',
      className: 'PrismAPIClient',
      imports: ['import axios, { AxiosResponse, AxiosInstance } from "axios";'],
      beautify: true,
      camelCase: true,
    });

    // Write the generated code
    const outputPath = path.join(OUTPUT_DIR, 'generated-api.ts');
    fs.writeFileSync(outputPath, tsCode);

    // Clean up temporary schema file
    fs.unlinkSync(schemaPath);

    console.log('✅ TypeScript types generated successfully!');
    console.log(`📁 Output file: ${outputPath}`);

    // Create index file for easier imports
    const indexContent = `// Auto-generated API types
// Generated on: ${new Date().toISOString()}
// Using swagger-typescript-codegen

export * from './generated-api';

// Type aliases for easier access
import { PrismAPI } from './generated-api';

export type User = PrismAPI.User;
export type Account = PrismAPI.Account;
export type Transaction = PrismAPI.Transaction;
export type Category = PrismAPI.Category;
export type Budget = PrismAPI.Budget;
export type Goal = PrismAPI.Goal;

export type LoginRequest = PrismAPI.LoginRequest;
export type RegisterRequest = PrismAPI.RegisterRequest;
export type AuthTokens = PrismAPI.AuthTokens;

export type APIClient = PrismAPI.PrismAPIClient;
`;

    fs.writeFileSync(path.join(OUTPUT_DIR, 'api-types.ts'), indexContent);
    console.log('📝 Created api-types.ts for easier imports');

  } catch (error) {
    console.error('❌ Error generating types:', error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Check if js-yaml is available for YAML parsing
try {
  require('js-yaml');
} catch (error) {
  console.log('📦 Installing js-yaml for YAML support...');
  execSync('npm install --save-dev js-yaml', { stdio: 'inherit' });
}

generateTypes();