import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Grid, Typography, Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import QuickStats from '../QuickStats/QuickStats';
import RecentUpdates from '../RecentUpdates/RecentUpdates';
import TrendingStartups from '../TrendingStartups/TrendingStartups';
import FeaturedCompanies from '../FeaturedCompanies/FeaturedCompanies';
import LatestNews from '../LatestNews/LatestNews';
import JobOpenings from '../JobOpenings/JobOpenings';
import { fetchDashboardData } from '../../store/actions/dashboardActions';
import { RootState } from '../../store/types';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  title: {
    marginBottom: theme.spacing(2),
  },
}));

const Dashboard: React.FC = () => {
  // Initialize state for loading status
  const [isLoading, setIsLoading] = useState(true);

  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Get the dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // Select dashboard data from Redux store using useSelector
  const dashboardData = useSelector((state: RootState) => state.dashboard);

  // Use useEffect to fetch dashboard data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        await dispatch(fetchDashboardData());
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setIsLoading(false);
      }
    };
    fetchData();
  }, [dispatch]);

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  // Render the dashboard layout using Material-UI Grid
  return (
    <div className={classes.root}>
      <Typography variant="h4" className={classes.title}>
        Boston Startup Tracker Dashboard
      </Typography>
      <Grid container spacing={3}>
        {/* Render QuickStats component */}
        <Grid item xs={12}>
          <Paper className={classes.paper}>
            <QuickStats stats={dashboardData.quickStats} />
          </Paper>
        </Grid>

        {/* Render RecentUpdates component */}
        <Grid item xs={12} md={6}>
          <Paper className={classes.paper}>
            <RecentUpdates updates={dashboardData.recentUpdates} />
          </Paper>
        </Grid>

        {/* Render TrendingStartups component */}
        <Grid item xs={12} md={6}>
          <Paper className={classes.paper}>
            <TrendingStartups startups={dashboardData.trendingStartups} />
          </Paper>
        </Grid>

        {/* Render FeaturedCompanies component */}
        <Grid item xs={12}>
          <Paper className={classes.paper}>
            <FeaturedCompanies companies={dashboardData.featuredCompanies} />
          </Paper>
        </Grid>

        {/* Render LatestNews component */}
        <Grid item xs={12} md={6}>
          <Paper className={classes.paper}>
            <LatestNews news={dashboardData.latestNews} />
          </Paper>
        </Grid>

        {/* Render JobOpenings component */}
        <Grid item xs={12} md={6}>
          <Paper className={classes.paper}>
            <JobOpenings jobs={dashboardData.jobOpenings} />
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard;

// Human tasks:
// - Implement error handling for failed data fetching
// - Add loading indicators for each dashboard section
// - Implement responsive design for mobile devices
// - Add unit tests for the Dashboard component
// - Implement accessibility features (ARIA labels, keyboard navigation)