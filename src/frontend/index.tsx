import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import App from './App';
import store from './store';
import './styles/global.css';

// Function to render the root component of the application
function render() {
  // Wrap the App component with Redux Provider
  // Pass the Redux store to the Provider
  const rootComponent = (
    <Provider store={store}>
      <App />
    </Provider>
  );

  // Use ReactDOM.render to mount the application to the DOM
  // Target the root element in the HTML
  ReactDOM.render(rootComponent, document.getElementById('root'));
}

// Call the render function to start the application
render();