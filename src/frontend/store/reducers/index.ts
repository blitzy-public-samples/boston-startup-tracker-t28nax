// Import necessary dependencies and reducers
import { combineReducers } from 'redux';
import startupReducer from './startupReducer';
import investorReducer from './investorReducer';
import userReducer from './userReducer';
import searchReducer from './searchReducer';
import authReducer from './authReducer';
import { RootState } from '../types';

// Combine all individual reducers into a single root reducer
const rootReducer = combineReducers<RootState>({
  // Map each reducer to its corresponding state slice
  startups: startupReducer,
  investors: investorReducer,
  user: userReducer,
  search: searchReducer,
  auth: authReducer
});

// Export the combined root reducer
export default rootReducer;