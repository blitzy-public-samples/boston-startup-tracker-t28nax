import axios, { AxiosResponse } from 'axios';
import { get, post, put, delete as apiDelete } from '../../../src/frontend/utils/api';
import { getAuthToken } from '../../../src/frontend/utils/auth';

// Mock axios methods
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock getAuthToken
jest.mock('../../../src/frontend/utils/auth');
const mockedGetAuthToken = getAuthToken as jest.MockedFunction<typeof getAuthToken>;

describe('API Utility Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('get function makes a GET request with correct parameters', async () => {
    // Mock axios.get to return a successful response
    const mockResponse: AxiosResponse = {
      data: { message: 'Success' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };
    mockedAxios.get.mockResolvedValue(mockResponse);

    // Call the get function with a test endpoint and params
    const endpoint = '/test';
    const params = { id: 1 };
    const result = await get(endpoint, params);

    // Assert that axios.get was called with correct arguments
    expect(mockedAxios.get).toHaveBeenCalledWith(endpoint, { params });

    // Assert that the function returns the expected data
    expect(result).toEqual(mockResponse.data);
  });

  test('post function makes a POST request with correct parameters', async () => {
    // Mock axios.post to return a successful response
    const mockResponse: AxiosResponse = {
      data: { message: 'Created' },
      status: 201,
      statusText: 'Created',
      headers: {},
      config: {},
    };
    mockedAxios.post.mockResolvedValue(mockResponse);

    // Call the post function with a test endpoint and data
    const endpoint = '/test';
    const data = { name: 'Test' };
    const result = await post(endpoint, data);

    // Assert that axios.post was called with correct arguments
    expect(mockedAxios.post).toHaveBeenCalledWith(endpoint, data);

    // Assert that the function returns the expected data
    expect(result).toEqual(mockResponse.data);
  });

  test('put function makes a PUT request with correct parameters', async () => {
    // Mock axios.put to return a successful response
    const mockResponse: AxiosResponse = {
      data: { message: 'Updated' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };
    mockedAxios.put.mockResolvedValue(mockResponse);

    // Call the put function with a test endpoint and data
    const endpoint = '/test/1';
    const data = { name: 'Updated Test' };
    const result = await put(endpoint, data);

    // Assert that axios.put was called with correct arguments
    expect(mockedAxios.put).toHaveBeenCalledWith(endpoint, data);

    // Assert that the function returns the expected data
    expect(result).toEqual(mockResponse.data);
  });

  test('delete function makes a DELETE request with correct parameters', async () => {
    // Mock axios.delete to return a successful response
    const mockResponse: AxiosResponse = {
      data: { message: 'Deleted' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };
    mockedAxios.delete.mockResolvedValue(mockResponse);

    // Call the delete function with a test endpoint
    const endpoint = '/test/1';
    const result = await apiDelete(endpoint);

    // Assert that axios.delete was called with correct arguments
    expect(mockedAxios.delete).toHaveBeenCalledWith(endpoint);

    // Assert that the function returns the expected data
    expect(result).toEqual(mockResponse.data);
  });

  test('API calls include authentication token in headers', async () => {
    // Mock getAuthToken to return a test token
    const testToken = 'test-auth-token';
    mockedGetAuthToken.mockReturnValue(testToken);

    // Mock axios.get to return a successful response
    const mockResponse: AxiosResponse = {
      data: { message: 'Success' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };
    mockedAxios.get.mockResolvedValue(mockResponse);

    // Call the get function with a test endpoint
    const endpoint = '/test';
    await get(endpoint);

    // Assert that axios.get was called with the auth token in headers
    expect(mockedAxios.get).toHaveBeenCalledWith(endpoint, {
      headers: { Authorization: `Bearer ${testToken}` },
    });
  });

  test('API calls handle errors correctly', async () => {
    // Mock axios.get to throw an error
    const mockError = new Error('Network Error');
    mockedAxios.get.mockRejectedValue(mockError);

    // Call the get function with a test endpoint
    const endpoint = '/test';

    // Assert that the function throws an error
    await expect(get(endpoint)).rejects.toThrow('Network Error');
  });
});