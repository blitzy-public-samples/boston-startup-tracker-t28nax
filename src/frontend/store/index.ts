import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';
import rootReducer from './reducers';
import { RootState } from './types';

// Check if Redux DevTools are available in the browser
const composeEnhancers =
  (typeof window !== 'undefined' &&
    window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) ||
  compose;

// Configure and create the Redux store with middleware and dev tools
const configureStore = (): Store<RootState> => {
  // Create the store using createStore function
  const store = createStore(
    // Apply rootReducer to the store
    rootReducer,
    // Apply middleware (thunk) to the store and composeEnhancers for dev tools integration
    composeEnhancers(applyMiddleware(thunk))
  );

  return store;
};

// Create and export the configured store
const store = configureStore();

export { store };