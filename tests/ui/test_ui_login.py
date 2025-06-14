# tests/ui/test_ui_login.py

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="module")
def driver():
    """Sets up headless Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

def test_login_page_loads(driver):
    """Test that the login page loads and has the login form."""
    driver.get("http://localhost:5000/login")
    time.sleep(1)

    assert "Login" in driver.title or "login" in driver.page_source
    assert driver.find_element(By.NAME, "email")
    assert driver.find_element(By.NAME, "password")

def test_valid_login(driver):
    """Test logging in after registering a user."""
    # Register first
    driver.get("http://localhost:5000/register")
    time.sleep(1)
    driver.find_element(By.NAME, "email").send_keys("uiuser@example.com")
    driver.find_element(By.NAME, "password").send_keys("Secure123!")
    driver.find_element(By.XPATH, '//button[contains(text(), "Register")]').click()
    time.sleep(1)

    # Then log in
    driver.get("http://localhost:5000/login")
    driver.find_element(By.NAME, "email").send_keys("uiuser@example.com")
    driver.find_element(By.NAME, "password").send_keys("Secure123!")
    driver.find_element(By.XPATH, '//button[contains(text(), "Login")]').click()
    time.sleep(2)

    assert "dashboard" in driver.page_source.lower() or "logout" in driver.page_source.lower()
