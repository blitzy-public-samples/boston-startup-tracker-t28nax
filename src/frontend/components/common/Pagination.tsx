import React from 'react';
import { Pagination as MuiPagination } from '@material-ui/lab';
import { makeStyles } from '@material-ui/core/styles';

// Define styles for the Pagination component
const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    justifyContent: 'center',
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
}));

// Define the props interface for the Pagination component
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (event: React.ChangeEvent<unknown>, page: number) => void;
}

// Main Pagination component
const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
  // Get the classes object from useStyles hook
  const classes = useStyles();

  return (
    <div className={classes.root}>
      {/* Render MuiPagination component with appropriate props */}
      <MuiPagination
        count={totalPages}
        page={currentPage}
        onChange={onPageChange}
        color="primary"
        size="large"
        showFirstButton
        showLastButton
      />
    </div>
  );
};

export default Pagination;

// Human tasks:
// TODO: Implement responsive design for various screen sizes
// TODO: Add accessibility features (ARIA labels, keyboard navigation)
// TODO: Add unit tests for the Pagination component
// TODO: Implement custom styling options for different themes
// TODO: Add support for different pagination variants (e.g., simple, rounded)
// TODO: Implement a 'Go to page' input field for quick navigation
// TODO: Add support for custom page size selection