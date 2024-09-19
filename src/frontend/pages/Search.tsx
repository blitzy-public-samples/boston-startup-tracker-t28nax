import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import SearchInterface from '../components/Search/SearchInterface';
import SearchResults from '../components/Search/SearchResults';
import Pagination from '../components/common/Pagination';
import { searchStartups } from '../../store/actions/searchActions';
import { RootState } from '../../store/types';

// Define styles for the Search component
const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(3),
  },
  title: {
    marginBottom: theme.spacing(3),
  },
}));

const Search: React.FC = () => {
  // Initialize state for search query, filters, and pagination
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Get the dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // Select search results and loading status from Redux store using useSelector
  const { results, totalResults, loading } = useSelector((state: RootState) => state.search);

  // Define handleSearch function to update search query and trigger search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setPage(1); // Reset to first page when new search is performed
  };

  // Define handleFilterChange function to update filters and trigger search
  const handleFilterChange = (newFilters: object) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  };

  // Define handlePageChange function to update pagination and trigger search
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  // Use useEffect to perform search when query, filters, or pagination changes
  useEffect(() => {
    dispatch(searchStartups(searchQuery, filters, page, pageSize));
  }, [dispatch, searchQuery, filters, page, pageSize]);

  return (
    <Container className={classes.root}>
      {/* Render Typography component for page title */}
      <Typography variant="h4" className={classes.title}>
        Search Boston Startups
      </Typography>

      {/* Render SearchInterface component, passing necessary props and handlers */}
      <SearchInterface
        onSearch={handleSearch}
        onFilterChange={handleFilterChange}
        loading={loading}
      />

      {/* Render SearchResults component if results are available */}
      {results && results.length > 0 && (
        <SearchResults results={results} loading={loading} />
      )}

      {/* Render Pagination component if there are multiple pages of results */}
      {totalResults > pageSize && (
        <Pagination
          currentPage={page}
          totalPages={Math.ceil(totalResults / pageSize)}
          onPageChange={handlePageChange}
        />
      )}
    </Container>
  );
};

export default Search;

// Human tasks:
// - Implement responsive design for various screen sizes
// - Add loading indicators for search results
// - Implement error handling for failed search requests
// - Add unit tests for the Search component
// - Implement advanced search options (e.g., date range, specific fields)
// - Add ability to save searches for logged-in users
// - Implement search analytics to track popular search terms
// - Add export functionality for search results