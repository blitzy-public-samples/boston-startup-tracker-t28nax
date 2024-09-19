import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Typography, CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import InvestorProfile from '../components/InvestorProfile/InvestorProfile';
import { fetchInvestorData } from '../../store/actions/investorActions';
import { RootState } from '../../store/types';

// Define styles using Material-UI's makeStyles hook
const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '50vh',
  },
  errorMessage: {
    color: theme.palette.error.main,
    textAlign: 'center',
  },
}));

const Investor: React.FC = () => {
  const classes = useStyles();
  const dispatch = useDispatch();
  const { id } = useParams<{ id: string }>();

  // Select investor data and loading status from Redux store
  const { investor, loading, error } = useSelector((state: RootState) => state.investor);

  // Fetch investor data when component mounts or investor ID changes
  useEffect(() => {
    if (id) {
      dispatch(fetchInvestorData(id));
    }
  }, [dispatch, id]);

  // Render loading indicator while fetching data
  if (loading) {
    return (
      <Container className={classes.loadingContainer}>
        <CircularProgress />
      </Container>
    );
  }

  // Display error message if there was an error fetching data
  if (error) {
    return (
      <Container className={classes.container}>
        <Typography variant="h6" className={classes.errorMessage}>
          Error: {error}
        </Typography>
      </Container>
    );
  }

  // Render InvestorProfile component if investor data is available
  return (
    <Container className={classes.container}>
      {investor ? (
        <InvestorProfile investor={investor} />
      ) : (
        <Typography variant="h6">No investor data available</Typography>
      )}
    </Container>
  );
};

export default Investor;

// Human tasks:
// - Implement error boundary to catch and display errors gracefully
// - Add breadcrumb navigation for better user orientation
// - Implement responsive design for various screen sizes
// - Add unit tests for the Investor component
// - Implement data caching to improve performance for frequently accessed investors
// - Add a feature to allow users to follow/unfollow investors
// - Implement a 'Similar Investors' section
// - Add social sharing functionality for investor profiles