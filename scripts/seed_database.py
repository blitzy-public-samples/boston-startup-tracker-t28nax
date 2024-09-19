import sys
import os
import django
from faker import Faker
import random
import datetime

# Set up global variables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'src', 'backend'))
faker = Faker()

def setup_django():
    # Set up Django environment
    sys.path.append(PROJECT_ROOT)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boston_startup_tracker.settings')
    django.setup()

def create_startups(num_startups):
    # Create fake startup data
    from startups.models import Startup
    startups = []
    for _ in range(num_startups):
        startup = Startup(
            name=faker.company(),
            description=faker.catch_phrase(),
            founded_date=faker.date_between(start_date='-10y', end_date='today'),
            website=faker.url(),
            logo_url=faker.image_url(),
            industry=random.choice(['Tech', 'Biotech', 'Fintech', 'Edtech', 'Cleantech']),
            employee_count=random.randint(1, 1000),
            funding_stage=random.choice(['Seed', 'Series A', 'Series B', 'Series C', 'IPO'])
        )
        startup.save()
        startups.append(startup)
    return startups

def create_investors(num_investors):
    # Create fake investor data
    from investors.models import Investor
    investors = []
    for _ in range(num_investors):
        investor = Investor(
            name=faker.company(),
            type=random.choice(['VC', 'Angel', 'Corporate', 'Accelerator']),
            website=faker.url(),
            logo_url=faker.image_url(),
            description=faker.paragraph(),
            founded_date=faker.date_between(start_date='-30y', end_date='today'),
            total_investments=random.randint(1000000, 1000000000)
        )
        investor.save()
        investors.append(investor)
    return investors

def create_funding_rounds(startups, investors):
    # Create fake funding round data
    from funding.models import FundingRound
    for startup in startups:
        for _ in range(random.randint(0, 3)):
            funding_round = FundingRound(
                startup=startup,
                round_type=random.choice(['Seed', 'Series A', 'Series B', 'Series C']),
                amount=random.randint(100000, 100000000),
                date=faker.date_between(start_date=startup.founded_date, end_date='today'),
                lead_investor=random.choice(investors)
            )
            funding_round.save()
            funding_round.investors.set(random.sample(investors, k=random.randint(1, 5)))

def create_job_postings(startups):
    # Create fake job posting data
    from jobs.models import JobPosting
    for startup in startups:
        for _ in range(random.randint(0, 5)):
            job_posting = JobPosting(
                startup=startup,
                title=faker.job(),
                description=faker.text(),
                location=faker.city(),
                salary_range=f"${random.randint(30, 200)}k - ${random.randint(50, 250)}k",
                posted_date=faker.date_between(start_date='-30d', end_date='today'),
                application_url=faker.url()
            )
            job_posting.save()

def create_news_articles(startups):
    # Create fake news article data
    from news.models import NewsArticle
    for startup in startups:
        for _ in range(random.randint(0, 3)):
            news_article = NewsArticle(
                startup=startup,
                title=faker.sentence(),
                content=faker.paragraphs(nb=3),
                author=faker.name(),
                publication_date=faker.date_between(start_date='-1y', end_date='today'),
                source_url=faker.url()
            )
            news_article.save()

def main():
    try:
        setup_django()
        
        print("Seeding database...")
        startups = create_startups(50)
        print(f"Created {len(startups)} startups")
        
        investors = create_investors(20)
        print(f"Created {len(investors)} investors")
        
        create_funding_rounds(startups, investors)
        print("Created funding rounds")
        
        create_job_postings(startups)
        print("Created job postings")
        
        create_news_articles(startups)
        print("Created news articles")
        
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"An error occurred while seeding the database: {str(e)}")

if __name__ == '__main__':
    main()

# Human tasks:
# TODO: Review and adjust the number of entities created for each model
# TODO: Ensure the fake data generation is realistic and relevant to the Boston startup ecosystem
# TODO: Add more specific data generation for Boston-related information (e.g., local addresses, area-specific industry focus)
# TODO: Implement command-line arguments to control the amount of data generated
# TODO: Add option to reset the database before seeding
# TODO: Create relationships between entities that reflect realistic scenarios
# TODO: Ensure generated data complies with any business rules or constraints in the models