from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
from typing import Union

class Linkedin:
    """
    Linkedin Class That Will Scrape Profiles To Get You Your Beautiful Data
    #### Arguments
    * Username ( str ) Username/Email of Linkedin
    * Password ( str ) Password Of Linkedin
    * headless ( str ) Set to True if you want to go headless

    """
    def __init__(self,username:str=None,password:str=None,
                 headless:str=None) -> None:

        self.username = username
        self.password = password
        self.headers_written = False
        chrome_options = Options()
        if headless is not None:
            chrome_options.add_argument("--headless")
        # if firefox is not installed it will automatically be installed. 
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()),options=chrome_options) 

    def login(self) -> None:

        """
        Logs The User In Does Not Take Any Arguments
        """
        self.driver.get("https://linkedin.com/login")
        login_form = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        username = self.driver.find_element(By.ID, "username") #finding user id
        password = self.driver.find_element(By.ID, "password") #finding password id
        username.send_keys(self.username) #entering email
        password.send_keys(self.password) #entering password
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(self.driver, 10).until(EC.title_contains("LinkedIn"))
        if self.driver.current_url != "https://www.linkedin.com/feed/":
            print("Entered Wrong Credientials Try Again")
    

    def scrape_profile(self,source_code) -> tuple:
        soup = BeautifulSoup(source_code, 'html.parser')
        name_tag = soup.find('h1', class_='text-heading-xlarge')
        name = name_tag.text.strip() if name_tag else ""

        skills_tag = soup.find('div', class_='text-body-medium')
        skills = skills_tag.text.strip() if skills_tag else ""

        # Find the location tag
        location_tag = soup.find('div', class_='OonsRDllhcAtPZoVkmvvEYTcRdBnpPCZAJ mt2')

        # Check if location_tag is not None before using find method on it
        if location_tag:
            location_span = location_tag.find('span', class_='text-body-small')
            # Check if location_span is not None before accessing its text
            if location_span:
                location_of_user = location_span.text.strip()
            else:
                location_of_user = "Location not found"  # Provide a default value if location_span is None
        else:
            location_of_user = "Location not found"  # Provide a default value if location_tag is None
        
        
        return name,skills,location_of_user 


    def contact_information(self,profile_link:str) -> list:
        contact_overlay = f"{profile_link}/overlay/contact-info/"
        self.driver.get(contact_overlay)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pv-profile-section__section-info')]")))
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'html.parser')
        all_links = soup.select('div.pv-profile-section__section-info a[href]')
        href_attributes = [link['href'] for link in all_links]

        return href_attributes 


    def get_profiles(self,links:Union [str,list]) -> tuple:
        """
        function that return profiles information
        #### Arguments
            * links ( str | list ) can pass links in a list or a single link to a profile
        #### Returns ( Tuple )
            * name
            * skills
            * location
            * profile_links 
        """ 
        if isinstance(links,list):
            for link in links:
                self.driver.get(link)
                src = self.driver.page_source
                name,skills,location = self.scrape_profile(src)
                profile_links = self.contact_information(link)

        else:
            self.driver.get(links)
            src = self.driver.page_source
            name,skills,location = self.scrape_profile(src)
            profile_links = self.contact_information(links)

        return name,skills,location,profile_links

    def save_data(self,filename:str=None,linkedin_url:str=None,
                  name:str=None,job_title:str=None,location:str=None) -> None:
        
        """
        Save Data Into CSV File Related To Profiles
        #### Arguments
        * filename ( str ) path or filename where the CSV is located
        * linkedin_url ( str )
        * name ( str ) profile name
        * job_title ( str )
        * location ( str ) location provided by the user in their profile
        """
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Profile Link', 'Name', 'Skills', 'Location']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not self.headers_written:
                writer.writeheader()
                self.headers_written = True
            writer.writerow({'Profile Links': linkedin_url, 'Name': name, 'Skills': job_title, 'Location': location})
        
                
    def close(self):
        self.driver.quit()
