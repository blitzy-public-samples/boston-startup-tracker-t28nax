import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardMedia, Typography, Button } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Company } from '../../types/Company';

// Define styles using Material-UI's makeStyles hook
const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: 345,
    margin: theme.spacing(2),
  },
  media: {
    height: 140,
  },
  content: {
    height: 200,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
  },
  button: {
    marginTop: theme.spacing(2),
  },
}));

interface CompanyCardProps {
  company: Company;
}

const CompanyCard: React.FC<CompanyCardProps> = ({ company }) => {
  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Destructure company data from props
  const { id, name, industry, location, fundingAmount, logoUrl } = company;

  return (
    // Render Card component as the main container
    <Card className={classes.root}>
      {/* Render CardMedia component for company logo */}
      <CardMedia
        className={classes.media}
        image={logoUrl}
        title={`${name} logo`}
      />
      {/* Render CardContent component for company information */}
      <CardContent className={classes.content}>
        {/* Display company name using Typography component */}
        <Typography gutterBottom variant="h5" component="h2">
          {name}
        </Typography>
        {/* Display company industry using Typography component */}
        <Typography variant="body2" color="textSecondary" component="p">
          Industry: {industry}
        </Typography>
        {/* Display company location using Typography component */}
        <Typography variant="body2" color="textSecondary" component="p">
          Location: {location}
        </Typography>
        {/* Display company funding information using Typography component */}
        <Typography variant="body2" color="textSecondary" component="p">
          Funding: ${fundingAmount.toLocaleString()}
        </Typography>
        {/* Render 'View Profile' button using Button component wrapped in Link */}
        <Link to={`/company/${id}`} style={{ textDecoration: 'none' }}>
          <Button
            variant="contained"
            color="primary"
            className={classes.button}
            fullWidth
          >
            View Profile
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
};

export default CompanyCard;

// Human tasks:
// TODO: Implement responsive design for various screen sizes
// TODO: Add hover effects for better user interaction
// TODO: Implement lazy loading for company logos
// TODO: Add unit tests for the CompanyCard component
// TODO: Implement a feature to save/bookmark companies
// TODO: Add a tooltip with more company information on hover
// TODO: Implement accessibility features (ARIA labels, keyboard navigation)
// TODO: Add support for different card layouts or sizes