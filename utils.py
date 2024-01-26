import os, time, re, zipfile, fnmatch, subprocess
from efd_extract import extract

def config_menu(configs: dict):
    for index, name in enumerate(configs.keys()):
        print(index, ": ", name)
    choice = input("Введите конфигурацию для скачивания: ")
    return configs[choice]

def download_menu(downloads: list):
    for index, name in enumerate(downloads):
        print(index, ": ", name)
    number = int(input("Введите номер скачивания: "))
    return downloads[number]

def login(driver, url, USERNAME, PASSWORD, By):
    driver.get(url)
    try:
        username_form = driver.find_element(By.ID, "username")
        password_form = driver.find_element(By.ID, "password")
        login_btn_form = driver.find_element(By.ID, "loginButton")
        username_form.send_keys(USERNAME)
        password_form.send_keys(PASSWORD)
        login_btn_form.click()
    except Exception as error:
        print(error)

def configs_page(driver, By):
    try:
        configs_list = driver.find_elements(By.XPATH, "//td[@class='nameColumn']/a[1]")
        for config_link in configs_list:
            if config_link.text == "":
                continue
            print(config_link.text)
        config_name = input("Введите имя конфигурации: ")
        config_url = driver.find_element(By.LINK_TEXT, config_name)
        config_url.click()
    except Exception as error:
        print("Ошибка при выборе конфигурации")

def version_page(driver, By):
    try:
        versions = driver.find_elements(By.XPATH, "//td[@class='versionColumn']/a[1]")
        versions_list = []
        for index, version in enumerate(versions):
            versions_list.append(version.text)
            print(index, ": ", version.text)

        choice = int(input("Введите номер версии: "))
        for version in versions:
            if  version.text == versions_list[choice]:
                version.click()
    except Exception as error:
        print(error)

def distribution_page(driver, By):
    try:
        distributions_list = driver.find_elements(By.XPATH, "//div[@class='with-file-info-tooltip']/a[1]")
        for distr_link in distributions_list:
            print(distr_link.text)
        distr_name = input("Введите имя дистрибутива: ")
        distr_url = driver.find_element(By.LINK_TEXT, distr_name)
        distr_url.click()
    except Exception as error:
        print("Ошибка при выборе дистрибутива")
    try:
        input_form = driver.find_element(By.ID, 'input-otp')
        continue_btn = driver.find_element(By.ID, 'btn-otp-continue')
        sms_code = input("Введите смс код: ")
        input_form.send_keys(sms_code)
        continue_btn.click()
    except Exception as error:
        print("Скачивание без смс")

def download_page(driver, By):
    try:
        download_links = driver.find_elements(By.XPATH, "//div[@class='downloadDist']/a")
        download_list = []
        for index, link in enumerate(download_links):
            download_list.append(link.text)
            print(index, ": ", link.text)

        choice = int(input("Введите номер ссылки: "))
        for link in download_links:
            if  link.text == download_list[choice]:
                link.click()
    except Exception as error:
        print(error)

def download_status(driver, download_dir):
    url = driver.current_url
    filename = re.split('5c', url)[2]
    download_file_path = download_dir + filename

    while not os.path.exists(download_file_path): # Цикл который ждет пока файл не скачается
        time.sleep(1)

    while not zipfile.is_zipfile(download_file_path): # Цикл который ждет пока файл не будет zip
        time.sleep(1)

    print("Progress: Файл успешно скачался!")
    unzip_efd_file(path_to_file=download_file_path, output_path=download_dir)
    os.remove(path=download_file_path)

def get_download_progress(driver):
    try:
        driver.get('chrome://downloads/')
        progress = driver.execute_script('''
        var tag = document.querySelector('downloads-manager').shadowRoot;
        var intag = tag.querySelector('downloads-item').shadowRoot;
        var progress_tag = intag.getElementById('progress');
        var progress = null;
        if(progress_tag) {
            progress = progress_tag.value;
        }
        return progress;
        ''')
        return progress
    except Exception as error:
        print('*')
    
def unzip_efd_file(path_to_file: str, output_path: str):
    with zipfile.ZipFile(path_to_file, 'r') as zip_ref:
        zip_ref.extract("1cv8.efd", output_path)

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def parse_mft(mft_path):
    src = dict()

    with open(mft_path, "r", encoding="utf-8") as f:
        content = list(filter(None, f.read().split('\n')))
    
    for index, line in enumerate(content):
        splitted = line.split('=')
        if splitted[0] == 'Catalog':
            src[splitted[1]] = content[index + 2].split('=')[1]

    return src

def unarchive_efd(download_dir):
    efd_path = download_dir + "1cv8.efd"
    if extract(efd_path, download_dir):
        print("efd файл распакован")
        os.remove(path=efd_path)

def check_mft(download_dir):
    mft_path = find("*.mft", download_dir)
    existing_configs = list()

    if  not os.path.isfile(mft_path[0]): 
        return

    configs = parse_mft(mft_path[0])
    for key in configs.keys():
        if find(configs[key], download_dir):
            existing_configs.append("{}: {}".format(key, configs[key]))
    return existing_configs

def load_config(download_dir, rac_path, IB_USERNAME, IB_PASSWORD, cluster, ib_name):
    config_files = check_mft(download_dir)
    selected_config = ""
    for index, config in enumerate(config_files):
        print("{}) {}".format(index, config))

    choice = int(input("Введите номер файла конфигурации который хотите загрузить в базу : "))
    for config in config_files:
        if config == config_files[choice]:
            selected_config = config.split(' : ')[1]

    # if selected_config:
    #     load_cf_cmd = "{} CONFIG /S{}\\{} /LoadCfg {}".format(rac_path, cluster, ib_name, selected_config)
    #     update_db_cmd =  "{} CONFIG /S{}\\{} /UpdateDBCfg".format(rac_path, cluster, ib_name)
    #     subprocess.call(load_cf_cmd)
    #     subprocess.call(update_db_cmd)



