import pandas as pd
import numpy as np
import re
from src.utils.logger import logger

class InvestorCleaner:
    """Class for cleaning and validating investor data"""

    def clean_investor_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main method to clean investor data
        
        Args:
            df (pd.DataFrame): Input investor data
        
        Returns:
            pd.DataFrame: Cleaned investor data
        """
        # Remove duplicate entries
        df = self.remove_duplicates(df)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Standardize investor names
        df = self.standardize_investor_names(df)
        
        # Clean and validate website URLs
        df = self.clean_website_urls(df)
        
        # Normalize investor types
        df = self.normalize_investor_types(df)
        
        # Standardize investment focus areas
        df = self.standardize_investment_focus(df)
        
        # Clean and validate investment amounts
        df = self.clean_investment_amounts(df)
        
        # Validate and format dates
        df = self.format_dates(df)
        
        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate investor entries
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with duplicates removed
        """
        # Identify duplicate entries based on investor name and website
        duplicates = df.duplicated(subset=['investor_name', 'website'], keep=False)
        
        # Keep the most recent or most complete entry in case of duplicates
        df = df.sort_values('last_updated', ascending=False).drop_duplicates(subset=['investor_name', 'website'], keep='first')
        
        logger.info(f"Removed {sum(duplicates)} duplicate entries")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in investor data
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with missing values handled
        """
        # Identify columns with missing values
        missing_columns = df.columns[df.isnull().any()].tolist()
        
        for column in missing_columns:
            missing_count = df[column].isnull().sum()
            
            if column in ['investor_name', 'website']:
                # Remove rows with missing critical information
                df = df.dropna(subset=[column])
                logger.info(f"Removed {missing_count} rows with missing {column}")
            elif column in ['investment_focus', 'investor_type']:
                # Fill with 'Unknown' for categorical columns
                df[column].fillna('Unknown', inplace=True)
                logger.info(f"Filled {missing_count} missing values in {column} with 'Unknown'")
            elif column in ['investment_amount']:
                # Fill with median for numerical columns
                median_value = df[column].median()
                df[column].fillna(median_value, inplace=True)
                logger.info(f"Filled {missing_count} missing values in {column} with median value {median_value}")
            else:
                # For other columns, fill with an empty string
                df[column].fillna('', inplace=True)
                logger.info(f"Filled {missing_count} missing values in {column} with empty string")
        
        return df

    def standardize_investor_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize investor names
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with standardized investor names
        """
        # Remove leading/trailing whitespace
        df['investor_name'] = df['investor_name'].str.strip()
        
        # Convert to title case
        df['investor_name'] = df['investor_name'].str.title()
        
        # Remove common suffixes
        common_suffixes = r'\s+(LP|LLC|Inc\.|Corp\.|Ltd\.)$'
        df['investor_name'] = df['investor_name'].str.replace(common_suffixes, '', regex=True)
        
        # Handle special characters and abbreviations
        df['investor_name'] = df['investor_name'].str.replace('&', 'and')
        df['investor_name'] = df['investor_name'].str.replace('Vc', 'Venture Capital')
        
        logger.info("Standardized investor names")
        return df

    def clean_website_urls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate website URLs
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with cleaned website URLs
        """
        # Remove leading/trailing whitespace
        df['website'] = df['website'].str.strip()
        
        # Ensure all URLs start with http:// or https://
        df['website'] = df['website'].apply(lambda x: f"https://{x}" if x and not x.startswith(('http://', 'https://')) else x)
        
        # Remove www. prefix if present
        df['website'] = df['website'].str.replace(r'^https?://www\.', 'https://', regex=True)
        
        # Validate URL format using regex
        url_pattern = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
        df['valid_url'] = df['website'].str.match(url_pattern)
        
        # Remove invalid URLs
        invalid_urls = df[~df['valid_url']]['website'].tolist()
        df.loc[~df['valid_url'], 'website'] = ''
        df.drop('valid_url', axis=1, inplace=True)
        
        logger.info(f"Cleaned website URLs. Removed {len(invalid_urls)} invalid URLs.")
        return df

    def normalize_investor_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize investor types
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with normalized investor types
        """
        # Load investor type normalization rules
        normalization_rules = {
            'VC': 'Venture Capital',
            'Venture Capital Firm': 'Venture Capital',
            'Angel': 'Angel Investor',
            'Angel Group': 'Angel Investor',
            'PE': 'Private Equity',
            'Private Equity Firm': 'Private Equity',
            'Corp': 'Corporate Investor',
            'Corporate Venture': 'Corporate Investor',
            'Accelerator': 'Accelerator/Incubator',
            'Incubator': 'Accelerator/Incubator'
        }
        
        # Apply normalization rules to investor type column
        df['investor_type'] = df['investor_type'].replace(normalization_rules)
        
        # Handle cases not covered by normalization rules
        df.loc[~df['investor_type'].isin(normalization_rules.values()), 'investor_type'] = 'Other'
        
        logger.info("Normalized investor types")
        return df

    def standardize_investment_focus(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize investment focus areas
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with standardized investment focus areas
        """
        # Load investment focus area standardization rules
        focus_area_rules = {
            'AI': 'Artificial Intelligence',
            'ML': 'Machine Learning',
            'Fintech': 'Financial Technology',
            'SaaS': 'Software as a Service',
            'Biotech': 'Biotechnology',
            'Healthtech': 'Healthcare Technology'
        }
        
        # Apply standardization rules to investment focus column
        df['investment_focus'] = df['investment_focus'].replace(focus_area_rules)
        
        # Handle multi-focus investors
        df['investment_focus'] = df['investment_focus'].str.split(',').apply(lambda x: [item.strip() for item in x])
        
        # Categorize focus areas into broader sectors
        sector_mapping = {
            'Artificial Intelligence': 'Technology',
            'Machine Learning': 'Technology',
            'Financial Technology': 'Finance',
            'Software as a Service': 'Technology',
            'Biotechnology': 'Healthcare',
            'Healthcare Technology': 'Healthcare'
        }
        df['sector'] = df['investment_focus'].apply(lambda x: [sector_mapping.get(focus, 'Other') for focus in x])
        df['sector'] = df['sector'].apply(lambda x: list(set(x)))  # Remove duplicates
        
        logger.info("Standardized investment focus areas")
        return df

    def clean_investment_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate investment amounts
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with cleaned investment amounts
        """
        def parse_amount(amount):
            if pd.isna(amount):
                return np.nan
            amount = str(amount).upper()
            if 'K' in amount:
                return float(amount.replace('K', '')) * 1000
            elif 'M' in amount:
                return float(amount.replace('M', '')) * 1000000
            elif 'B' in amount:
                return float(amount.replace('B', '')) * 1000000000
            else:
                return float(amount.replace(',', ''))

        # Convert investment amounts to numeric type
        df['investment_amount'] = df['investment_amount'].apply(parse_amount)
        
        # Validate investment amounts are within reasonable bounds
        lower_bound = 10000  # $10,000
        upper_bound = 10000000000  # $10 billion
        df.loc[df['investment_amount'] < lower_bound, 'investment_amount'] = np.nan
        df.loc[df['investment_amount'] > upper_bound, 'investment_amount'] = np.nan
        
        logger.info("Cleaned and validated investment amounts")
        return df

    def format_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and format dates
        
        Args:
            df (pd.DataFrame): Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with formatted dates
        """
        date_columns = ['founded_date', 'last_investment_date']
        
        for column in date_columns:
            # Convert dates to a standard format (YYYY-MM-DD)
            df[column] = pd.to_datetime(df[column], errors='coerce', format='%Y-%m-%d')
            
            # Validate dates are within reasonable bounds
            min_date = pd.Timestamp('1900-01-01')
            max_date = pd.Timestamp.now()
            df.loc[df[column] < min_date, column] = pd.NaT
            df.loc[df[column] > max_date, column] = pd.NaT
            
            # Flag invalid dates
            invalid_dates = df[column].isna().sum()
            logger.info(f"Found {invalid_dates} invalid dates in {column}")
        
        logger.info("Formatted and validated dates")
        return df

# Human tasks:
# TODO: Review and update investor type normalization rules
# TODO: Implement more advanced duplicate detection algorithms
# TODO: Add data quality scoring mechanism
# TODO: Implement fuzzy matching for investor names to catch near-duplicates
# TODO: Add logic to merge information from duplicate entries instead of just keeping one
# TODO: Review and update missing value handling strategies for each column
# TODO: Implement more advanced imputation techniques (e.g., KNN imputation)
# TODO: Maintain and update a list of common investor name variations
# TODO: Implement fuzzy matching to standardize similar investor names
# TODO: Implement URL validation using an external service or library
# TODO: Add logic to handle and standardize country-specific domains
# TODO: Regularly review and update investor type normalization rules
# TODO: Implement machine learning-based classification for uncategorized investor types
# TODO: Develop and maintain a comprehensive list of investment focus areas and their categorizations
# TODO: Implement natural language processing techniques to extract focus areas from unstructured text
# TODO: Implement currency conversion using up-to-date exchange rates
# TODO: Develop logic to estimate investment amounts when given as ranges
# TODO: Implement logic to handle partial dates (e.g., only year or year-month)
# TODO: Add support for different regional date formats