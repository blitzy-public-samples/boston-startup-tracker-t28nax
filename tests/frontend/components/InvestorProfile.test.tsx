import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { MemoryRouter, Route } from 'react-router-dom';
import { InvestorProfile } from '../../../src/frontend/components/InvestorProfile/InvestorProfile';
import { investorReducer } from '../../../src/frontend/store/reducers/investorReducer';
import { fetchInvestorData } from '../../../src/frontend/store/actions/investorActions';

// Mock the fetchInvestorData action
jest.mock('../../../src/frontend/store/actions/investorActions', () => ({
  fetchInvestorData: jest.fn(),
}));

// Create a mock store
const mockStore = configureStore({ reducer: { investor: investorReducer } });

// Helper function to render a component with Redux store and Router
const renderWithReduxAndRouter = (
  component: React.ReactElement,
  initialEntries: string[] = ['/']
) => {
  const store = mockStore;
  const rendered = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={initialEntries}>
        {component}
      </MemoryRouter>
    </Provider>
  );
  return { ...rendered, store };
};

describe('InvestorProfile Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    renderWithReduxAndRouter(<InvestorProfile />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders investor data when loaded', async () => {
    const mockInvestorData = {
      id: '1',
      name: 'John Doe',
      type: 'Angel Investor',
      portfolio: ['Company A', 'Company B'],
      recentInvestments: ['Investment X', 'Investment Y'],
    };

    (fetchInvestorData as jest.Mock).mockResolvedValue(mockInvestorData);

    renderWithReduxAndRouter(<InvestorProfile />);

    await waitFor(() => {
      expect(screen.getByText(mockInvestorData.name)).toBeInTheDocument();
      expect(screen.getByText(mockInvestorData.type)).toBeInTheDocument();
      expect(screen.getByText(/portfolio/i)).toBeInTheDocument();
      expect(screen.getByText(/recent investments/i)).toBeInTheDocument();
    });
  });

  test('handles error state', async () => {
    const errorMessage = 'Failed to fetch investor data';
    (fetchInvestorData as jest.Mock).mockRejectedValue(new Error(errorMessage));

    renderWithReduxAndRouter(<InvestorProfile />);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('fetches investor data with correct ID from URL', async () => {
    const investorId = '123';
    renderWithReduxAndRouter(<Route path="/investor/:id" component={InvestorProfile} />, [`/investor/${investorId}`]);

    await waitFor(() => {
      expect(fetchInvestorData).toHaveBeenCalledWith(investorId);
    });
  });
});