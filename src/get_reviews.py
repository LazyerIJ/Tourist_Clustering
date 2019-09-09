import csv
import os.path
import urllib
from bs4 import BeautifulSoup
import time
import json

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait

base_url = "https://www.tripadvisor.com/"
comment_class_id = "partial_entry"
comment_page_idx = "data-page-number"
driver_path = "../utils/chromedriver"
json_file = "tourlist_url.json"
data_dir = "../data/"

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
            print(css_form)
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

#need to add dictionary to get more reviews
if __name__=='__main__':


    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print('[*]make dir: {}'.format(data_dir))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")

    scrawller = ScrawlTripAdvisor(chrome_options) 
    with open(json_file) as f:
        for data in json.load(f):
            title = data['title']
            url = data['url']
            fname = os.path.join(data_dir, '{}.csv'.format(title))
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
        scrawller.closedriver()
