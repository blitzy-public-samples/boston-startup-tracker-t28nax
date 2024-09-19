// Base URL for the API
export const API_BASE_URL = '/api/v1';

// Maximum number of results to return per page
export const MAX_RESULTS_PER_PAGE = 50;

// Default number of results to return per page
export const DEFAULT_RESULTS_PER_PAGE = 20;

// Array of possible funding stages
export const FUNDING_STAGES = [
  'SEED',
  'SERIES_A',
  'SERIES_B',
  'SERIES_C',
  'SERIES_D',
  'SERIES_E',
  'GROWTH',
  'IPO'
];

// Array of possible investor types
export const INVESTOR_TYPES = [
  'VENTURE_CAPITAL',
  'ANGEL',
  'PRIVATE_EQUITY',
  'CORPORATE',
  'ACCELERATOR',
  'INCUBATOR'
];

// Array of possible job departments
export const JOB_DEPARTMENTS = [
  'ENGINEERING',
  'PRODUCT',
  'DESIGN',
  'MARKETING',
  'SALES',
  'CUSTOMER_SUCCESS',
  'OPERATIONS',
  'FINANCE',
  'HR',
  'LEGAL'
];

// Standard date format for the application
export const DATE_FORMAT = 'YYYY-MM-DD';

// Default currency for financial amounts
export const CURRENCY = 'USD';

// Token expiration time in seconds
export const TOKEN_EXPIRATION = 3600;