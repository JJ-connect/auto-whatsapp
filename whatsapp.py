from __future__ import annotations
import os
import platform
import random
import shutil
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import time
from PIL import Image
from datetime import datetime

class FileInfo:
    def __init__(self, file_location: str, date_created: str, file_name: str) -> None:
        self.file_location = file_location
        self.date_created = date_created
        self.file_name = file_name

NUMBER_OF_PHOTOGRAPHS = 2
PHOTO_COLLECT_LOCATION = r"/path/to/photos/for/sending"
PHOTO_DEPOSIT_LOCATION = r"/path/to/photos/already/sent"
GROUP_TO_SEND_TO = "Name of WhatsApp contact/group" # Plaintext name as it appears on WhatsApp
USER_DATA_DIRECTORY = r"Memory/WebWhatsAppBot"      # This prevents you having to scan the QR code every time. It gets written to on first running.


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    
    if platform.system() == 'Windows':
        timestamp = os.path.getctime(path_to_file)
        return datetime.fromtimestamp(timestamp).strftime("%H:%M, %d %B %Y")
    else:
        stat = os.stat(path_to_file)
        try:
            timestamp = stat.st_birthtime
            return datetime.fromtimestamp(timestamp).strftime("%H:%M, %d %B %Y")
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            timestamp = stat.st_mtime
            return datetime.fromtimestamp(timestamp).strftime("%H:%M, %d %B %Y")

def collect_photograph(collection_filepath: str) -> FileInfo:
    file_name: str = random.choice(os.listdir(collection_filepath))
    file_location: str = os.path.join(collection_filepath, file_name)
    date_created: str = creation_date(file_location)
    return FileInfo(file_location, date_created, file_name)

def setup_selenium(group_to_receive: str, user_data_directory: str) -> WebDriver:
    if platform.system() == 'Windows':
        from webdriver_manager.chrome import ChromeDriverManager
        chrome_options: Options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("user-data-dir=" + user_data_directory)
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    else:
        chrome_options: Options = Options()
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("user-data-dir=" + user_data_directory)
        chrome_options.add_argument("--headless")
        driver_path="/usr/lib/chromium-browser/chromedriver"
        driver = webdriver.Chrome(service=Service(driver_path), chrome_options=chrome_options)

    driver.get("https://web.whatsapp.com")
    print("Scan QR Code, And then Enter")
    selected_contact_xpath = "//span[@title='" + group_to_receive + "']"
    WebDriverWait(driver, 300).until(ec.element_to_be_clickable((By.XPATH, selected_contact_xpath)))
    print("Logged In")

    selected_contact = driver.find_element("xpath", selected_contact_xpath)

    parent1 = selected_contact.find_element("xpath", "./..")
    parent2 = parent1.find_element("xpath", "./..")
    parent3 = parent2.find_element("xpath", "./..")
    parent4 = parent3.find_element("xpath", "./..")
    parent5 = parent4.find_element("xpath", "./..")
    print(parent5.get_attribute("attribute name"))
    print(parent5)
    parent5.click()
    print("Opened contact")
    
    return driver
    
def move_file_out(photograph: FileInfo, photo_deposition_location: str):
    shutil.move(photograph.file_location, photo_deposition_location)

def send_photos(number_of_photographs: int, group_to_receive: str, photo_deposition_location: str, photo_collection_location: str, user_data_directory: str):
    print("**** beginning script")
    print("**** setting up Selenium Web Driver")
    driver = setup_selenium(group_to_receive, user_data_directory)

    print("**** Beginning loop over number of photographs")
    for _ in range(number_of_photographs):
        
        print(f"**** Attempting to send photo number {_ + 1}")
        print(f"**** Beginning photo collection from {photo_collection_location}")
        photograph: FileInfo = collect_photograph(photo_collection_location)
        print(f"**** found photograph at {photograph.file_location}")

        print(f"**** Waiting to see 'Type a message")
        inp_xpath = '//div[@title="Type a message"]'
        WebDriverWait(driver, 300).until(ec.element_to_be_clickable((By.XPATH, inp_xpath)))
        print(f"**** Input box exists!")
        input_box = driver.find_element("xpath",inp_xpath)
        print("found input box")

        print(f"**** Pasting photograph creation time")
        input_box.send_keys(photograph.date_created)

        print(f"**** Waiting to see a send button on the text")
        send_button_button_xpath = '//button[@aria-label="Send"]'
        WebDriverWait(driver, 300).until(ec.element_to_be_clickable((By.XPATH, send_button_button_xpath)))
        print(f"**** Initial send button exists!")

        attach_button_xpath = '//div[@aria-label="Attach"]'
        attach_paperclip = driver.find_element("xpath", attach_button_xpath)
        attach_paperclip.click()

        attach_photo_xpath = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
        attach_photo = driver.find_element("xpath", attach_photo_xpath)
        attach_photo.send_keys(photograph.file_location)

        try:
            print(f"**** Waiting to see a send div for the image")
            send_button_div_xpath = '//div[@aria-label="Send"]'
            WebDriverWait(driver, 300).until(ec.element_to_be_clickable((By.XPATH, send_button_div_xpath)))
            print(f"**** Green circle send button exists!")
            send_button = driver.find_element("xpath",send_button_div_xpath)
            send_button.click()
            print("Clicked send")

            print(f"**** Waiting 5s to send!")
            time.sleep(5)
            print(f"sent photo number {_ + 1}")
            move_file_out(photograph, photo_deposition_location)
        except TimeoutException:
            print("**** Write failed")
            print("**** Moving to failed folder")
            move_file_out(photograph, os.path.join(photo_deposition_location, "FailedToSend", photograph.file_name))

            send_button = driver.find_element("xpath",send_button_button_xpath)
            send_button.click()

    driver.quit()
    print("now quit")

if __name__ == "__main__":
    send_photos(NUMBER_OF_PHOTOGRAPHS, GROUP_TO_SEND_TO, PHOTO_DEPOSIT_LOCATION, PHOTO_COLLECT_LOCATION, USER_DATA_DIRECTORY)
