import pandas as pd
import numpy as np
import re
from src.utils.logger import logger

class StartupCleaner:
    """Class for cleaning and validating startup data"""

    def clean_startup_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main method to clean startup data

        Args:
            df (pd.DataFrame): Input DataFrame containing startup data

        Returns:
            pd.DataFrame: Cleaned startup data
        """
        # Remove duplicate entries
        df = self.remove_duplicates(df)

        # Handle missing values
        df = self.handle_missing_values(df)

        # Standardize company names
        df = self.standardize_company_names(df)

        # Clean and validate website URLs
        df = self.clean_website_urls(df)

        # Normalize industry and sub-sector names
        df = self.normalize_industry_names(df)

        # Validate and clean employee count data
        df = self.clean_employee_count(df)

        # Standardize funding information
        df = self.standardize_funding_info(df)

        # Validate and format dates
        df = self.format_dates(df)

        logger.info("Startup data cleaning completed")
        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate startup entries

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with duplicates removed
        """
        # Identify duplicate entries based on company name and website
        duplicates = df.duplicated(subset=['company_name', 'website'], keep=False)

        # Keep the most recent or most complete entry in case of duplicates
        df = df.sort_values('last_updated', ascending=False).drop_duplicates(subset=['company_name', 'website'], keep='first')

        logger.info(f"Removed {sum(duplicates)} duplicate entries")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in startup data

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with missing values handled
        """
        # Identify columns with missing values
        missing_columns = df.columns[df.isnull().any()].tolist()

        for column in missing_columns:
            missing_count = df[column].isnull().sum()
            if column in ['company_name', 'website']:
                # Remove rows with missing critical information
                df = df.dropna(subset=[column])
                logger.info(f"Removed {missing_count} rows with missing {column}")
            elif column in ['industry', 'sub_sector']:
                # Fill missing industry/sub-sector with 'Unknown'
                df[column] = df[column].fillna('Unknown')
                logger.info(f"Filled {missing_count} missing values in {column} with 'Unknown'")
            elif column in ['employee_count', 'funding_amount']:
                # Fill missing numeric data with median
                df[column] = df[column].fillna(df[column].median())
                logger.info(f"Filled {missing_count} missing values in {column} with median")
            else:
                # For other columns, fill with 'Unknown' or 0 depending on dtype
                fill_value = 'Unknown' if df[column].dtype == 'object' else 0
                df[column] = df[column].fillna(fill_value)
                logger.info(f"Filled {missing_count} missing values in {column} with {fill_value}")

        return df

    def standardize_company_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize company names

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with standardized company names
        """
        # Remove leading/trailing whitespace
        df['company_name'] = df['company_name'].str.strip()

        # Convert to title case
        df['company_name'] = df['company_name'].str.title()

        # Remove common suffixes
        common_suffixes = r'\s+(Inc\.?|LLC|Ltd\.?|Limited|Corp\.?|Corporation)$'
        df['company_name'] = df['company_name'].str.replace(common_suffixes, '', regex=True)

        # Handle special characters and abbreviations
        df['company_name'] = df['company_name'].str.replace('&', 'and')
        df['company_name'] = df['company_name'].str.replace('@', 'at')

        logger.info("Standardized company names")
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
        url_pattern = r'^https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$'
        df['valid_url'] = df['website'].str.match(url_pattern)

        # Remove invalid URLs
        invalid_urls = df['valid_url'] == False
        df.loc[invalid_urls, 'website'] = np.nan
        logger.info(f"Removed {sum(invalid_urls)} invalid URLs")

        df = df.drop('valid_url', axis=1)

        return df

    def normalize_industry_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize industry and sub-sector names

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with normalized industry names
        """
        # Load industry and sub-sector normalization rules
        # This is a placeholder. In a real implementation, you would load these rules from a file or database
        industry_rules = {
            'AI': 'Artificial Intelligence',
            'ML': 'Machine Learning',
            'Fin Tech': 'FinTech',
            'Health Tech': 'HealthTech'
        }

        # Apply normalization rules to industry and sub-sector columns
        df['industry'] = df['industry'].replace(industry_rules)
        df['sub_sector'] = df['sub_sector'].replace(industry_rules)

        # Handle cases not covered by normalization rules
        df.loc[~df['industry'].isin(industry_rules.values()), 'industry'] = 'Other'
        df.loc[~df['sub_sector'].isin(industry_rules.values()), 'sub_sector'] = 'Other'

        logger.info("Normalized industry and sub-sector names")
        return df

    def clean_employee_count(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean employee count data

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with cleaned employee count data
        """
        # Convert employee count to numeric type
        df['employee_count'] = pd.to_numeric(df['employee_count'], errors='coerce')

        # Handle ranges (e.g., '10-50' employees)
        df['employee_count'] = df['employee_count'].apply(lambda x: np.mean([int(i) for i in str(x).split('-')]) if isinstance(x, str) and '-' in x else x)

        # Remove non-numeric characters
        df['employee_count'] = df['employee_count'].replace(r'[^0-9]', '', regex=True)

        # Validate employee count is within reasonable bounds
        df.loc[df['employee_count'] > 1000000, 'employee_count'] = np.nan

        # Flag suspicious values
        df['suspicious_employee_count'] = df['employee_count'] > 100000

        logger.info("Cleaned employee count data")
        return df

    def standardize_funding_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize funding information

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with standardized funding information
        """
        # Convert funding amounts to a standard currency (USD)
        # This is a placeholder. In a real implementation, you would use current exchange rates
        currency_conversion = {'EUR': 1.2, 'GBP': 1.4}
        df['funding_amount_usd'] = df.apply(lambda row: row['funding_amount'] * currency_conversion.get(row['funding_currency'], 1), axis=1)

        # Handle different funding formats
        df['funding_amount_usd'] = df['funding_amount_usd'].replace(r'[MK]', lambda x: '000000' if x.group() == 'M' else '000', regex=True).astype(float)

        # Standardize funding round names
        round_mapping = {'Seed': 'Seed', 'Series A': 'Series A', 'Series B': 'Series B', 'Series C': 'Series C'}
        df['funding_round'] = df['funding_round'].replace(round_mapping)

        # Validate funding amounts are within reasonable bounds
        df.loc[df['funding_amount_usd'] > 1000000000, 'funding_amount_usd'] = np.nan

        # Flag suspicious funding data
        df['suspicious_funding'] = df['funding_amount_usd'] > 100000000

        logger.info("Standardized funding information")
        return df

    def format_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and format dates

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with formatted dates
        """
        date_columns = ['founded_date', 'last_funding_date', 'last_updated']

        for column in date_columns:
            # Convert dates to a standard format (YYYY-MM-DD)
            df[column] = pd.to_datetime(df[column], errors='coerce', format='%Y-%m-%d')

            # Validate dates are within reasonable bounds
            df.loc[df[column] < '1900-01-01', column] = pd.NaT
            df.loc[df[column] > pd.Timestamp.now(), column] = pd.NaT

            # Flag invalid dates
            df[f'invalid_{column}'] = df[column].isnull()

        logger.info("Formatted and validated dates")
        return df

# Human tasks:
# TODO: Review and update industry and sub-sector normalization rules
# TODO: Implement more advanced duplicate detection algorithms
# TODO: Add data quality scoring mechanism
# TODO: Implement fuzzy matching for company names to catch near-duplicates
# TODO: Add logic to merge information from duplicate entries instead of just keeping one
# TODO: Review and update missing value handling strategies for each column
# TODO: Implement more advanced imputation techniques (e.g., KNN imputation)
# TODO: Maintain and update a list of common company name variations
# TODO: Implement fuzzy matching to standardize similar company names
# TODO: Implement URL validation using an external service or library
# TODO: Add logic to handle and standardize country-specific domains
# TODO: Regularly review and update industry and sub-sector normalization rules
# TODO: Implement machine learning-based classification for uncategorized industries
# TODO: Develop a method to estimate employee count when given as a range
# TODO: Implement logic to cross-validate employee count with other company metrics
# TODO: Implement currency conversion using up-to-date exchange rates
# TODO: Develop logic to infer funding rounds from other available data
# TODO: Implement logic to handle partial dates (e.g., only year or year-month)
# TODO: Add support for different regional date formats