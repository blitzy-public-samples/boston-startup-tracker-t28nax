// Jest configuration file for the Boston Startup Tracker project

module.exports = {
  // Use ts-jest preset for TypeScript support
  preset: 'ts-jest',

  // Set the test environment to jsdom for browser-like environment
  testEnvironment: 'jsdom',

  // Specify the root directory for tests
  roots: ['<rootDir>/src'],

  // Define file extensions Jest should look for
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  // Configure module name mapping for easier imports
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },

  // Specify setup files to run after Jest is initialized
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],

  // Define patterns to detect test files
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/?(*.)+(spec|test).+(ts|tsx|js)'
  ],

  // Configure TypeScript transformation
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },

  // Specify which files to collect coverage information from
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts'
  ],

  // Set coverage thresholds to enforce minimum coverage
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },

  // Configure coverage report formats
  coverageReporters: ['json', 'lcov', 'text', 'clover']
}

// Human tasks:
// TODO: Review and adjust the coverage thresholds based on project requirements
// TODO: Ensure all necessary file extensions are included in moduleFileExtensions
// TODO: Verify that the moduleNameMapper paths align with your project structure
// TODO: Add any project-specific setup files to setupFilesAfterEnv if needed
// TODO: Consider adding transformIgnorePatterns for any dependencies that should not be transformed
// TODO: Review and update testMatch patterns if you have a different test file naming convention
// TODO: Consider adding testPathIgnorePatterns for any directories that should be excluded from testing
// TODO: Verify that the preset and transform configurations work correctly with your TypeScript setup
// TODO: Consider adding globalSetup and globalTeardown configurations if needed
// TODO: Regularly update Jest and related dependencies to leverage new features and improvements