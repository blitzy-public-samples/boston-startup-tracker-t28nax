import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { AppBar, Toolbar, Typography, Button, IconButton, Menu, MenuItem } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Menu as MenuIcon, AccountCircle } from '@material-ui/icons';
import { logout } from '../../store/actions/authActions';
import { RootState } from '../../store/types';

// Define styles using Material-UI's makeStyles hook
const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
  link: {
    color: 'inherit',
    textDecoration: 'none',
  },
}));

const Header: React.FC = () => {
  // Initialize state for mobile menu and user menu anchors
  const [mobileAnchorEl, setMobileAnchorEl] = useState<null | HTMLElement>(null);
  const [userAnchorEl, setUserAnchorEl] = useState<null | HTMLElement>(null);

  // Get the classes object from useStyles hook
  const classes = useStyles();

  // Get the dispatch function from useDispatch hook
  const dispatch = useDispatch();

  // Select user authentication status from Redux store using useSelector
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  // Define handleMobileMenuOpen function to open mobile menu
  const handleMobileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMobileAnchorEl(event.currentTarget);
  };

  // Define handleMobileMenuClose function to close mobile menu
  const handleMobileMenuClose = () => {
    setMobileAnchorEl(null);
  };

  // Define handleUserMenuOpen function to open user menu
  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserAnchorEl(event.currentTarget);
  };

  // Define handleUserMenuClose function to close user menu
  const handleUserMenuClose = () => {
    setUserAnchorEl(null);
  };

  // Define handleLogout function to dispatch logout action
  const handleLogout = () => {
    dispatch(logout());
    handleUserMenuClose();
  };

  return (
    <div className={classes.root}>
      <AppBar position="static">
        <Toolbar>
          {/* Render logo and site title */}
          <Typography variant="h6" className={classes.title}>
            <Link to="/" className={classes.link}>
              Boston Startup Tracker
            </Link>
          </Typography>

          {/* Render navigation menu items */}
          <Button color="inherit" component={Link} to="/startups">
            Startups
          </Button>
          <Button color="inherit" component={Link} to="/investors">
            Investors
          </Button>
          <Button color="inherit" component={Link} to="/events">
            Events
          </Button>

          {/* Render user authentication buttons or user menu based on auth status */}
          {isAuthenticated ? (
            <>
              <IconButton
                edge="end"
                aria-label="account of current user"
                aria-controls="user-menu"
                aria-haspopup="true"
                onClick={handleUserMenuOpen}
                color="inherit"
              >
                <AccountCircle />
              </IconButton>
              <Menu
                id="user-menu"
                anchorEl={userAnchorEl}
                keepMounted
                open={Boolean(userAnchorEl)}
                onClose={handleUserMenuClose}
              >
                <MenuItem component={Link} to="/profile" onClick={handleUserMenuClose}>
                  Profile
                </MenuItem>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
            </>
          ) : (
            <>
              <Button color="inherit" component={Link} to="/login">
                Login
              </Button>
              <Button color="inherit" component={Link} to="/register">
                Register
              </Button>
            </>
          )}

          {/* Render mobile menu for smaller screens */}
          <IconButton
            edge="start"
            className={classes.menuButton}
            color="inherit"
            aria-label="menu"
            onClick={handleMobileMenuOpen}
          >
            <MenuIcon />
          </IconButton>
          <Menu
            id="mobile-menu"
            anchorEl={mobileAnchorEl}
            keepMounted
            open={Boolean(mobileAnchorEl)}
            onClose={handleMobileMenuClose}
          >
            <MenuItem component={Link} to="/startups" onClick={handleMobileMenuClose}>
              Startups
            </MenuItem>
            <MenuItem component={Link} to="/investors" onClick={handleMobileMenuClose}>
              Investors
            </MenuItem>
            <MenuItem component={Link} to="/events" onClick={handleMobileMenuClose}>
              Events
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
    </div>
  );
};

export default Header;

// Human tasks:
// - Implement responsive design for various screen sizes
// - Add animations for menu transitions
// - Implement keyboard navigation for accessibility
// - Add unit tests for the Header component
// - Implement a search bar in the header
// - Add support for multiple languages
// - Implement a notification system in the header
// - Add a dark mode toggle in the header