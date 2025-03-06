from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def extract_and_print_info(driver):
    """Extracts and prints company details from the opened detail page."""
    try:
        h4_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h4"))
        )
        print(h4_element.text)

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

def click_next_page(driver, current_page):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-cb-name='JumpToNext']"))
        )

        if not next_button.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

        driver.execute_script("arguments[0].click();", next_button)  # JavaScript click to bypass issues

        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != driver.current_url or 
                      d.find_element(By.CSS_SELECTOR, "select.cbResultSetNavigationDDown").get_attribute("value") == str(current_page + 1)
        )
        return True

    except Exception as e:
        print(f"❌ Error while clicking 'Next': {e}")
        return False

def main():
    """Runs the full scraping process over all 2341 pages."""
    driver = webdriver.Chrome()
    driver.get("https://www.pefc.org/find-certified")

    try:
        for page in range(1, 6):  # 2341 iterations
            print(f"\n🚀 Scraping page {page}/2341...\n")

            buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "button-round"))
            )

            original_window_handle = driver.current_window_handle

            for i in range(5, 8): # 25
                try:
                    buttons[i * 3].click()  # Click the 'View details' button

                    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)

                    new_window_handle = [win for win in driver.window_handles if win != original_window_handle][0]
                    driver.switch_to.window(new_window_handle)

                    extract_and_print_info(driver)

                    driver.close()
                    driver.switch_to.window(original_window_handle)

                    buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "button-round"))
                    )

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Error processing item {i+1}: {e}")

            # Click on 'Next' and check if the next page exists
            if not click_next_page(driver, page):
                break  # Stop if there is no next page

    finally:
        print("\n✅ Scraping complete.")
        driver.quit()

if __name__ == "__main__":
    main()
