from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from write_csv import CSVWriter
import time

def extract_and_print_info(driver, writer):
    """Extracts and prints company details from the opened detail page, then writes to CSV."""
    try:
        h4_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h4"))
        )
        name = h4_element.text
        print(name)

        div_element = h4_element.find_element(By.XPATH, "following-sibling::div")
        div_text = div_element.text
        lines = div_text.split('\n')

        address = lines[0] if len(lines) > 0 else None
        city = lines[1] if len(lines) > 1 else None
        country = lines[2] if len(lines) > 2 else None

        vat = extract_element_text(div_element, ".//strong[contains(text(), 'VAT n°:')]", "following-sibling::text()")
        phone = extract_element_attribute(div_element, ".//a[starts-with(@href, 'tel:')]", "textContent")
        email = extract_element_attribute(div_element, ".//a[starts-with(@href, 'mailto:')]", "textContent")
        website = extract_element_attribute(div_element, ".//a[starts-with(@href, 'http')]", "href")

        # Extracting the license status
        license_status = extract_license_status(driver)

        print("Address:", address)
        print("City:", city)
        print("Country:", country)
        print("VAT:", vat)
        print("Phone:", phone)
        print("Email:", email)
        print("Website:", website)
        print("License Valid:", license_status)
        print("=" * 50)

        # Write to CSV
        writer.write_row([name, address, city, country, vat, phone, email, website, license_status])

    except Exception as e:
        print("An error occurred while extracting info:", e)

def extract_license_status(driver):
    """Extracts and returns the license status as a boolean."""
    try:
        # Locate the element that contains the license status
        status_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Licence status')]/following-sibling::div")
        status_text = status_element.text.strip()
        
        # Set the license status to True if 'Valid', otherwise False
        return True if "Valid" in status_text else False

    except Exception as e:
        print("Error while extracting license status:", e)
        return False  # Return False if the status is not found or there is an error

def extract_element_text(parent_element, xpath, following_xpath):
    """Extracts text content from an element."""
    try:
        element = parent_element.find_element(By.XPATH, xpath)
        return element.find_element(By.XPATH, following_xpath).get_attribute('textContent').strip()
    except:
        return None

def extract_element_attribute(parent_element, xpath, attribute):
    """Extracts an attribute value from an element."""
    try:
        element = parent_element.find_element(By.XPATH, xpath)
        return element.get_attribute(attribute).strip()
    except:
        return None

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def navigate_to_page(driver, page_number):
    """Navigates to a specific page by entering the number in the text field and pressing Enter."""
    try:
        # Locate the input field using wildcard for the changing ID
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'JumpToInputBottom_')]"))
        )

        # Scroll to make the input field visible if needed
        driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
        
        # Clear and enter the desired page number
        input_field.clear()
        input_field.send_keys(str(page_number))
        input_field.send_keys(Keys.RETURN)  # Simulate pressing Enter

        # Wait until the dropdown reflects the correct page number
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "select.cbResultSetNavigationDDown").get_attribute("value") == str(page_number)
        )
        
        print(f"✅ Successfully navigated to page {page_number}")
        return True

    except Exception as e:
        print(f"❌ Error navigating to page {page_number}: {e}")
        return False


def main():
    """Runs the full scraping process over all 2341 pages."""
    writer = CSVWriter()
    driver = webdriver.Chrome()
    driver.get("https://www.pefc.org/find-certified")
    driver.set_window_size(1100, 1080)  

    try:
        for page in range(2, 2341):  # 2341 iterations
            if page != 1:
                if not navigate_to_page(driver, page):
                    break

            print(f"\n🚀 Scraping page {page}/2341...\n")

            # WAIT for the new page to load fully
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cbResultSetTable"))
            )

            # FORCE REFRESH DOM ELEMENTS
            time.sleep(2)  # Ensures WebSockets have updated everything
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
            time.sleep(1)

            # RE-FETCH buttons after page change
            buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "button-round"))
            )

            original_window_handle = driver.current_window_handle

            for i in range(25): #25
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", buttons[i * 3])
                    time.sleep(0.5)

                    driver.execute_script("arguments[0].click();", buttons[i * 3])

                    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)

                    new_window_handle = [win for win in driver.window_handles if win != original_window_handle][0]
                    driver.switch_to.window(new_window_handle)

                    extract_and_print_info(driver, writer)

                    driver.close()
                    driver.switch_to.window(original_window_handle)

                    #  RE-FETCH buttons list after closing the pop-up
                    buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "button-round"))
                    )

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Error processing item {i+1}: {e}")

            time.sleep(1)

    finally:
        print("\n✅ Scraping complete.")
        driver.quit()


if __name__ == "__main__":
    main()
