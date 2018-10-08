from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# We create an options object and add the headless property to it
options = webdriver.ChromeOptions()
options.add_argument('headless')

# We create a headless browser, this does not create a window
driver = webdriver.Chrome(options = options)

# Tests
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()
