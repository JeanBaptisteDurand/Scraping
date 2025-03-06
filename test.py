from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def extract_and_print_info(driver):
    """Extrait et affiche les informations de l'entreprise sur la page de détails."""
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

        print("Address:", address)
        print("City:", city)
        print("Country:", country)
        print("VAT:", vat)
        print("Phone:", phone)
        print("Email:", email)
        print("Website:", website)
        print("="*50)

    except Exception as e:
        print("An error occurred while extracting info:", e)

def extract_element_text(parent_element, xpath, following_xpath):
    """Extrait le texte d'un élément en fonction de son XPath."""
    try:
        element = parent_element.find_element(By.XPATH, xpath)
        return element.find_element(By.XPATH, following_xpath).get_attribute('textContent').strip()
    except:
        return None

def extract_element_attribute(parent_element, xpath, attribute):
    """Extrait un attribut d'un élément en fonction de son XPath."""
    try:
        element = parent_element.find_element(By.XPATH, xpath)
        return element.get_attribute(attribute).strip()
    except:
        return None

def main():
    """Exécute le script principal pour récupérer les informations des 25 premiers résultats."""
    driver = webdriver.Chrome()
    driver.get("https://www.pefc.org/find-certified")

    try:
        buttons = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "button-round"))
        )

        original_window_handle = driver.current_window_handle

        for i in range(25):
            try:
                buttons[i * 3].click()

                # Attendre que la nouvelle fenêtre apparaisse
                WebDriverWait(driver, 20).until(lambda d: len(d.window_handles) > 1)

                new_window_handle = [win for win in driver.window_handles if win != original_window_handle][0]
                driver.switch_to.window(new_window_handle)

                # Extraire et afficher les infos
                extract_and_print_info(driver)

                # ✅ Revenir sur l'onglet principal avant de fermer
                driver.close()
                driver.switch_to.window(original_window_handle)

                # ✅ Recharge la liste des boutons pour éviter les références obsolètes
                buttons = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "button-round"))
                )

            except TimeoutException:
                print(f"Timeout sur l'élément {i+1}, passage au suivant.")
            except Exception as e:
                print(f"Erreur lors de l'extraction du {i+1}ème élément:", e)

    finally:
        print("Done")
        driver.quit()

if __name__ == "__main__":
    main()
