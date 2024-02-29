from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv


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
        if headless != None:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):

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
    

    def scrape_profile(self,source_code):
        soup = BeautifulSoup(source_code, 'html.parser')
        name_tag = soup.find('h1', class_='text-heading-xlarge')
        name = name_tag.text.strip() if name_tag else ""

        skills_tag = soup.find('div', class_='text-body-medium')
        skills = skills_tag.text.strip() if skills_tag else ""

        # Find the location tag
        location_tag = soup.find('div', class_='cEkkBrtZIPVkPONKQgkTtPnzKntznvYP mt2')

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


    def contact_information(self,profile_link:str):
        contact_overlay = f"{profile_link}/overlay/contact-info/"
        self.driver.get(contact_overlay)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pv-profile-section__section-info')]")))
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'html.parser')
        all_links = soup.select('div.pv-profile-section__section-info a[href]')
        href_attributes = [link['href'] for link in all_links]

        return href_attributes 


    def get_profiles(self,links:any):
        """
        function that return profiles information
        #### Arguments
            * links ( any ) can pass links in a list or a single link to a profile
        """
        if type(links) == list:
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
                  name:str=None,job_title:str=None,location:str=None):
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Profile Link', 'Name', 'Skills', 'Location']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not self.headers_written:
                writer.writeheader()
                self.headers_written = True
            writer.writerow({'Profile Links': linkedin_url, 'Name': name, 'Skills': job_title, 'Location': location})
    

    def close(self):
        self.driver.quit()