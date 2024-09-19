import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Typography, CircularProgress, Button, TextField, Grid } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { fetchUserProfile, updateUserProfile } from '../../store/actions/userActions';
import { RootState } from '../../store/types';

// Define styles for the component
const useStyles = makeStyles((theme) => ({
  container: {
    marginTop: theme.spacing(4),
  },
  title: {
    marginBottom: theme.spacing(3),
  },
  form: {
    width: '100%',
    marginTop: theme.spacing(3),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
  cancelButton: {
    marginLeft: theme.spacing(2),
  },
}));

const User: React.FC = () => {
  const classes = useStyles();
  const dispatch = useDispatch();
  const { id } = useParams<{ id: string }>();

  // State for user data and edit mode
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    bio: '',
  });
  const [editMode, setEditMode] = useState(false);

  // Select user profile data and loading status from Redux store
  const { user, loading, error } = useSelector((state: RootState) => state.user);

  // Fetch user profile data when component mounts or user ID changes
  useEffect(() => {
    dispatch(fetchUserProfile(id));
  }, [dispatch, id]);

  // Update local state when user data is fetched
  useEffect(() => {
    if (user) {
      setUserData({
        name: user.name,
        email: user.email,
        bio: user.bio || '',
      });
    }
  }, [user]);

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(updateUserProfile(id, userData));
    setEditMode(false);
  };

  // Toggle edit mode
  const toggleEditMode = () => {
    setEditMode((prevMode) => !prevMode);
    if (editMode) {
      // Reset form data if canceling edit
      setUserData({
        name: user.name,
        email: user.email,
        bio: user.bio || '',
      });
    }
  };

  return (
    <Container className={classes.container} maxWidth="md">
      <Typography variant="h4" className={classes.title}>
        User Profile
      </Typography>

      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <>
          {!editMode ? (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6">Name: {userData.name}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6">Email: {userData.email}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6">Bio: {userData.bio}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Button variant="contained" color="primary" onClick={toggleEditMode}>
                  Edit Profile
                </Button>
              </Grid>
            </Grid>
          ) : (
            <form className={classes.form} onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Name"
                    name="name"
                    value={userData.name}
                    onChange={handleInputChange}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={userData.email}
                    onChange={handleInputChange}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Bio"
                    name="bio"
                    multiline
                    rows={4}
                    value={userData.bio}
                    onChange={handleInputChange}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button type="submit" variant="contained" color="primary" className={classes.submit}>
                    Save Changes
                  </Button>
                  <Button variant="contained" onClick={toggleEditMode} className={classes.cancelButton}>
                    Cancel
                  </Button>
                </Grid>
              </Grid>
            </form>
          )}
        </>
      )}
    </Container>
  );
};

export default User;

// Human tasks:
// TODO: Implement form validation for user input
// TODO: Add password change functionality
// TODO: Implement profile picture upload feature
// TODO: Add user activity history section
// TODO: Implement email verification process for email changes
// TODO: Add option to delete user account
// TODO: Implement two-factor authentication setup
// TODO: Add social media account linking functionality