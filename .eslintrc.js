module.exports = {
  // Specify the environments where the code will run
  env: {
    browser: true,
    es2021: true,
    jest: true,
  },
  // Extend from recommended rule sets
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  // Specify the parser for TypeScript
  parser: '@typescript-eslint/parser',
  // Configure parser options
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  // Specify the plugins to use
  plugins: ['react', '@typescript-eslint', 'prettier'],
  // Define custom rules
  rules: {
    'prettier/prettier': 'error',
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    'no-console': 'warn',
  },
  // Configure settings for React
  settings: {
    react: {
      version: 'detect',
    },
  },
};

// Human tasks:
// TODO: Review and adjust the 'rules' section based on project coding standards
// TODO: Consider adding custom rules specific to the project's needs
// TODO: Ensure all necessary plugins are installed and listed in package.json
// TODO: Review the 'extends' array and add or remove configurations as needed
// TODO: Consider adding 'overrides' for specific file patterns if needed
// TODO: Regularly update ESLint and its plugins to leverage new features and rules
// TODO: Ensure the configuration aligns with the TypeScript configuration in tsconfig.json
// TODO: Consider adding rules to enforce consistent import ordering
// TODO: Review and possibly customize the 'env' section based on the project's runtime environment
// TODO: Ensure the configuration works well with the IDE/editor setup of the development team