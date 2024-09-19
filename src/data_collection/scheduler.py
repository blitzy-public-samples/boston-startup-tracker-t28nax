import schedule
import time
import threading
from ..utils import logger
from .scrapers.startup_scraper import StartupScraper
from .scrapers.investor_scraper import InvestorScraper
from .scrapers.job_scraper import JobScraper
from .scrapers.news_scraper import NewsScraper
from .data_enrichment.startup_enricher import StartupEnricher
from .data_enrichment.investor_enricher import InvestorEnricher

# Global variables for scraping and enrichment intervals
STARTUP_SCRAPE_INTERVAL = 24  # hours
INVESTOR_SCRAPE_INTERVAL = 24  # hours
JOB_SCRAPE_INTERVAL = 12  # hours
NEWS_SCRAPE_INTERVAL = 6  # hours
ENRICHMENT_INTERVAL = 48  # hours

def run_startup_scraper():
    """Execute the startup scraping task"""
    # Initialize StartupScraper
    startup_scraper = StartupScraper()
    
    # Execute scrape_startups method
    startup_scraper.scrape_startups()
    
    # Log the completion of the task
    logger.info("Startup scraping task completed")

def run_investor_scraper():
    """Execute the investor scraping task"""
    # Initialize InvestorScraper
    investor_scraper = InvestorScraper()
    
    # Execute scrape_investors method
    investor_scraper.scrape_investors()
    
    # Log the completion of the task
    logger.info("Investor scraping task completed")

def run_job_scraper():
    """Execute the job scraping task"""
    # Initialize JobScraper
    job_scraper = JobScraper()
    
    # Execute scrape_jobs method
    job_scraper.scrape_jobs()
    
    # Log the completion of the task
    logger.info("Job scraping task completed")

def run_news_scraper():
    """Execute the news scraping task"""
    # Initialize NewsScraper
    news_scraper = NewsScraper()
    
    # Execute scrape_news method
    news_scraper.scrape_news()
    
    # Log the completion of the task
    logger.info("News scraping task completed")

def run_data_enrichment():
    """Execute the data enrichment task"""
    # Initialize StartupEnricher and InvestorEnricher
    startup_enricher = StartupEnricher()
    investor_enricher = InvestorEnricher()
    
    # Execute enrich_startup_data method
    startup_enricher.enrich_startup_data()
    
    # Execute enrich_investor_data method
    investor_enricher.enrich_investor_data()
    
    # Log the completion of the task
    logger.info("Data enrichment task completed")

def run_scheduled_tasks():
    """Run all scheduled tasks in separate threads"""
    # Create a new thread for each scheduled task
    startup_thread = threading.Thread(target=schedule.every(STARTUP_SCRAPE_INTERVAL).hours.do(run_startup_scraper))
    investor_thread = threading.Thread(target=schedule.every(INVESTOR_SCRAPE_INTERVAL).hours.do(run_investor_scraper))
    job_thread = threading.Thread(target=schedule.every(JOB_SCRAPE_INTERVAL).hours.do(run_job_scraper))
    news_thread = threading.Thread(target=schedule.every(NEWS_SCRAPE_INTERVAL).hours.do(run_news_scraper))
    enrichment_thread = threading.Thread(target=schedule.every(ENRICHMENT_INTERVAL).hours.do(run_data_enrichment))
    
    # Start all threads
    startup_thread.start()
    investor_thread.start()
    job_thread.start()
    news_thread.start()
    enrichment_thread.start()
    
    # Enter an infinite loop to run pending tasks
    while True:
        schedule.run_pending()
        # Sleep for a short interval between checks
        time.sleep(1)

# Human tasks:
# TODO: Implement error handling and retries for failed scraping attempts
# TODO: Add monitoring for the duration and success rate of scraping tasks
# TODO: Implement error handling and retries for failed enrichment attempts
# TODO: Add monitoring for the duration and success rate of enrichment tasks
# TODO: Implement a graceful shutdown mechanism
# TODO: Add monitoring and alerting for thread health
# TODO: Optimize the sleep interval for better performance