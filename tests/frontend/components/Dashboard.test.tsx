import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import Dashboard from '../../../src/frontend/components/Dashboard/Dashboard';
import dashboardReducer from '../../../src/frontend/store/reducers/dashboardReducer';
import { fetchDashboardData } from '../../../src/frontend/store/actions/dashboardActions';

// Mock the fetchDashboardData action
jest.mock('../../../src/frontend/store/actions/dashboardActions', () => ({
  fetchDashboardData: jest.fn(),
}));

// Create a mock store
const mockStore = configureStore({ reducer: { dashboard: dashboardReducer } });

// Helper function to render a component with Redux store
const renderWithRedux = (component: React.ReactElement) => {
  const store = mockStore;
  const rendered = render(
    <Provider store={store}>
      {component}
    </Provider>
  );
  return { ...rendered, store };
};

describe('Dashboard Component', () => {
  test('renders loading state initially', () => {
    renderWithRedux(<Dashboard />);
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });

  test('renders dashboard data when loaded', async () => {
    // Create mock dashboard data
    const mockDashboardData = {
      quickStats: { /* mock quick stats data */ },
      recentUpdates: [ /* mock recent updates data */ ],
      trendingStartups: [ /* mock trending startups data */ ],
      featuredCompanies: [ /* mock featured companies data */ ],
    };

    // Dispatch fetchDashboardData action with mock data
    (fetchDashboardData as jest.Mock).mockResolvedValue(mockDashboardData);

    renderWithRedux(<Dashboard />);

    // Wait for dashboard elements to be present
    await waitFor(() => {
      expect(screen.getByTestId('quick-stats')).toBeInTheDocument();
      expect(screen.getByTestId('recent-updates')).toBeInTheDocument();
      expect(screen.getByTestId('trending-startups')).toBeInTheDocument();
      expect(screen.getByTestId('featured-companies')).toBeInTheDocument();
    });
  });

  test('handles error state', async () => {
    // Dispatch fetchDashboardData action with error
    (fetchDashboardData as jest.Mock).mockRejectedValue(new Error('Failed to fetch dashboard data'));

    renderWithRedux(<Dashboard />);

    // Wait for error message to be present
    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch dashboard data')).toBeInTheDocument();
    });
  });
});