import axios, { AxiosInstance } from 'axios';
import { getAuthToken } from './auth';

// Base URL for the Boston Startup Tracker API
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

// Create and configure an Axios instance for API requests
const createAxiosInstance = (): AxiosInstance => {
  // Create a new Axios instance with API_BASE_URL as the base URL
  const instance = axios.create({
    baseURL: API_BASE_URL,
  });

  // Set up request interceptor to add authorization header with token
  instance.interceptors.request.use(
    (config) => {
      const token = getAuthToken();
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Set up response interceptor to handle common error scenarios
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response) {
        // Handle specific HTTP error codes here if needed
        switch (error.response.status) {
          case 401:
            // Handle unauthorized access
            break;
          case 404:
            // Handle not found
            break;
          // Add more cases as needed
        }
      }
      return Promise.reject(error);
    }
  );

  return instance;
};

// Create an Axios instance to be used for all API calls
const axiosInstance = createAxiosInstance();

// Performs a GET request to the specified endpoint
export const get = async (endpoint: string, params?: object): Promise<any> => {
  const response = await axiosInstance.get(endpoint, { params });
  return response.data;
};

// Performs a POST request to the specified endpoint
export const post = async (endpoint: string, data: object): Promise<any> => {
  const response = await axiosInstance.post(endpoint, data);
  return response.data;
};

// Performs a PUT request to the specified endpoint
export const put = async (endpoint: string, data: object): Promise<any> => {
  const response = await axiosInstance.put(endpoint, data);
  return response.data;
};

// Performs a DELETE request to the specified endpoint
export const delete = async (endpoint: string): Promise<any> => {
  const response = await axiosInstance.delete(endpoint);
  return response.data;
};