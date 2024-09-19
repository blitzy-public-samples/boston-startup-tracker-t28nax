import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Typography, CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import CompanyProfile from '../components/CompanyProfile/CompanyProfile';
import { fetchCompanyData } from '../../store/actions/companyActions';
import { RootState } from '../../store/types';

// Define styles using Material-UI's makeStyles hook
const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(3),
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '50vh',
  },
  error: {
    color: theme.palette.error.main,
    textAlign: 'center',
  },
}));

const Company: React.FC = () => {
  const classes = useStyles();
  const dispatch = useDispatch();
  const { id } = useParams<{ id: string }>();

  // Select company data and loading status from Redux store
  const { companyData, loading, error } = useSelector((state: RootState) => state.company);

  // Fetch company data when component mounts or company ID changes
  useEffect(() => {
    if (id) {
      dispatch(fetchCompanyData(id));
    }
  }, [dispatch, id]);

  return (
    <Container className={classes.root}>
      {loading ? (
        // Display loading indicator while fetching data
        <div className={classes.loading}>
          <CircularProgress />
        </div>
      ) : error ? (
        // Display error message if there was an error fetching data
        <Typography variant="h6" className={classes.error}>
          Error: {error}
        </Typography>
      ) : companyData ? (
        // Render CompanyProfile component if company data is available
        <CompanyProfile company={companyData} />
      ) : (
        // Display message if no company data is available
        <Typography variant="h6">No company data available.</Typography>
      )}
    </Container>
  );
};

export default Company;

// Human tasks:
// TODO: Implement error boundary to catch and display errors gracefully
// TODO: Add breadcrumb navigation for better user orientation
// TODO: Implement responsive design for various screen sizes
// TODO: Add unit tests for the Company component
// TODO: Implement data caching to improve performance for frequently accessed companies
// TODO: Add a feature to allow users to follow/unfollow companies
// TODO: Implement a 'Related Companies' section
// TODO: Add social sharing functionality for company profiles