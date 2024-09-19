import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import SearchInterface from '../../../src/frontend/components/Search/SearchInterface';
import searchReducer from '../../../src/frontend/store/reducers/searchReducer';
import { searchStartups } from '../../../src/frontend/store/actions/searchActions';

// Mock the searchStartups action
jest.mock('../../../src/frontend/store/actions/searchActions', () => ({
  searchStartups: jest.fn(),
}));

// Create a mock store
const mockStore = configureStore({ reducer: { search: searchReducer } });

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

describe('SearchInterface Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders search input and button', () => {
    renderWithRedux(<SearchInterface />);
    
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
  });

  test('performs search on button click', async () => {
    const { store } = renderWithRedux(<SearchInterface />);
    
    const searchInput = screen.getByRole('textbox');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(searchInput, { target: { value: 'test query' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(searchStartups).toHaveBeenCalledWith('test query', expect.any(Object));
    });
  });

  test('displays search results', async () => {
    const mockResults = [
      { id: 1, name: 'Startup 1' },
      { id: 2, name: 'Startup 2' },
    ];

    (searchStartups as jest.Mock).mockImplementation(() => ({
      type: 'SEARCH_STARTUPS_SUCCESS',
      payload: mockResults,
    }));

    const { store } = renderWithRedux(<SearchInterface />);
    store.dispatch(searchStartups('test', {}));

    await waitFor(() => {
      expect(screen.getByText('Startup 1')).toBeInTheDocument();
      expect(screen.getByText('Startup 2')).toBeInTheDocument();
      expect(screen.getAllByTestId('startup-result-item')).toHaveLength(2);
    });
  });

  test('handles empty search results', async () => {
    (searchStartups as jest.Mock).mockImplementation(() => ({
      type: 'SEARCH_STARTUPS_SUCCESS',
      payload: [],
    }));

    const { store } = renderWithRedux(<SearchInterface />);
    store.dispatch(searchStartups('test', {}));

    await waitFor(() => {
      expect(screen.getByText(/no results found/i)).toBeInTheDocument();
    });
  });

  test('updates results on filter change', async () => {
    const { store } = renderWithRedux(<SearchInterface />);
    
    const filterSelect = screen.getByLabelText(/filter by/i);
    fireEvent.change(filterSelect, { target: { value: 'funding' } });

    await waitFor(() => {
      expect(searchStartups).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({
        filter: 'funding',
      }));
    });
  });
});