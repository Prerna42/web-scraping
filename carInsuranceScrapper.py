from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Setup Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in background
#chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--disable-dev-shm-usage")

# Replace with your ChromeDriver path
driver_path = "path"  # Download from https://chromedriver.chromium.org/
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

def handle_cookie_popup():
    try:
        cookie_accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept All') or contains(text(), 'Accept')]"))
        )
        cookie_accept_button.click()
        print("Cookie popup accepted")
        time.sleep(2)
    except Exception as e:
        print(f"No cookie popup or error: {e}")

def get_car_insurance_data(reg_number):
    try:
        # Navigate to the page
        print("Navigating to confused.com")
        driver.get("https://www.confused.com/compare-car-insurance")
        time.sleep(2)
        
        # Handle cookie popup
        handle_cookie_popup()

        # Click "Search for car by make and model"
        print("Looking for 'Search for car by make and model' link")
        search_by_reg_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Search for car by make and model"))
        )
        search_by_reg_link.click()
        print("Clicked 'Search for car by make and model'")
        time.sleep(2)  # Wait for page transition

        # Try multiple locators for registration input
        print("Searching for registration input field")
        reg_input = None
        locators = [
            (By.XPATH, "//*[@id='registration-number-input']")
        ]
        
        for locator_type, locator_value in locators:
            try:
                reg_input = WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((locator_type, locator_value))
                )
                print(f"Found input using {locator_type}: {locator_value}")
                break
            except Exception as e:
                print(f"Failed to find input with {locator_type} '{locator_value}': {e}")

        if not reg_input:
            # Save page source for debugging
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise Exception("Could not locate registration input field. Page source saved to 'page_source.html'.")

        # Ensure input is interactable
        driver.execute_script("arguments[0].scrollIntoView(true);", reg_input)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='registration-number-input']")))
        
        # Enter registration number
        print(f"Attempting to enter registration: {reg_number}")
        reg_input.clear()
        reg_input.send_keys(reg_number)
        print(f"Successfully entered registration: {reg_number}")

        # Click the search/find button
        print("Clicking 'Find my car' button")
        find_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='find-vehicle-btn']"))
        )
        find_button.click()

        # Wait for results
        print("Waiting for results")
        time.sleep(5)

        # Extract car details (placeholders)
        car_details = {}
        try:
            make = driver.find_element(By.XPATH, "//*[@id='vehicle-summary']/div[1]").text
            model = driver.find_element(By.XPATH, "//*[contains(text(), 'Model')]//following-sibling::*").text
            year = driver.find_element(By.XPATH, "//*[contains(text(), 'Year')]//following-sibling::*").text
            car_details = {"Make": make}
            print(f"Extracted details: {car_details}")
        except Exception as e:
            print(f"Error extracting details: {e}")
            car_details = {"Registration": reg_number, "Error": "Details not found"}

        return car_details

    except Exception as e:
        print(f"Full error: {e}")
        return {"Registration": reg_number, "Error": str(e)}

def save_to_csv(data_list, filename="car_details.csv"):
    df = pd.DataFrame(data_list)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Example usage
if __name__ == "__main__":
    # Prompt user for registration number
    reg_number = input("Please enter the car registration number: ").strip()
    
    if not reg_number:
        print("No registration number provided. Exiting.")
    else:
        print(f"\nScraping data for {reg_number}")
        result = get_car_insurance_data(reg_number)
        save_to_csv([result])  # Save as a single-item list
    
    # Clean up
    driver.quit()
