import dayjs from 'dayjs';
import { DATE_FORMAT } from './constants';

// Format a date string according to the application's standard format
export function formatDate(date: string | Date): string {
  // Parse the input date using dayjs
  const parsedDate = dayjs(date);
  
  // Format the parsed date using the DATE_FORMAT constant
  return parsedDate.format(DATE_FORMAT);
}

// Format a number as currency
export function formatCurrency(amount: number, currency: string): string {
  // Use Intl.NumberFormat to format the amount as currency
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  });
  
  // Return the formatted currency string
  return formatter.format(amount);
}

// Truncate a string to a specified length
export function truncateText(text: string, maxLength: number): string {
  // Check if the text length exceeds maxLength
  if (text.length > maxLength) {
    // If it does, truncate the text and add ellipsis
    return text.slice(0, maxLength - 3) + '...';
  }
  
  // Return the original text if it's not longer than maxLength
  return text;
}

// Validate an email address
export function validateEmail(email: string): boolean {
  // Use a regular expression to validate the email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  // Return true if the email is valid, false otherwise
  return emailRegex.test(email);
}

// Create a debounced function that delays invoking func until after wait milliseconds have elapsed since the last time the debounced function was invoked
export function debounce(func: Function, wait: number): Function {
  // Create a closure to store the timeout ID
  let timeoutId: NodeJS.Timeout | null = null;
  
  // Return a new function that clears the previous timeout and sets a new one
  return function(this: any, ...args: any[]) {
    // Clear the previous timeout if it exists
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    // Set a new timeout to invoke the original function after the specified wait time
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, wait);
  };
}

// Human tasks:
// - Add error handling for invalid date inputs in formatDate function
// - Consider adding options for different date formats in formatDate function
// - Add support for different locales in formatCurrency function
// - Consider adding options for different currency display styles in formatCurrency function
// - Add option to truncate at word boundaries in truncateText function
// - Consider adding support for HTML truncation in truncateText function
// - Consider using a more comprehensive email validation library in validateEmail function
// - Add support for international email formats in validateEmail function
// - Add support for immediate execution option in debounce function
// - Consider adding TypeScript generics for better type inference in debounce function