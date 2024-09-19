import pytest
import pandas as pd
import numpy as np
from src.data_collection.data_cleaning.startup_cleaner import StartupCleaner

class TestStartupCleaner:

    @pytest.fixture
    def sample_data(self):
        # Create a sample DataFrame for testing
        return pd.DataFrame({
            'company_name': ['Test Inc.', 'Sample LLC', 'Example Corp'],
            'website': ['www.test.com', 'http://sample.com', 'https://example.com'],
            'industry': ['Tech', 'Finance', 'Healthcare'],
            'employee_count': ['1-10', '50+', '100-500'],
            'funding': ['$1M', '$5M Series A', 'Bootstrapped'],
            'founded_date': ['2020-01-01', '2019-05-15', '2018-12-31']
        })

    def test_clean_startup_data(self, sample_data):
        cleaner = StartupCleaner()
        cleaned_data = cleaner.clean_startup_data(sample_data)

        # Assert that the returned DataFrame has the expected shape and columns
        assert cleaned_data.shape[0] == sample_data.shape[0]
        assert set(cleaned_data.columns) == set(sample_data.columns)

    def test_remove_duplicates(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'company_name': ['Test Inc.', 'Test Inc.', 'Sample LLC'],
            'website': ['www.test.com', 'www.test.com', 'www.sample.com']
        })
        cleaned_data = cleaner.remove_duplicates(data)

        # Assert that duplicates are removed correctly
        assert cleaned_data.shape[0] < data.shape[0]
        assert cleaned_data['company_name'].nunique() == cleaned_data.shape[0]

    def test_handle_missing_values(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'company_name': ['Test Inc.', 'Sample LLC', np.nan],
            'employee_count': ['1-10', np.nan, '100-500']
        })
        cleaned_data = cleaner.handle_missing_values(data)

        # Assert that missing values are handled correctly
        assert cleaned_data.isnull().sum().sum() == 0
        assert cleaned_data.loc[cleaned_data['company_name'] == 'Unknown', 'company_name'].count() == 1
        assert cleaned_data.loc[cleaned_data['employee_count'] == 'Unknown', 'employee_count'].count() == 1

    def test_standardize_company_names(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'company_name': ['Test, Inc.', 'Sample LLC', 'Example Corp.']
        })
        cleaned_data = cleaner.standardize_company_names(data)

        # Assert that company names are standardized correctly
        assert all(name.strip() for name in cleaned_data['company_name'])
        assert not any(name.endswith(('Inc.', 'LLC', 'Corp.')) for name in cleaned_data['company_name'])

    def test_clean_website_urls(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'website': ['www.test.com', 'http://sample.com', 'https://example.com', 'invalid-url']
        })
        cleaned_data = cleaner.clean_website_urls(data)

        # Assert that URLs are cleaned and validated correctly
        assert all(url.startswith(('http://', 'https://')) for url in cleaned_data['website'] if pd.notna(url))
        assert cleaned_data['website'].isnull().sum() == 1  # Invalid URL should be removed or flagged

    def test_normalize_industry_names(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'industry': ['Tech', 'Information Technology', 'FinTech', 'Healthcare IT']
        })
        cleaned_data = cleaner.normalize_industry_names(data)

        # Assert that industry names are normalized correctly
        assert set(cleaned_data['industry']) == set(['Technology', 'Finance', 'Healthcare'])

    def test_clean_employee_count(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'employee_count': ['1-10', '50+', '100-500', 'Unknown']
        })
        cleaned_data = cleaner.clean_employee_count(data)

        # Assert that employee counts are cleaned correctly
        assert all(isinstance(count, (int, str)) for count in cleaned_data['employee_count'])
        assert 'Unknown' in cleaned_data['employee_count'].values

    def test_standardize_funding_info(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'funding': ['$1M', '$5M Series A', 'Bootstrapped', '$10,000,000']
        })
        cleaned_data = cleaner.standardize_funding_info(data)

        # Assert that funding information is standardized correctly
        assert all(isinstance(amount, (float, str)) for amount in cleaned_data['funding'])
        assert 'Bootstrapped' in cleaned_data['funding'].values

    def test_format_dates(self):
        cleaner = StartupCleaner()
        data = pd.DataFrame({
            'founded_date': ['2020-01-01', '5/15/2019', '12/31/2018', 'Invalid Date']
        })
        cleaned_data = cleaner.format_dates(data)

        # Assert that dates are formatted correctly
        assert all(pd.to_datetime(date, errors='coerce').notna() for date in cleaned_data['founded_date'] if date != 'Unknown')
        assert 'Unknown' in cleaned_data['founded_date'].values