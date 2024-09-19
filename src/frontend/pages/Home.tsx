import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Grid, Typography, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import Dashboard from '../components/Dashboard/Dashboard';
import FeaturedStartups from '../components/FeaturedStartups/FeaturedStartups';
import RecentNews from '../components/RecentNews/RecentNews';
import StatisticsOverview from '../components/StatisticsOverview/StatisticsOverview';
import { fetchHomePageData } from '../../store/actions/homeActions';
import { RootState } from '../../store/types';

// Define styles using Material-UI's makeStyles hook
const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  hero: {
    marginBottom: theme.spacing(4),
    textAlign: 'center',
  },
  heroButtons: {
    marginTop: theme.spacing(4),
  },
  section: {
    marginBottom: theme.spacing(4),
  },
}));

const Home: React.FC = () => {
  // Initialize state for loading status
  const [isLoading, setIsLoading] = useState(true);

  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Get the dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // Select home page data from Redux store using useSelector
  const homeData = useSelector((state: RootState) => state.home);

  // Use useEffect to fetch home page data on component mount
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      await dispatch(fetchHomePageData());
      setIsLoading(false);
    };
    fetchData();
  }, [dispatch]);

  return (
    // Render Container component as the main wrapper
    <Container className={classes.root}>
      {/* Render hero section with welcome message and call-to-action buttons */}
      <div className={classes.hero}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to Boston Startup Tracker
        </Typography>
        <Typography variant="h5" color="textSecondary" paragraph>
          Discover, track, and connect with the most innovative startups in Boston's thriving ecosystem.
        </Typography>
        <div className={classes.heroButtons}>
          <Grid container spacing={2} justifyContent="center">
            <Grid item>
              <Button variant="contained" color="primary" component={Link} to="/startups">
                Explore Startups
              </Button>
            </Grid>
            <Grid item>
              <Button variant="outlined" color="primary" component={Link} to="/about">
                Learn More
              </Button>
            </Grid>
          </Grid>
        </div>
      </div>

      {/* Render Dashboard component */}
      <div className={classes.section}>
        <Dashboard />
      </div>

      {/* Render FeaturedStartups component */}
      <div className={classes.section}>
        <FeaturedStartups startups={homeData.featuredStartups} isLoading={isLoading} />
      </div>

      {/* Render RecentNews component */}
      <div className={classes.section}>
        <RecentNews news={homeData.recentNews} isLoading={isLoading} />
      </div>

      {/* Render StatisticsOverview component */}
      <div className={classes.section}>
        <StatisticsOverview statistics={homeData.statistics} isLoading={isLoading} />
      </div>
    </Container>
  );
};

export default Home;

// Human tasks:
// - Implement responsive design for various screen sizes
// - Add animations for component transitions and data loading
// - Implement error handling for failed data fetching
// - Add unit tests for the Home component
// - Implement lazy loading for components to improve initial load time
// - Add a newsletter signup form in the hero section
// - Implement a dynamic background or hero image
// - Add user testimonials or success stories section