from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker
from datetime import datetime
import time
import os
import random
import string
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import shutil
from pathlib import Path
import traceback

fake = Faker()

def random_delay():
    time.sleep(random.uniform(0.5, 2))

def human_like_typing(element, text):
    """Type text like a human"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(12))

def generate_username(full_name):
    base = full_name.lower().replace(' ', '')
    random_num = random.randint(100, 999)
    return f"{base}{random_num}"

def setup_browser():
    """Setup undetected Chrome browser"""
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--no-sandbox')
    
    browser = uc.Chrome(
        options=options,
        version_main=None,
        use_subprocess=True
    )
    return browser

def get_temp_mail(browser):
    """Get temporary email from temp-mail.io"""
    try:
        print("Opening temp-mail.io...")
        browser.get('https://temp-mail.io')
        wait = WebDriverWait(browser, 45)
        
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        time.sleep(5)
        
        selectors = [
            "input#mail",
            "input[type='text']",
            ".emailbox",
            "#email"
        ]
        
        email_element = None
        for selector in selectors:
            try:
                email_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if email_element:
                    break
            except:
                continue
                
        if not email_element:
            raise Exception("Could not locate email field")
            
        start_time = time.time()
        while time.time() - start_time < 30:
            temp_email = email_element.get_attribute("value")
            if temp_email:
                print(f"Generated email: {temp_email}")
                return temp_email
            time.sleep(2)
            
        raise Exception("Failed to generate temp email after 30 seconds")
            
    except Exception as e:
        print(f"Error getting temp email: {e}")
        print(f"Current URL: {browser.current_url}")
        print("Page source preview:", browser.page_source[:500])
        raise

def check_username_availability(browser, username):
    """Check if username is available on Instagram"""
    try:
        time.sleep(2)
        
        error_messages = [
            "//span[contains(text(), 'username already exists')]",
            "//span[text()='A user with that username already exists.']",
            "//span[contains(text(), 'not available')]"
        ]
        
        for xpath in error_messages:
            errors = browser.find_elements(By.XPATH, xpath)
            if errors:
                print(f"Username {username} is taken. Error: {errors[0].text}")
                return False
                
        print(f"Username {username} appears to be available")
        return True
        
    except Exception as e:
        print(f"Error checking username: {e}")
        return False

def get_suggested_username(browser):
    """Get Instagram's suggested username"""
    try:
        suggestion_button = browser.find_element(By.XPATH,
            "//button[contains(@class, '_acan') and contains(text(), 'suggestion')]"
        )
        suggestion_button.click()
        time.sleep(1)
        
        username_field = browser.find_element(By.NAME, "username")
        return username_field.get_attribute("value")
        
    except:
        return None

def fill_signup_form(browser, email, name, username, password):
    """Fill Instagram signup form with proper waits"""
    try:
        print("Creating Instagram tab...")
        browser.execute_script("window.open('https://www.instagram.com/accounts/emailsignup')")
        browser.switch_to.window(browser.window_handles[-1])
        
        wait = WebDriverWait(browser, 20)
        
        # Wait for page load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        print("Loading Instagram signup...")
        
        # Wait for form with multiple selectors
        form_selectors = [
            "form[id='emailForm']",
            "form[method='post']",
            "form._ab1y"
        ]
        
        form = None
        for selector in form_selectors:
            try:
                form = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if form:
                    break
            except:
                continue
                
        if not form:
            raise Exception("Could not find signup form")
            
        # Fill email with retry
        attempts = 0
        while attempts < 3:
            try:
                email_field = wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
                human_like_typing(email_field, email)
                time.sleep(2)
                break
            except:
                attempts += 1
                time.sleep(2)
                
        # Fill remaining fields
        name_field = browser.find_element(By.NAME, "fullName")
        human_like_typing(name_field, name)
        time.sleep(random.uniform(1, 2))
        
        username_field = browser.find_element(By.NAME, "username") 
        human_like_typing(username_field, username)
        time.sleep(2)
        
        if not check_username_availability(browser, username):
            new_username = generate_username(name)
            print(f"Trying new username: {new_username}")
            username_field.clear()
            human_like_typing(username_field, new_username)
            username = new_username
            
        password_field = browser.find_element(By.NAME, "password")
        human_like_typing(password_field, password)
        time.sleep(random.uniform(1, 2))
        
        # Click signup with retry
        attempts = 0
        while attempts < 3:
            try:
                signup_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[type='submit']")
                ))
                signup_button.click()
                print("Clicked signup button")
                time.sleep(3)
                return username
            except:
                attempts += 1
                time.sleep(2)
                
        raise Exception("Failed to click signup button")
        
    except Exception as e:
        print(f"Error in signup form: {e}")
        print(f"Current URL: {browser.current_url}")
        raise

def fill_birthdate_form(browser):
    """Fill birthdate form with proper waits and selectors"""
    wait = WebDriverWait(browser, 20)
    
    try:
        # Wait for signup form to complete
        time.sleep(5)
        print("Filling birthdate form...")
        
        # Wait for month selector to be visible
        month_select = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select[title='Month:']"))
        )
        # Ensure element is interactive
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select[title='Month:']")))
        Select(month_select).select_by_index(random.randint(1, 11))
        time.sleep(1)
        
        # Select day with wait
        day_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[title='Day:']"))
        )
        Select(day_select).select_by_index(random.randint(1, 27))
        time.sleep(1)
        
        # Select year with wait
        year_select = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[title='Year:']"))
        )
        select_year = Select(year_select)
        
        # Calculate valid year options (20+ years)
        current_year = datetime.now().year
        min_year = current_year - 40
        max_year = current_year - 20
        
        # Get valid year options
        valid_years = []
        for option in select_year.options:
            if option.text.isdigit():
                year = int(option.text)
                if min_year <= year <= max_year:
                    valid_years.append(option)
        
        if valid_years:
            random.choice(valid_years).click()
            time.sleep(2)
            
            # Click Next with updated selector
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
            )
            next_button.click()
            print("Clicked next button")
            time.sleep(3)
            
            return True
            
        raise Exception("No valid year options found")
        
    except Exception as e:
        print(f"Error filling birthdate: {e}")
        print(f"Current URL: {browser.current_url}")
        print("Page source preview:", browser.page_source[:1000])
        raise

def resend_verification_code(browser):
    """Click resend code button and wait for new code"""
    try:
        # Switch to Instagram tab
        browser.switch_to.window(browser.window_handles[1])
        
        # Wait for and click resend button
        wait = WebDriverWait(browser, 10)
        resend_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Resend Code')]"))
        )
        resend_button.click()
        print("Clicked resend code button")
        
        # Switch back to temp mail tab
        browser.switch_to.window(browser.window_handles[0])
        return True
    except Exception as e:
        print(f"Error resending code: {e}")
        return False

def wait_for_verification_code(browser, max_retries=3):
    """Wait for verification code with retries"""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} waiting for verification code...")
            wait = WebDriverWait(browser, 60)  # 1 minute timeout
            
            # Wait for Instagram email
            email = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Instagram')]"))
            )
            email.click()
            
            # Get code from subject
            subject = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-qa='message-subject']"))
            )
            code = ''.join(filter(str.isdigit, subject.text))[:6]
            
            if code:
                print(f"Found verification code: {code}")
                return code
                
        except Exception as e:
            print(f"Timeout waiting for code, attempt {attempt + 1}")
            if attempt < max_retries - 1:
                if not resend_verification_code(browser):
                    break
    
    return None

def complete_signup(browser, code):
    """Complete signup by entering verification code and clicking Next"""
    try:
        print(f"Completing signup with code: {code}")
        wait = WebDriverWait(browser, 10)
        
        # Enter verification code
        code_input = wait.until(
            EC.presence_of_element_located((By.NAME, "email_confirmation_code"))
        )
        human_like_typing(code_input, code)
        time.sleep(2)
        
        # Click Next button with updated selector
        next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(text(), 'Next')]"))
        )
        next_button.click()
        print("Clicked Next button")
        time.sleep(2)
        
        print("Verification completed")
        return True
        
    except Exception as e:
        print(f"Error completing signup: {e}")
        print(f"Current URL: {browser.current_url}")
        return False

def setup_photo_directories():
    """Create directories for profile and post photos"""
    base_dir = Path(__file__).parent
    profile_dir = base_dir / 'profile_photos'
    posts_dir = base_dir / 'post_photos'
    used_dir = base_dir / 'used_photos'
    
    for dir in [profile_dir, posts_dir, used_dir]:
        dir.mkdir(exist_ok=True)
    
    return profile_dir, posts_dir, used_dir

def get_random_unused_photo(source_dir, used_dir):
    """Get random unused photo from directory"""
    photos = list(Path(source_dir).glob('*.jpg')) + list(Path(source_dir).glob('*.png'))
    unused_photos = [p for p in photos if not (used_dir / p.name).exists()]
    
    if not unused_photos:
        print("No unused photos available")
        return None
        
    photo = random.choice(unused_photos)
    return photo

def upload_profile_photo(browser, profile_dir, used_dir):
    """Upload profile photo to Instagram"""
    try:
        print("Uploading profile photo...")
        
        # Get random unused profile photo
        photo = get_random_unused_photo(profile_dir, used_dir)
        if not photo:
            return False
            
        # Click profile edit button
        wait = WebDriverWait(browser, 10)
        edit_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit profile')]"))
        )
        edit_button.click()
        time.sleep(2)
        
        # Click change profile photo button
        change_photo_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@accept='image/jpeg,image/png']"))
        )
        change_photo_button.send_keys(str(photo.absolute()))
        time.sleep(5)
        
        # Save changes
        save_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
        )
        save_button.click()
        time.sleep(3)
        
        # Move used photo to used directory
        shutil.move(str(photo), str(used_dir / photo.name))
        print(f"Profile photo uploaded: {photo.name}")
        return True
        
    except Exception as e:
        print(f"Error uploading profile photo: {e}")
        return False

def save_credentials(email, password, name, username):
    """Save account credentials to file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filepath = "instagram_accounts.txt"
        
        with open(filepath, 'a') as f:
            f.write(f"\n=== Account Created: {timestamp} ===\n")
            f.write(f"Email: {email}\n")
            f.write(f"Password: {password}\n")  
            f.write(f"Full Name: {name}\n")
            f.write(f"Username: {username}\n")
            f.write("=" * 40 + "\n")
            
        print(f"Credentials saved to {filepath}")
        
    except Exception as e:
        print(f"Error saving credentials: {e}")

def create_account():
    browser = None
    try:
        browser = setup_browser()
        temp_email = get_temp_mail(browser)
        name = fake.name()
        username = generate_username(name)
        password = generate_password()
        
        if fill_signup_form(browser, temp_email, name, username, password):
            save_credentials(temp_email, password, name, username)
            
            if fill_birthdate_form(browser):
                print("Account created successfully!")
                return True
        return False
        
    except Exception as e:
        print(f"Error during account creation: {e}")
        traceback.print_exc()
    finally:
        if browser:
            browser.quit()

if __name__ == "__main__":
    create_account()