from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import loginDetails
import time
import csv


def locateAndClickButton(findFn, searchPhrase, interval=0.5):
    # findFn: Function to locate element in a webpage.
    # Use By class in conjunction with function
    # For list of available function to use: http://selenium-python.readthedocs.io/locating-elements.html
    # searchPhrase: Query to be searched using findFn to locate element
    # interval: seconds(time) explicitly slows down button click to prevent random errors
    button = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((findFn, searchPhrase)))
    time.sleep(interval)
    button.click()


def locateAndFillText(findFn, searchPhrase, fillText):
    # findFn: Function to locate element in a webpage.
    # Use By class in conjunction with function
    # For list of available function to use: http://selenium-python.readthedocs.io/locating-elements.html
    # searchPhrase: Query to be searched using findFn to locate element
    # fillText: Text to be written into textbox
    textbox = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((findFn, searchPhrase)))
    time.sleep(0.5)
    textbox.clear()
    textbox.send_keys(fillText)


def zoomIn(iterations):
    # Clicks the zoom in button on MapBrowser
    for i in range(iterations):
        locateAndClickButton(
            By.XPATH, '/html/body/div[4]/div[1]/div[1]/div/div[8]/div/div/button[1]', 1)


def scrubAddress(address):
    # address: String format, spaces allowed. Include suburb to prevent ambiguous search result
    locateAndFillText(
        By.XPATH, '/html/body/div[4]/div[3]/form/input[2]', address)
    locateAndClickButton(
        By.XPATH, '/html/body/div[4]/div[3]/form/input[1]')
    zoomIn(2)
    # Make Green marker disappear
    locateAndClickButton(
        By.XPATH, '/html/body/div[4]/div[1]/div[1]/div/div[1]/div[4]/div[3]/div', 0)  # Clicks green marker
    locateAndClickButton(
        By.XPATH, '/html/body/div[4]/div[4]/div/div[2]/div/div[2]/div[4]', 0)  # Clicks 'Clear marker' button
    locateAndClickButton(
        By.XPATH, '/html/body/div[4]/div[4]/div/div[1]', 0)  # Closes Marker popup
    # Takes 2 screenshots, 1 as satellite, 1 as cadastre
    browser.get_screenshot_as_file(
        "{}_raw.png".format(address.replace(" ", "_")))
    # Clicks the Layer button
    locateAndClickButton(By.XPATH, '/html/body/div[2]/div[19]')
    time.sleep(1)
    browser.get_screenshot_as_file(
        "{}_bound.png".format(address.replace(" ", "_")))
    # Closes layer popup
    locateAndClickButton(By.XPATH, '/html/body/div[4]/div[4]/div/div[2]', 0)


def activatePropertyBoundary():
    # Function navigates MapBrowser to activate cadastre boundary area and decreases transparency
    # Only has to be run once per session
    locateAndClickButton(By.XPATH, '/html/body/div[2]/div[19]', 0)
    locateAndClickButton(
        By.XPATH, '/html/body/div[4]/div[4]/div/div[3]/div/div[4]/div/div[2]/ul/li[1]/div', 0)  # Clicks the Boundaries button
    # Property boundary button
    # locateAndClickButton(By.XPATH, '/html/body/div[4]/div[4]/div/div[3]/div/div[4]/div/div[2]/ul/li[1]/ul/li[7]/label', 0)
    # Cadastre boundary button
    locateAndClickButton(
        By.XPATH, '/html/body/div[4]/div[4]/div/div[3]/div/div[4]/div/div[2]/ul/li[1]/ul/li[1]/label', 0)
    sliderbutton = WebDriverWait(browser, 30).until(EC.presence_of_element_located(
        (By.XPATH, '/html/body/div[4]/div[4]/div/div[3]/div/div[4]/ul/li/div[3]/span/div/div/div')))  # Sets transparency slide to opaque
    actionControl = ActionChains(browser)
    actionControl.click_and_hold(sliderbutton).move_by_offset(
        200, 0).release().perform()
    # Closes layer popup
    locateAndClickButton(By.XPATH, '/html/body/div[4]/div[4]/div/div[2]')


if __name__ == "__main__":
    filename = "addresses.csv"
    # Initialize web browser
    browser = webdriver.Chrome()
    browser.fullscreen_window()
    browser.get("http://maps.au.nearmap.com/")

    # Enters username details and clicks next
    locateAndFillText(
        By.XPATH, '//input[@id="username"]', loginDetails.email_user)
    locateAndClickButton(By.XPATH, '//button[@id="btn-idp"]')
    # Sleep required for log in initialization. Can be reduced if running with good internet speed
    time.sleep(1)

    # Enters password and click "login" button
    locateAndFillText(
        By.XPATH, '//input[@id="password"]', loginDetails.password)
    locateAndClickButton(
        By.XPATH, '/html/body/div/div/div/form/fieldset/div[2]/button')
    time.sleep(2)

    # Clicks through introductory messages
    locateAndClickButton(By.XPATH, '/html/body/div[11]/div[2]/div', 0)
    for i in range(4):
        locateAndClickButton(By.XPATH, '/html/body/div[11]/div[2]/div[2]', 0)

    # Configure Layer to have property boundary
    activatePropertyBoundary()

    # Open CSV file and read addresses to scrub
    with open(filename) as file:
        csv_iter = csv.reader(file)
        for row in csv_iter:
            # Index can be changed to suit the formatting of the CSV file
            scrubAddress(row[0])

    browser.close()
    print("Scrubbing completed")
