import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Grid, Typography, Paper, Tabs, Tab } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import CompanyOverview from './CompanyOverview';
import TeamSection from './TeamSection';
import FundingHistory from './FundingHistory';
import JobOpenings from './JobOpenings';
import NewsSection from './NewsSection';
import SimilarCompanies from './SimilarCompanies';
import { fetchCompanyProfile } from '../../store/actions/companyActions';
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
  companyHeader: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: theme.spacing(2),
  },
  companyLogo: {
    width: 64,
    height: 64,
    marginRight: theme.spacing(2),
  },
  tabs: {
    marginBottom: theme.spacing(2),
  },
}));

const CompanyProfile: React.FC = () => {
  // Initialize state for active tab
  const [activeTab, setActiveTab] = useState(0);

  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Get the dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // Get the company ID from URL params using useParams
  const { id } = useParams<{ id: string }>();

  // Select company profile data from Redux store using useSelector
  const companyProfile = useSelector((state: RootState) => state.company.profile);

  // Use useEffect to fetch company profile data on component mount or when company ID changes
  useEffect(() => {
    dispatch(fetchCompanyProfile(id));
  }, [dispatch, id]);

  // Define handleTabChange function to update active tab
  const handleTabChange = (event: React.ChangeEvent<{}>, newValue: number) => {
    setActiveTab(newValue);
  };

  // Render the company profile layout using Material-UI Grid
  return (
    <div className={classes.root}>
      <Paper className={classes.paper}>
        {/* Render company name and logo */}
        <div className={classes.companyHeader}>
          <img src={companyProfile?.logo} alt={`${companyProfile?.name} logo`} className={classes.companyLogo} />
          <Typography variant="h4">{companyProfile?.name}</Typography>
        </div>

        {/* Render Tabs component for navigation between sections */}
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
          className={classes.tabs}
        >
          <Tab label="Overview" />
          <Tab label="Team" />
          <Tab label="Funding" />
          <Tab label="Jobs" />
          <Tab label="News" />
          <Tab label="Similar Companies" />
        </Tabs>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            {/* Render CompanyOverview component */}
            {activeTab === 0 && <CompanyOverview company={companyProfile} />}

            {/* Render TeamSection component */}
            {activeTab === 1 && <TeamSection team={companyProfile?.team} />}

            {/* Render FundingHistory component */}
            {activeTab === 2 && <FundingHistory fundingRounds={companyProfile?.fundingRounds} />}

            {/* Render JobOpenings component */}
            {activeTab === 3 && <JobOpenings jobs={companyProfile?.jobOpenings} />}

            {/* Render NewsSection component */}
            {activeTab === 4 && <NewsSection news={companyProfile?.news} />}

            {/* Render SimilarCompanies component */}
            {activeTab === 5 && <SimilarCompanies companies={companyProfile?.similarCompanies} />}
          </Grid>
        </Grid>
      </Paper>
    </div>
  );
};

export default CompanyProfile;

// Human tasks:
// - Implement error handling for failed data fetching
// - Add loading indicators for each section
// - Implement responsive design for mobile devices
// - Add unit tests for the CompanyProfile component
// - Implement accessibility features (ARIA labels, keyboard navigation)
// - Add data visualization for company metrics and funding history
// - Implement a feature to allow users to follow/unfollow companies
// - Add a section for user-generated content (e.g., reviews, comments)