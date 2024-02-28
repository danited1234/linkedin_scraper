from bs4 import BeautifulSoup
import sys

from .profile_scarper import Linkedin

class MultiProfiles(Linkedin):
    """
    MultiProfiles Class That Will Scrape Profiles To Get You Your Beautiful Data
    #### Arguments
    * username ( str ) Username/Email of Linkedin
    * password ( str ) Password Of Linkedin
    * headless ( str ) Set to True if you want to go headless
    * file_path ( str ) file path of the csv file if you want to save results into a csv file

    """

    def __init__(self, username: str = None,
                  password: str = None,headless:str = None,
                  file_path: str = None) -> None:
        super().__init__(username, password,headless)
        self.file_path = file_path
    def find_profile_information(self,source_code):
        soup = BeautifulSoup(source_code,'html.parser')
        profile_containers = soup.find_all('div', class_='mb1')

    # Iterate over each profile container
        for profile in profile_containers:
            # Extract LinkedIn member name
            linkedin_member_name_span = profile.find('span', class_='entity-result__title-text').find('span', attrs={"aria-hidden": True})
            linkedin_member_name = linkedin_member_name_span.text.strip() if linkedin_member_name_span else ""

            # Extract LinkedIn URL
            linkedin_url = profile.find('a', class_='app-aware-link')['href']

            # Extract job title
            job_title = profile.find('div', class_='entity-result__primary-subtitle').text.strip()

            # Extract location
            location = profile.find('div', class_='entity-result__secondary-subtitle').text.strip()
            if self.file_path != None:
                self.save_data(self.file_path,linkedin_url,linkedin_member_name,job_title,location)
            else:
                print("---------------------------------------------------")
                print(f"{linkedin_member_name}\n{linkedin_url}\n{job_title}\n{location}")
                print("---------------------------------------------------")
        
    def get_mulitple_profiles(self,keyword:str):
        """
        main function that scrapes linkedin searches based on a keyword
        #### Arguments
            * keyword ( str ) keyword against you want to make a search

        """
        # profile_information_list = []
        profile_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL&sid=sjh"
        self.driver.get(profile_url)
        src = self.driver.page_source
        print("Fetching Data...")
        print("Scraping Page 1")
        self.find_profile_information(src)
        for i in range(2, 100):
            profile_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL&page={i}"
            self.driver.get(profile_url)
            src = self.driver.page_source
            soup = BeautifulSoup(src,'html.parser')
            no_results_element = soup.find('h2', class_='artdeco-empty-state__headline')
            if no_results_element:
                print("Scrapping Profiles Completed")
                sys.exit(1) #exit and close the script if there are no pages left to scrape
            print(f"Scrapping Page Number {i}")
            self.find_profile_information(src)

