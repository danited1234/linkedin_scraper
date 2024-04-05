from .profile_scraper import Linkedin
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from selenium.common.exceptions import TimeoutException


class JobSearch(Linkedin):
    """
    JobSearch Class That Will Scrape Job Results Based On Your Query
    #### Arguments
    * username ( str ) Username/Email of Linkedin
    * password ( str ) Password Of Linkedin
    * headless ( str ) Set to True if you want to go headless
    * file_path ( str ) file path of the csv file if you want to save results into a csv file
    """

    def __init__(self, username: str = None, password: str = None, headless: str = None,
                 file_path: str = None) -> None:
        super().__init__(username, password, headless)
        self.file_path = file_path

    def save_job_data(self, filename: str=None, job_url: str=None,
            job_title: str=None, company_name: str=None, location_of_job: str=None) -> None:
        """
        Save Data Into CSV File Related To Job
        #### Arguments
        * filename ( str ) path or filename where the CSV is located
        * job_url ( str )
        * job_title ( str )
        * company_name ( str )
        * location_of_job ( str )
        """
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Job Link', 'Job Title', 'Company Name', 'Location']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not self.headers_written:
                writer.writeheader()
                self.headers_written = True
            writer.writerow({'Job Link': job_url, 'Job Title': job_title, 'Company Name': company_name, 'Location': location_of_job})

    def scroll_div (self,scrollable_div: str) -> None:
    # Get the total scroll height of the div
        div_element = self.driver.find_element(By.CLASS_NAME,scrollable_div)
        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight",div_element)

        # Define the scroll speed (in seconds)
        scroll_speed = 0.5  #scroll 0.5 seconds per scroll action

        # Calculate the number of scroll steps
        num_steps = int(scroll_height / (div_element.size['height'] * 0.5))

        # Scroll through the div gradually
        for i in range(num_steps):
            # Calculate the scroll amount for each step
            scroll_amount = (scroll_height / num_steps) * i
            # Scroll the div to the calculated scroll amount using JavaScript
            self.driver.execute_script("arguments[0].scrollTop = arguments[1];", div_element, scroll_amount)
            # Wait for a short time to allow content to load
            time.sleep(scroll_speed)

    # Scroll to the bottom one final time to ensure all content is loaded
        self.driver.execute_script("arguments[0].scrollTop = arguments[1];", div_element, scroll_height)



    def find_jobs(self, query: str) -> None:
        """
        Finds Jobs on Linkedin Based on User's Query
        #### Arguments
        * query ( str ) 
         
        Example Usage
        `.find_jobs("Junior Web Developer")`
        """
        jobs = []
        url = f"https://www.linkedin.com/jobs/?keywords={query}"
        self.driver.get(url)
        try:
            show_all_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"app-aware-link.discovery-templates-jobs-home-vertical-list__footer.artdeco-button.artdeco-button--2.artdeco-button--tertiary.artdeco-button--muted")))
            show_all_button.click()    
        except TimeoutException:
            print("Something Went Wrong Please Try Again")
        current_url = self.driver.current_url
        WebDriverWait(self.driver, 10).until(EC.url_changes(current_url))
        current_url = self.driver.current_url
        self.get_jobs_content(current_url,count=1)
        i = 0
        for count in range(2,10):
            i += 25
            link = f"{current_url}&start={i}" 
            try:
                self.get_jobs_content(link, count)
                # return job_url, job_title, company_name, location
            except Exception as e:
                break
            

    def get_jobs_content(self, links: str, count: int = None) -> None:  
        # job_urls = []
        # job_titles = []
        # company_names = []
        # locations = []

        print(f"Scraping Page {count}")
        if count == 1:
            pass
        else:
            self.driver.get(links) 
        #go to the url and scroll through this div so that every element is loaded
        # self.driver.execute_script("document.querySelector('.jobs-search-results-list').scrollTop = document.querySelector('.jobs-search-results-list').scrollHeight;")
        self.scroll_div("jobs-search-results-list")
        #get the source code 
        source_code = self.driver.page_source
        soup = BeautifulSoup(source_code,'html.parser')
        h1_element = soup.find('h1', class_='t-24 t-black t-normal text-align-center')
        # Check if the element exists and contains the specified text
        if h1_element and h1_element.text.strip() == "No matching jobs found.":
            print("Job Search Finished")
            self.close()
        containers = soup.find_all('div', class_='flex-grow-1 artdeco-entity-lockup__content ember-view')
        # Iterate over each container to extract information
        for container in containers:
            # Extract href and aria-label from the anchor tag within the container
            a_tag = container.find('a')
            job_url = a_tag['href']
            job_url = f"https://www.linkedin.com{job_url}"
            job_title = a_tag['aria-label']
            # Extract company name from the span within the container
            company_name = container.find('span', class_='job-card-container__primary-description').text.strip()
            # print("block 3")
            # Extract location from the li within the container
            location = container.find('li', class_='job-card-container__metadata-item').text.strip()
            if self.file_path is not None:
                self.save_job_data(self.file_path,job_url,job_title,company_name,location)
                print("Saving Data To File")
            else:
                print("---------------------------------------------------")
                print(f"{job_url}\n{job_title}\n{company_name}\n{location}")
                print("---------------------------------------------------")
