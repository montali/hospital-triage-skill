from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from io import BytesIO
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


HOST_NAME = ''  # localhost
PORT_NUMBER = 8000
MINISTERO_SALUTE_ENCYCLOPEDIA = "http://www.salute.gov.it/portale/salute/p1_3.jsp?lingua=italiano&tema=Salute_A_Z"


class DataFetcher():
    def __init__(self):
        super().__init__()
        self.driver = webdriver.Firefox()
        self.driver.get(MINISTERO_SALUTE_ENCYCLOPEDIA)
        # The next script is used to accept the cookie policy
        self.driver.execute_script("setPrivacy();")

    def get_all(self):
        self.driver.get(MINISTERO_SALUTE_ENCYCLOPEDIA)
        fetched_data = {}
        aree = self.driver.find_elements_by_class_name("aree")
        for i in range(0, len(aree)):
            # This is kinda esoteric: the references on the DOM get changed on every refresh. So, we have to re-get them every time.
            aree = self.driver.find_elements_by_class_name("aree")
            aree[i].click()
            data = self.get_query()
            if data is not None:
                fetched_data[self.driver.title] = data
            self.driver.get(MINISTERO_SALUTE_ENCYCLOPEDIA)
        return fetched_data

    def get_query(self):
        try:
            tabs = self.driver.find_element_by_class_name("nav-tabs")
            children = tabs.find_elements_by_tag_name("li")
            informations = {}
            i = 1
            for information_tab in children:
                link = information_tab.find_element_by_tag_name("a")
                information_tab.click()
                text = ""
                tab_content = self.driver.find_element_by_id("tab-"+str(i))
                for paragraph in tab_content.find_elements_by_tag_name("p"):
                    text = text + str(paragraph.text)
                # Sometimes paragraphs end with a list. So, if the string ends with :, we cut off the last sentence.
                if len(text) > 0:
                    if text[-1] == ':':
                        text = text.rsplit('.', 1)[0]
                    informations[link.get_attribute(
                        "title")] = text
                i = i + 1
            return informations
        except NoSuchElementException:
            return None


if __name__ == '__main__':
    df = DataFetcher()
    data = df.get_all()
    with open("informations.json", "w") as info_file:
        json.dump(data, info_file)
    with open("locale/it-it/disease.entity", "w+") as entity_file:
        for name in data:
            entity_file.write(name+"\n")
