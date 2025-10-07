#!/usr/bin/env node

const { spawn } = require('child_process');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BACKEND_URL = process.env.VITE_API_URL || 'http://localhost:8000';
const TYPES_FILE = path.join(__dirname, '..', 'src', 'types', 'api-schema.ts');

console.log('🚀 Starting development with automatic type generation...');

// Function to check if backend is ready
async function waitForBackend(maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      execSync(`curl -s ${BACKEND_URL}/api/schema/ > nul 2>&1`, { stdio: 'ignore' });
      return true;
    } catch (error) {
      console.log(`⏳ Waiting for backend... (${i + 1}/${maxAttempts})`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  return false;
}

// Function to generate types
function generateTypes() {
  try {
    console.log('🔄 Generating TypeScript types...');
    execSync('npm run generate-types', { stdio: 'inherit' });
    console.log('✅ Types updated successfully');
  } catch (error) {
    console.error('❌ Failed to generate types:', error.message);
  }
}

// Function to watch for schema changes
function watchForSchemaChanges() {
  let lastModified = 0;

  setInterval(async () => {
    try {
      // Check if backend is still available
      execSync(`curl -s ${BACKEND_URL}/api/schema/ > nul 2>&1`, { stdio: 'ignore' });

      // Check if types file exists and get its modification time
      if (fs.existsSync(TYPES_FILE)) {
        const stats = fs.statSync(TYPES_FILE);
        const currentModified = stats.mtime.getTime();

        // Check if it's been more than 30 seconds since last update
        const now = Date.now();
        if (now - lastModified > 30000) {
          // Download current schema and compare with existing
          const tempFile = path.join(__dirname, 'temp-schema.json');
          execSync(`curl -s "${BACKEND_URL}/api/schema/" -o "${tempFile}"`, { stdio: 'ignore' });

          if (fs.existsSync(tempFile)) {
            // Simple check if schema might have changed by comparing file sizes
            const tempStats = fs.statSync(tempFile);
            const existingSize = fs.existsSync(TYPES_FILE) ? fs.statSync(TYPES_FILE).size : 0;

            if (Math.abs(tempStats.size - existingSize) > 100) { // Threshold for changes
              console.log('📡 Backend schema changes detected, regenerating types...');
              generateTypes();
              lastModified = now;
            }

            fs.unlinkSync(tempFile);
          }
        }
      }
    } catch (error) {
      // Backend not available or other error, ignore for now
    }
  }, 10000); // Check every 10 seconds
}

async function main() {
  // Wait for backend to be ready
  const backendReady = await waitForBackend();

  if (!backendReady) {
    console.log('⚠️  Backend not available, starting dev server without type generation');
  } else {
    // Generate initial types
    generateTypes();

    // Start watching for changes
    watchForSchemaChanges();
  }

  // Start the development server
  console.log('🌟 Starting Vite development server...');
  const devServer = spawn('npm', ['run', 'dev'], {
    stdio: 'inherit',
    shell: true
  });

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\n👋 Shutting down...');
    devServer.kill('SIGINT');
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    devServer.kill('SIGTERM');
    process.exit(0);
  });
}

main().catch(console.error);