import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Grid, Typography, Paper, Tabs, Tab } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import InvestorOverview from './InvestorOverview';
import Portfolio from './Portfolio';
import RecentInvestments from './RecentInvestments';
import InvestmentTrends from './InvestmentTrends';
import { fetchInvestorProfile } from '../../store/actions/investorActions';
import { RootState } from '../../store/types';

// Define styles for the component
const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  paper: {
    padding: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  tabs: {
    marginBottom: theme.spacing(2),
  },
}));

const InvestorProfile: React.FC = () => {
  // Initialize state for active tab
  const [activeTab, setActiveTab] = useState(0);

  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Get the dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // Get the investor ID from URL params using useParams
  const { id } = useParams<{ id: string }>();

  // Select investor profile data from Redux store using useSelector
  const investorProfile = useSelector((state: RootState) => state.investor.profile);

  // Use useEffect to fetch investor profile data on component mount or when investor ID changes
  useEffect(() => {
    dispatch(fetchInvestorProfile(id));
  }, [dispatch, id]);

  // Define handleTabChange function to update active tab
  const handleTabChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setActiveTab(newValue);
  };

  // Render the investor profile layout using Material-UI Grid
  return (
    <div className={classes.root}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper className={classes.paper}>
            {/* Render investor name and logo */}
            <Typography variant="h4">{investorProfile?.name}</Typography>
            {/* TODO: Add investor logo */}
          </Paper>
        </Grid>
        <Grid item xs={12}>
          {/* Render Tabs component for navigation between sections */}
          <Paper className={classes.paper}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              centered
              className={classes.tabs}
            >
              <Tab label="Overview" />
              <Tab label="Portfolio" />
              <Tab label="Recent Investments" />
              <Tab label="Investment Trends" />
            </Tabs>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          {/* Render InvestorOverview component */}
          {activeTab === 0 && <InvestorOverview investor={investorProfile} />}
          {/* Render Portfolio component */}
          {activeTab === 1 && <Portfolio investor={investorProfile} />}
          {/* Render RecentInvestments component */}
          {activeTab === 2 && <RecentInvestments investor={investorProfile} />}
          {/* Render InvestmentTrends component */}
          {activeTab === 3 && <InvestmentTrends investor={investorProfile} />}
        </Grid>
      </Grid>
    </div>
  );
};

export default InvestorProfile;

// Human tasks:
// TODO: Implement error handling for failed data fetching
// TODO: Add loading indicators for each section
// TODO: Implement responsive design for mobile devices
// TODO: Add unit tests for the InvestorProfile component
// TODO: Implement accessibility features (ARIA labels, keyboard navigation)
// TODO: Add data visualization for investment trends and portfolio performance
// TODO: Implement a feature to allow users to follow/unfollow investors
// TODO: Add a section for user-generated content (e.g., reviews, comments)
// TODO: Implement a comparison feature to compare multiple investors