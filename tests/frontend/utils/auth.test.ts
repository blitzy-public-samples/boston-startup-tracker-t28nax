import jwt_decode from 'jwt-decode';
import {
  setAuthToken,
  getAuthToken,
  removeAuthToken,
  isAuthenticated,
  decodeToken,
  getUserId
} from '../../../src/frontend/utils/auth';

// Mock localStorage
const localStorageMock = {
  setItem: jest.fn(),
  getItem: jest.fn(),
  removeItem: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock jwt_decode
jest.mock('jwt-decode');

describe('Authentication Utility Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('setAuthToken stores token in localStorage', () => {
    const testToken = 'test-token';
    setAuthToken(testToken);
    expect(localStorage.setItem).toHaveBeenCalledWith('authToken', testToken);
  });

  test('getAuthToken retrieves token from localStorage', () => {
    const testToken = 'test-token';
    localStorage.getItem.mockReturnValue(testToken);
    const result = getAuthToken();
    expect(result).toBe(testToken);
  });

  test('removeAuthToken removes token from localStorage', () => {
    removeAuthToken();
    expect(localStorage.removeItem).toHaveBeenCalledWith('authToken');
  });

  test('isAuthenticated returns true when token exists', () => {
    localStorage.getItem.mockReturnValue('valid-token');
    const result = isAuthenticated();
    expect(result).toBe(true);
  });

  test("isAuthenticated returns false when token doesn't exist", () => {
    localStorage.getItem.mockReturnValue(null);
    const result = isAuthenticated();
    expect(result).toBe(false);
  });

  test('decodeToken returns decoded token payload', () => {
    const testToken = 'test-token';
    const testPayload = { sub: '123', name: 'John Doe' };
    localStorage.getItem.mockReturnValue(testToken);
    (jwt_decode as jest.Mock).mockReturnValue(testPayload);

    const result = decodeToken();
    expect(result).toEqual(testPayload);
    expect(jwt_decode).toHaveBeenCalledWith(testToken);
  });

  test('getUserId returns user ID from token', () => {
    const testUserId = '123';
    const testPayload = { sub: testUserId };
    (jwt_decode as jest.Mock).mockReturnValue(testPayload);

    const result = getUserId();
    expect(result).toBe(testUserId);
  });
});