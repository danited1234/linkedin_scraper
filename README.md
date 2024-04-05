# Linkedin Scraper

LinkdOutScraper is a Python library for scraping data from Linkedin

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install LinkedOutScraper.

```bash
pip install LinkdOutScraper==0.0.1
```

## Scrape Multiple Profiles With A Single Keyword

```python
from LinkedOutScraper import key_search
file_path= "somefile/path/with/csv/extension"
search = key_search.MultiProfiles(username="someusername@example.com",password="password",headless=True,file_path=file_path)
search.login()
profiles = search.get_multiple_profiles("Google")

```

## Scrape A Single Profile Using Their Profile Link

```python
from LinkedOutScraper import profile_scraper
search = profile_scarper.Linkedin(username="someusername@example.com",password="password")
search.login()
profiles = search.get_profiles("https://www.linkedin.com/in/muzammal-akram/")
for variables in profiles:
    print(variables)
```

## Scrape Job Results By Entering A Query

```python
from LinkedOutScraper import job_search
search = job_search.JobSearch("someusername@example","password")
search.login()
search.find_jobs("Senior Python Developer")
```
