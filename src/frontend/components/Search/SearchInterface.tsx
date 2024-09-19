import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Grid, TextField, Button, Typography, Paper, CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import SearchFilters from './SearchFilters';
import SearchResults from './SearchResults';
import Pagination from '../common/Pagination';
import { searchStartups } from '../../store/actions/searchActions';
import { RootState } from '../../store/types';

// Define styles for the SearchInterface component
const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(3),
  },
  searchBar: {
    marginBottom: theme.spacing(3),
  },
  loadingSpinner: {
    display: 'flex',
    justifyContent: 'center',
    marginTop: theme.spacing(3),
  },
}));

const SearchInterface: React.FC = () => {
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
  const { results, loading, totalResults } = useSelector((state: RootState) => state.search);

  // Define handleSearch function to trigger search action
  const handleSearch = () => {
    dispatch(searchStartups(searchQuery, filters, page, pageSize));
  };

  // Define handleFilterChange function to update filters
  const handleFilterChange = (newFilters: object) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  };

  // Define handlePageChange function to update pagination
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  // Use useEffect to perform search when query, filters, or pagination changes
  useEffect(() => {
    handleSearch();
  }, [searchQuery, filters, page, pageSize]);

  return (
    <Paper className={classes.root}>
      <Grid container spacing={3}>
        {/* Render search input field and search button */}
        <Grid item xs={12} className={classes.searchBar}>
          <TextField
            fullWidth
            variant="outlined"
            label="Search startups"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button variant="contained" color="primary" onClick={handleSearch}>
            Search
          </Button>
        </Grid>

        {/* Render SearchFilters component */}
        <Grid item xs={12} md={3}>
          <SearchFilters onFilterChange={handleFilterChange} />
        </Grid>

        {/* Render SearchResults component */}
        <Grid item xs={12} md={9}>
          {loading ? (
            <div className={classes.loadingSpinner}>
              <CircularProgress />
            </div>
          ) : (
            <>
              <Typography variant="h6">
                {totalResults} results found
              </Typography>
              <SearchResults results={results} />
            </>
          )}
        </Grid>

        {/* Render Pagination component */}
        <Grid item xs={12}>
          <Pagination
            totalItems={totalResults}
            itemsPerPage={pageSize}
            currentPage={page}
            onPageChange={handlePageChange}
          />
        </Grid>
      </Grid>
    </Paper>
  );
};

export default SearchInterface;

// Human tasks:
// TODO: Implement debounce for search input to reduce API calls
// TODO: Add error handling for failed search requests
// TODO: Implement advanced search options (e.g., date range, specific fields)
// TODO: Add unit tests for the SearchInterface component
// TODO: Implement keyboard shortcuts for search and navigation
// TODO: Optimize performance for large result sets
// TODO: Implement search history and saved searches functionality