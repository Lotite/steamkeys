import undetected_chromedriver as uc
import tempfile
import shutil
import os
from selenium.webdriver.chrome.webdriver import WebDriver

def create_driver(headless: bool = True) -> tuple[WebDriver, str]:
    options = uc.ChromeOptions()
    profile_dir = tempfile.mkdtemp(prefix="steamkeys-chrome-")

    if headless:
        options.add_argument("--headless=new")
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )
    options.add_argument(f"--user-data-dir={profile_dir}")

    driver = uc.Chrome(options=options, version_main=146)
    driver.set_page_load_timeout(45)
    
    return driver, profile_dir

def destroy_driver(driver: WebDriver | None, profile_dir: str | None):
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
        
        try:
            driver.service.stop()
        except Exception:
            pass

    if profile_dir and os.path.exists(profile_dir):
        shutil.rmtree(profile_dir, ignore_errors=True)
