import os, subprocess, argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from config import *
from utils import *

download_dir_firefox = download_dir.replace('/', '\\')

options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", download_dir_firefox)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
options.add_argument("-headless")
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

login(driver=driver, url=total_url, USERNAME=USERNAME, PASSWORD=PASSWORD, By=By) # Логинимся и переходим на страницу со всеми конфигурациями
configs_page(driver=driver, By=By) # Выбираем и переходим на страницу выбранной конфигурации
version_page(driver=driver, By=By) # Выбираем нужную версию конфигурации и переходим ссылке
distribution_page(driver=driver, By=By) # Выбираем нужный дистрибутив скачивания
download_page(driver=driver, By=By) # Выбираем ссылку для скачивания
download_status(driver=driver, download_dir=download_dir)
unarchive_efd(download_dir=download_dir) # Разархивируем efd файл
load_config(download_dir, rac_path, IB_USERNAME, IB_PASSWORD, cluster, ib_name)
