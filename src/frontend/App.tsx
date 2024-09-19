import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { ThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import Home from './pages/Home';
import Search from './pages/Search';
import Company from './pages/Company';
import Investor from './pages/Investor';
import User from './pages/User';
import theme from './styles/theme';

const App: React.FC = () => {
  return (
    // Wrap the entire app with ThemeProvider and pass the custom theme
    <ThemeProvider theme={theme}>
      {/* Include CssBaseline for consistent baseline styles */}
      <CssBaseline />
      {/* Set up BrowserRouter for routing */}
      <Router>
        <div className="App">
          {/* Render Header component */}
          <Header />
          <main>
            {/* Set up Switch component for exclusive routing */}
            <Switch>
              {/* Define Route for Home page ('/') */}
              <Route exact path="/" component={Home} />
              {/* Define Route for Search page ('/search') */}
              <Route path="/search" component={Search} />
              {/* Define Route for Company page ('/company/:id') */}
              <Route path="/company/:id" component={Company} />
              {/* Define Route for Investor page ('/investor/:id') */}
              <Route path="/investor/:id" component={Investor} />
              {/* Define Route for User page ('/user/:id') */}
              <Route path="/user/:id" component={User} />
            </Switch>
          </main>
          {/* Render Footer component */}
          <Footer />
        </div>
      </Router>
    </ThemeProvider>
  );
};

export default App;

// Human tasks:
// TODO: Implement error boundary to catch and display errors gracefully
// TODO: Add loading indicators for route transitions
// TODO: Implement code splitting for better performance
// TODO: Add authentication checks for protected routes
// TODO: Implement a 404 Not Found page for undefined routes
// TODO: Add analytics tracking for page views
// TODO: Implement internationalization (i18n) support