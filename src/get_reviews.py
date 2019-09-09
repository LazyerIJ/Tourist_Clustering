import csv
import os.path
import urllib
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait

base_url = "https://www.tripadvisor.com/"
comment_class_id = "partial_entry"
comment_page_idx = "data-page-number"
driver_path = "../utils/chromedriver"


def write_csv(fname, total_comment):
    file_exists = os.path.isfile(fname)
    with open(fname, 'a') as csvfile:
        headers = ['Comment']
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        for comment in total_comment:
            writer.writerow({'Comment': comment})


class ScrawlTripAdvisor():

    def __init__(self, chrome_options, implicitly=3, driver_path=driver_path):
        self.chrome = webdriver.Chrome(driver_path,
                                       chrome_options=chrome_options)
        self.implicitly = implicitly

    def getdriver(self, url, base_url=base_url):
        self.chrome.get(base_url+url)
        self.chrome.implicitly_wait(self.implicitly)

    def scrawl_comment(self, fname, max_idx, sleep_time=0.5, write_iter=50):

        flag = False
        total_comment = []

        for step in range(1, max_idx+1):

            print('Read comment {} page'.format(step))

            if(flag):
                css_form = "a[{}='{}']".format(comment_page_idx, step)
                self.chrome.find_element_by_css_selector(css_form).click()
                self.chrome.implicitly_wait(self.implicitly)
            flag = True

            # unroll comment
            css_form = "p[class='{}']>span".format(comment_class_id)
            more = self.chrome.find_element_by_css_selector(css_form).click()
            self.chrome.implicitly_wait(self.implicitly)

            # get html
            elem = self.chrome.find_element_by_xpath("//*")
            source_code = elem.get_attribute("outerHTML")
            html = BeautifulSoup(source_code, "html.parser")

            for comment in html.findAll("p", {"class": comment_class_id}):
                total_comment.append(comment.text)
            time.sleep(sleep_time)

            if step%write_iter == 0 or step == max_idx:
                print('[*]Write csv  ~ {})'.format(step))
                write_csv(fname, total_comment)
                total_comment = []

    def closedriver(self):
        self.chrome.quit()


if __name__=='__main__':

    #url_city = "Attraction_Review-g187791-d192285-Reviews-or{}-Colosseum-Rome_Lazio.html" 
    #url_title = "Collosseum"
    #url_city = "Attraction_Review-g187791-d246072-Reviews-Catacombe_di_Priscilla-Rome_Lazio.html"
    #url_title = "Catacombe_di_Priscilla"
    #url_city = "Attraction_Review-g187791-d243032-Reviews-Catacombe_di_Santa_Domitilla-Rome_Lazio.html"
    #url_title = "Catacombe_di_Santa_Domitilla"
    #url_city = "Attraction_Review-g187791-d2154770-Reviews-Roman_Forum-Rome_Lazio.html"
    #url_title = "Roman_Forum"

    #url_city = "Attraction_Review-g187791-d190131-Reviews-Trevi_Fountain-Rome_Lazio.html"
    #url_title = "Trevi_Fountain"

    #url_city = "Attraction_Review-g187791-d197714-Reviews-Pantheon-Rome_Lazio.html"
    #url_title= "Pantheon"

    url_city = "Attraction_Review-g294265-d1837767-Reviews-Marina_Bay_Sands_Skypark-Singapore.html"
    url_title = "marina_bay_sands"


    city_list = [url_city]
    title_list = [url_title]

    file_type = ".csv"
    data_dir = "../data/"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")

    scrawller = ScrawlTripAdvisor(chrome_options) 
    
    for url, title in zip(city_list, title_list):
        fname = data_dir+title+file_type

        if os.path.isfile(fname):
            print('[*]File Already Exist - {}]'.format(fname))
        else:
            print('[*]Scrawlling City - [{}]'.format(title))
            print('[*]File name - {}'.format(fname))
            max_idx = 25
            scrawller.getdriver(url)
            scrawller.scrawl_comment(fname,
                                     write_iter=10,
                                     max_idx=max_idx)

            print('[*]Success to Scrapy - [{}]'.format(fname))
            #scrawller.closedriver()

    scrawller.closedriver()
