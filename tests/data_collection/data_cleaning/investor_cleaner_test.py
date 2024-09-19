import pytest
import pandas as pd
import numpy as np
from src.data_collection.data_cleaning.investor_cleaner import InvestorCleaner

class TestInvestorCleaner:

    @pytest.fixture
    def sample_investor_data(self):
        # Create a sample DataFrame with investor data
        return pd.DataFrame({
            'investor_name': ['Acme Ventures', 'Beta Capital', 'Gamma Investments'],
            'investor_type': ['Venture Capital', 'Angel Investor', 'Private Equity'],
            'website': ['www.acme.com', 'https://beta.capital', 'gamma-inv.com'],
            'investment_focus': ['Tech, Healthcare', 'Fintech', 'Real Estate, Energy'],
            'investment_amount': ['$1M - $5M', 'Up to $500K', '10M+'],
            'founded_date': ['2010-01-01', '2015', '05/15/2008']
        })

    def test_clean_investor_data(self, sample_investor_data):
        # Create an InvestorCleaner instance
        cleaner = InvestorCleaner()
        
        # Call the clean_investor_data method
        cleaned_data = cleaner.clean_investor_data(sample_investor_data)
        
        # Assert that the returned DataFrame has the expected shape and columns
        expected_columns = ['investor_name', 'investor_type', 'website', 'investment_focus', 'investment_amount', 'founded_date']
        assert cleaned_data.shape[0] == 3
        assert all(col in cleaned_data.columns for col in expected_columns)

    def test_remove_duplicates(self):
        # Create a sample DataFrame with duplicate entries
        data = pd.DataFrame({
            'investor_name': ['Acme Ventures', 'Beta Capital', 'Acme Ventures'],
            'investor_type': ['Venture Capital', 'Angel Investor', 'Venture Capital']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.remove_duplicates(data)
        
        # Assert that duplicates are removed correctly
        assert result.shape[0] == 2
        assert not result.duplicated().any()

    def test_handle_missing_values(self):
        # Create a sample DataFrame with missing values
        data = pd.DataFrame({
            'investor_name': ['Acme Ventures', 'Beta Capital', np.nan],
            'investor_type': ['Venture Capital', np.nan, 'Private Equity'],
            'investment_amount': [np.nan, '$1M', '$5M']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.handle_missing_values(data)
        
        # Assert that missing values are handled correctly
        assert not result.isnull().any().any()
        assert result.loc[2, 'investor_name'] == 'Unknown'
        assert result.loc[1, 'investor_type'] == 'Other'
        assert result.loc[0, 'investment_amount'] == 'Unknown'

    def test_standardize_investor_names(self):
        # Create a sample DataFrame with various investor name formats
        data = pd.DataFrame({
            'investor_name': ['Acme Ventures, LP', 'BETA CAPITAL LLC', 'Gamma Investments Inc.']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.standardize_investor_names(data)
        
        # Assert that investor names are standardized correctly
        assert result['investor_name'].tolist() == ['Acme Ventures', 'Beta Capital', 'Gamma Investments']

    def test_clean_website_urls(self):
        # Create a sample DataFrame with various URL formats
        data = pd.DataFrame({
            'website': ['www.acme.com', 'https://beta.capital', 'invalid-url', 'http://gamma.inv']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.clean_website_urls(data)
        
        # Assert that URLs are cleaned and validated correctly
        assert result['website'].tolist() == ['https://www.acme.com', 'https://beta.capital', '', 'http://gamma.inv']

    def test_normalize_investor_types(self):
        # Create a sample DataFrame with various investor types
        data = pd.DataFrame({
            'investor_type': ['VC', 'angel', 'PE Firm', 'Accelerator', 'Unknown']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.normalize_investor_types(data)
        
        # Assert that investor types are normalized correctly
        expected_types = ['Venture Capital', 'Angel Investor', 'Private Equity', 'Accelerator', 'Other']
        assert result['investor_type'].tolist() == expected_types

    def test_standardize_investment_focus(self):
        # Create a sample DataFrame with various investment focus descriptions
        data = pd.DataFrame({
            'investment_focus': ['Tech, Healthcare', 'Fintech, AI', 'Real Estate, Energy, Biotech']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.standardize_investment_focus(data)
        
        # Assert that investment focus areas are standardized correctly
        expected_focus = ['Technology, Healthcare', 'Financial Technology, Artificial Intelligence', 'Real Estate, Energy, Biotechnology']
        assert result['investment_focus'].tolist() == expected_focus

    def test_clean_investment_amounts(self):
        # Create a sample DataFrame with various investment amount formats
        data = pd.DataFrame({
            'investment_amount': ['$1M - $5M', 'Up to $500K', '10M+', '$50,000 - $100,000']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.clean_investment_amounts(data)
        
        # Assert that investment amounts are cleaned correctly
        expected_amounts = ['1000000-5000000', '0-500000', '10000000+', '50000-100000']
        assert result['investment_amount'].tolist() == expected_amounts

    def test_format_dates(self):
        # Create a sample DataFrame with various date formats
        data = pd.DataFrame({
            'founded_date': ['2010-01-01', '2015', '05/15/2008', 'Invalid Date']
        })
        
        cleaner = InvestorCleaner()
        result = cleaner.format_dates(data)
        
        # Assert that dates are formatted correctly
        expected_dates = ['2010-01-01', '2015-01-01', '2008-05-15', None]
        assert result['founded_date'].tolist() == expected_dates

# No human tasks to be added as comments for this file.