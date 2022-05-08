import pandas as pd
import random
from matplotlib import pyplot as plt
from PIL import Image
import cv2
import requests
import os
from selenium.common.exceptions import ElementClickInterceptedException
import time as t
import io
from selenium import webdriver
from pathlib import Path
import tqdm
CUR_DIR = Path.cwd()
PARENT_DIR = CUR_DIR/"chromedriver.exe"

driver = webdriver.Chrome(PARENT_DIR)

def scrap_google_img(term):
    
    search_url="https://www.google.com/search?q={q}&tbm=isch&chips=q:{q},online_chips:container:XOU1cx6BhF8%3D&client=firefox-b-d&hl=fr&sa=X&ved=2ahUKEwjY09LyiMT3AhVN8xQKHbYZD2MQ4lYoAnoECAEQIQ&biw=1519&bih=754" 

    driver.get(search_url.format(q=term))
    for _ in range(10):
        try:
            driver.execute_async_script("window.scrollTo(0, document.body.scrollHeight);}, 2000);")
            t.sleep(0.3)
        except Exception as e:
            print("Error: ",e)
            continue
    imgResults = driver.find_elements_by_xpath("//img[contains(@class,'rg_i Q4LuWd')]")
    return imgResults

#Click on each Image to extract its corresponding link to download
def data_img_generator(term):
    imgResults = scrap_google_img(term)
    img_urls = set()
    for i in  range(0,len(imgResults)):
        img=imgResults[i]
        try:
            img.click()
            t.sleep(4)
            actual_images = driver.find_elements_by_css_selector('img.Q4LuWd')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'https' in actual_image.get_attribute('src'):
                    print(actual_image.get_attribute('src'))
                    img_urls.add(actual_image.get_attribute('src'))
    
        except Exception  as err:
            print(err)
    return img_urls

def download_googleImgs(path:Path,term:str) :
    path_sepc = path/"-".join(term.split(" "))
    path_sepc.mkdir(exist_ok=True)
    list_urls = data_img_generator(term)
    files_list = [f for f in path_sepc.iterdir() if (f.is_file()) & (str(f).endswith(".jpg"))]
    print(len(files_list))
    if len(files_list) != 0:
        max_number_file = int(str(files_list.sort()[-1]).split("-")[-1].split(".")[0])+1
    else:
        max_number_file= 1
    for i, url in enumerate(list_urls):
        print(url)
        file_name = f"{term}-{i+max_number_file}.jpg"    
        try:
            image_content = requests.get(url).content
    
        except Exception as e:
            print(f"ERROR - COULD NOT DOWNLOAD {url} - {e}")
    
        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            
            file_path = path_sepc/file_name
            
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=100)
            print(f"SAVED - {url} - AT: {file_path}")
        except Exception as e:
            print(f"ERROR - COULD NOT SAVE {url} - {e}")

def main(list_terms, path_parent):
    for term in list_terms:
        download_googleImgs(path_parent,term)
        t.sleep(300)

if __name__ == "__main__":


    dataSets = CUR_DIR/"datasets"
    dataSets.mkdir(exist_ok=True)

    list_search = ["dirty plastic cutlery"
               ]
    
    main(list_search, dataSets)


