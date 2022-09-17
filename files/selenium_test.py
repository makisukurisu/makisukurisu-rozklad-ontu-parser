from selenium import webdriver
import time

s = time.time()
driver = webdriver.Firefox()
driver.get('https://rozklad.ontu.edu.ua/guest_n.php')
notbot = None
while True:
    if notbot:
        break
    cookies = driver.get_cookies()
    if cookies:
        for cookie in cookies:
            if cookie['name'] == 'notbot':
                notbot = cookie['value']
e = time.time()
print('Spent:', e-s)
print(notbot)