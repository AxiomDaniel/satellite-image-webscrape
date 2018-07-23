from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import cv2
import os
import numpy as np
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


def scrubAddress(address, saveImage=True):
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
    if saveImage is True:
        raw_img_name = "{}_raw.png".format(address.replace(" ", "_"))
        bound_img_name = "{}_bound.png".format(address.replace(" ", "_"))
    else:
        raw_img_name = "tmp_raw.png"
        bound_img_name = "tmp_bound.png"
    browser.get_screenshot_as_file(raw_img_name)
    # Clicks the Layer button
    locateAndClickButton(By.XPATH, '/html/body/div[2]/div[19]')
    time.sleep(1)
    browser.get_screenshot_as_file(bound_img_name)
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


def isolatePropertyBoundary(img_raw, img_bound):
    # img_raw: Coloured, raw satellite image
    # img_bound: Greyscale image of property boundaries
    # Output#1: An image of the property with its surroundings blacked out
    # Output#2: The land_area of the property

    # Thresholding simplifies the image by classifying each pixels to either black or white
    _, thresh1 = cv2.threshold(img_bound, 75, 255, cv2.THRESH_BINARY)

    # Dilate the boundaries so they are fatter and more visible
    # Kernel is like a slider in this case of 5 by 5 pixels.
    # Slide the slider around, if all pixels are white, we get white, otherwise black.
    kernel = np.ones((5, 5), np.uint8)
    image = cv2.dilate(thresh1, kernel, iterations=1)

    # Perform canny edge detection
    # 75 refers to the minVal, 76 refers to the maxVal
    # These values are used to decide which edges are genuine edges
    canny = cv2.Canny(image, 75, 76)

    # Close the boundaries - useful for closing small holes, dilation followed by erosion
    # This is so we don't have any open contours
    kernel = np.ones((2, 2), np.uint8)
    edged = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)

    # Find contours, returning the contours as a list
    _, contours, hierarchy = cv2.findContours(
        edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # Image data - height, width, value, centre y matrix value, centre x matrix value
    h, w, v = img_raw.shape
    iy = w / 2
    ix = h / 2

    # Initialise variables to isolate closest contour data
    closest_center_contour = None
    contour_min_distance = np.inf
    land_area = 0

    # Find the closest contour to the centre
    for c in contours:
        area = cv2.contourArea(c)
        # ie, sufficiently large and we are not capturing a tiny contour
        if cv2.contourArea(c) > 1000:
            M = cv2.moments(c)  # data for the centre of the contour
            # Ammended from Ali's original code, was cx
            cy = int(M['m10'] / M['m00'])
            # Ammended from Ali's original code, was cy
            cx = int(M['m01'] / M['m00'])
        else:
            cx, cy = 0, 0
        distance_from_center = ((cx - ix)**2 + (cy - iy)**2)**0.5
        if distance_from_center < contour_min_distance:
            contour_min_distance = distance_from_center
            closest_center_contour = c
            land_area = area
        else:
            pass

    # Make a mask and apply to original image
    img = img_raw.copy()  # original image - make a copy
    mask = np.zeros_like(img)
    cv2.drawContours(mask, [closest_center_contour], -1,
                     (255, 255, 255), -1)  # Draw filled contour in mask
    img_masked = np.zeros_like(img)  # create a black canvas for output
    # fill the canvas with image of mask-contour
    img_masked[mask == 255] = img[mask == 255]
    return img_masked, land_area


def calculateGardenPercentage(img_masked, land_area):
    # Function detects the gardens in the property and the proportion of greenery of total land land_area
    # img_masked: Image of the property with its surroundings blacked out
    # land_area: area of the property
    # Output: Ratio of greenery to total land area

    # Convert image to hsv, this is to get the colour range for green
    img_masked_hsv = cv2.cvtColor(img_masked, cv2.COLOR_BGR2HSV)

    # Define the colour range for green
    lower = np.array([16, 35, 0], dtype=np.uint8)
    upper = np.array([64, 255, 255], dtype=np.uint8)

    # Detect the green grass
    mask_grass = cv2.inRange(img_masked_hsv, lower, upper)

    # Remove noise by applying opening and closing
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(mask_grass, cv2.MORPH_OPEN, kernel)

    kernel = np.ones((9, 9), np.uint8)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    # Make a mask and apply it to the de-noised image
    mask_grass_denoised = closing.copy()

    # Create contours
    _, contours, heirarchy = cv2.findContours(
        mask_grass_denoised, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Draw contours
    cv2.drawContours(img_masked, contours, -1, (0, 255, 0), 1)

    # Initialise variable for grass area
    grass_area = 0

    # Calculate total area of grass
    for c in contours:
        patch_area = cv2.contourArea(c)
        grass_area += patch_area

    # Calculate percentage of grass on land
    grass_land_perc = grass_area / land_area * 100

    return grass_land_perc


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

    # Open C into
    output = open("address_with_grass_proportions.csv", 'w')
    writeCSV = csv.writer(output)
    # Open CSV file and read addresses to scrub
    with open(filename) as file:
        csv_iter = csv.reader(file)
        for row in csv_iter:
            # Index can be changed to suit the formatting of the CSV file
            scrubAddress(row[0], False)

            # Read screenshots into CV2 for analysis
            img_raw = cv2.imread("tmp_raw.png", 1)  # 1 for colour image
            img_bound = cv2.imread("tmp_bound.png", 0)  # 0 for greyscale image

            isolated_property_img, property_land_area = isolatePropertyBoundary(
                img_raw, img_bound)

            land_greenery_ratio = calculateGardenPercentage(
                isolated_property_img, property_land_area)

            writeCSV.writerow([row[0], land_greenery_ratio])
    browser.close()
    os.remove("tmp_raw.png")
    os.remove("tmp_bound.png")
    print("Scrubbing completed")
