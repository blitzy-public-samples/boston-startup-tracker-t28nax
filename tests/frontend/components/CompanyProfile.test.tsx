import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { MemoryRouter, Route } from 'react-router-dom';
import { CompanyProfile } from '../../../src/frontend/components/CompanyProfile/CompanyProfile';
import { companyReducer } from '../../../src/frontend/store/reducers/companyReducer';
import { fetchCompanyData } from '../../../src/frontend/store/actions/companyActions';

// Mock the fetchCompanyData action
jest.mock('../../../src/frontend/store/actions/companyActions', () => ({
  fetchCompanyData: jest.fn(),
}));

// Create a mock store
const mockStore = configureStore({ reducer: { company: companyReducer } });

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

describe('CompanyProfile Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    renderWithReduxAndRouter(<CompanyProfile />);
    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
  });

  test('renders company data when loaded', async () => {
    const mockCompanyData = {
      id: '1',
      name: 'Test Company',
      description: 'A test company description',
      funding: '$1M',
      team: [{ name: 'John Doe', role: 'CEO' }],
    };

    (fetchCompanyData as jest.Mock).mockResolvedValue(mockCompanyData);

    renderWithReduxAndRouter(<CompanyProfile />);

    await waitFor(() => {
      expect(screen.getByText('Test Company')).toBeInTheDocument();
      expect(screen.getByText('A test company description')).toBeInTheDocument();
      expect(screen.getByText('$1M')).toBeInTheDocument();
      expect(screen.getByText('Team')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('CEO')).toBeInTheDocument();
    });
  });

  test('handles error state', async () => {
    (fetchCompanyData as jest.Mock).mockRejectedValue(new Error('Failed to fetch company data'));

    renderWithReduxAndRouter(<CompanyProfile />);

    await waitFor(() => {
      expect(screen.getByText(/Error: Failed to fetch company data/i)).toBeInTheDocument();
    });
  });

  test('fetches company data with correct ID from URL', async () => {
    renderWithReduxAndRouter(
      <Route path="/company/:id" element={<CompanyProfile />} />,
      ['/company/123']
    );

    await waitFor(() => {
      expect(fetchCompanyData).toHaveBeenCalledWith('123');
    });
  });
});