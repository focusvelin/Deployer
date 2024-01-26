import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

download_dir = config["VARS"]["download_dir"]
total_url = config["VARS"]["total_url"]
USERNAME = config["VARS"]["USERNAME"]
PASSWORD = config["VARS"]["PASSWORD"]

rac_path = config["VARS"]["rac_path"]
cluster = config["VARS"]["cluster"]
ib_name = config["VARS"]["ib_name"]
IB_USERNAME = config["VARS"]["ib_username"]
IB_PASSWORD = config["VARS"]["ib_password"]
