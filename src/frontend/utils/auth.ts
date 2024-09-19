import jwtDecode from 'jwt-decode';

// Constant key for storing the authentication token in local storage
const TOKEN_KEY = 'boston_startup_tracker_auth_token';

/**
 * Stores the authentication token in local storage
 * @param token The authentication token to store
 */
export function setAuthToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Retrieves the authentication token from local storage
 * @returns The stored token or null if not found
 */
export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Removes the authentication token from local storage
 */
export function removeAuthToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Checks if the user is currently authenticated
 * @returns True if authenticated, false otherwise
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  return !!token;
}

/**
 * Decodes the JWT token to extract user information
 * @returns Decoded token payload or null if no token
 */
export function decodeToken(): object | null {
  const token = getAuthToken();
  if (token) {
    try {
      return jwtDecode(token);
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }
  return null;
}

/**
 * Extracts the user ID from the decoded JWT token
 * @returns User ID or null if not authenticated
 */
export function getUserId(): string | null {
  const decodedToken = decodeToken();
  if (decodedToken && 'userId' in decodedToken) {
    return (decodedToken as { userId: string }).userId;
  }
  return null;
}