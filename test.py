from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def extract_and_print_info(driver):
    try:
        # Find the <h4> element and print its text
        h4_element = driver.find_element(By.TAG_NAME, "h4")
        print(h4_element.text)

        # Find the div immediately following the <h4> element
        div_element = h4_element.find_element(By.XPATH, "following-sibling::div")
        div_text = div_element.text

        # Split the text by lines and extract the relevant parts
        lines = div_text.split('\n')
        address = lines[0] if len(lines) > 0 else None
        city = lines[1] if len(lines) > 1 else None
        country = lines[2] if len(lines) > 2 else None

        # Find other elements (VAT, Phone, Email, Website) and extract their values
        vat = extract_element_text(div_element, ".//strong[contains(text(), 'VAT n°:')]", "following-sibling::text()")
        phone = extract_element_attribute(div_element, ".//a[starts-with(@href, 'tel:')]", "textContent")
        email = extract_element_attribute(div_element, ".//a[starts-with(@href, 'mailto:')]", "textContent")
        website = extract_element_attribute(div_element, ".//a[starts-with(@href, 'http')]", "href")

        # Print the extracted information
        print("Address:", address)
        print("City:", city)
        print("Country:", country)
        print("VAT:", vat)
        print("Phone:", phone)
        print("Email:", email)
        print("Website:", website)

    except Exception as e:
        print("An error occurred:", e)

def extract_element_text(parent_element, xpath, following_xpath):
    try:
        element = parent_element.find_element(By.XPATH, xpath)
        text = element.find_element(By.XPATH, following_xpath).get_attribute('textContent').strip()
        return text if text else None
    except:
        return None

def extract_element_attribute(parent_element, xpath, attribute):
    try:
        element = parent_element.find_element(By.XPATH, xpath)
        attr_value = element.get_attribute(attribute)
        return attr_value.strip() if attr_value and attr_value.strip() else None
    except:
        return None



# Initialize Chrome WebDriver
driver = webdriver.Chrome()

# Open a webpage
driver.get("https://www.pefc.org/find-certified")

# Store the handle of the original window
original_window_handle = driver.current_window_handle

# Add a wait here if necessary to ensure the page has loaded and the buttons are present
time.sleep(20)  # Waits for 40 seconds, adjust as needed

# Find all buttons with class "button-round"
buttons = driver.find_elements(By.CLASS_NAME, "button-round")

# Click the first button (if it exists)
if len(buttons) > 0:
    buttons[0].click()

# Wait for the new page to load
time.sleep(10)  # Adjust the wait time as needed

# Switch to the new window/tab
windows = driver.window_handles
driver.switch_to.window(windows[-1])  # Assumes the new window is the last one opened
extract_and_print_info(driver)
driver.close()
driver.switch_to.window(original_window_handle)

time.sleep(5)

# ADD CLICK TO THE NEXT PAGE !!!!!!!!!!!!!!

# Wait for user input to quit
input("Press Enter to quit")

# Clean up: close the browser
driver.quit()
