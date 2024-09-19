import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Grid, Typography, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Facebook, Twitter, LinkedIn, Instagram } from '@material-ui/icons';

// Define styles using Material-UI's makeStyles hook
const useStyles = makeStyles((theme) => ({
  footer: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(6, 0),
  },
  socialIcon: {
    marginRight: theme.spacing(1),
  },
  link: {
    margin: theme.spacing(1, 1.5),
  },
}));

const Footer: React.FC = () => {
  // Get the classes object from useStyles hook
  const classes = useStyles();

  return (
    <footer className={classes.footer}>
      {/* Render Container component with maxWidth prop */}
      <Container maxWidth="lg">
        {/* Render Grid container for footer content */}
        <Grid container spacing={4} justifyContent="space-between">
          {/* Render Grid item for copyright information */}
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="textSecondary" align="center">
              © {new Date().getFullYear()} Boston Startup Tracker
            </Typography>
          </Grid>

          {/* Render Grid item for footer links */}
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="textSecondary" align="center">
              <Link to="/about" className={classes.link}>
                About
              </Link>
              <Link to="/privacy" className={classes.link}>
                Privacy Policy
              </Link>
              <Link to="/terms" className={classes.link}>
                Terms of Service
              </Link>
            </Typography>
          </Grid>

          {/* Render Grid item for social media icons */}
          <Grid item xs={12} sm={4}>
            <Typography variant="body2" color="textSecondary" align="center">
              <IconButton
                aria-label="Facebook"
                color="inherit"
                className={classes.socialIcon}
              >
                <Facebook />
              </IconButton>
              <IconButton
                aria-label="Twitter"
                color="inherit"
                className={classes.socialIcon}
              >
                <Twitter />
              </IconButton>
              <IconButton
                aria-label="LinkedIn"
                color="inherit"
                className={classes.socialIcon}
              >
                <LinkedIn />
              </IconButton>
              <IconButton
                aria-label="Instagram"
                color="inherit"
                className={classes.socialIcon}
              >
                <Instagram />
              </IconButton>
            </Typography>
          </Grid>
        </Grid>
      </Container>
    </footer>
  );
};

export default Footer;

// Human tasks:
// - Implement responsive design for various screen sizes
// - Add hover effects for links and social media icons
// - Implement accessibility features (ARIA labels, keyboard navigation)
// - Add unit tests for the Footer component
// - Implement a newsletter signup form in the footer
// - Add language selection option for multilingual support
// - Implement dynamic copyright year update
// - Add a 'Back to Top' button in the footer