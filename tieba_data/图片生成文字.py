import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json  # 引入json模块
import os
import hashlib
import random
import time
from playwright.sync_api import sync_playwright
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Set up a rotating User-Agent list to avoid getting blocked
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Pre-load the BLIP model and processor from local directory to avoid downloading
try:
    blip_model = BlipForConditionalGeneration.from_pretrained("./blip/")
    blip_processor = BlipProcessor.from_pretrained("./blip/")
except Exception as e:
    print(f"Failed to load BLIP model. Error: {e}")
    blip_model = None
    blip_processor = None

# Fetch posts from Tieba using Playwright
def fetch_tieba_posts(keyword, page_limit=1):
    base_url = f"https://tieba.baidu.com/f?kw={keyword}&ie=utf-8"
    posts = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        for page_number in range(page_limit):
            page_url = f"{base_url}&pn={page_number * 50}"
            try:
                page.goto(page_url)
                time.sleep(random.uniform(2, 5))  # Random delay to avoid getting blocked
                threads = page.locator('div.threadlist_title a.j_th_tit')

                for i in range(threads.count()):
                    title = threads.nth(i).text_content().strip()
                    link = urljoin("https://tieba.baidu.com", threads.nth(i).get_attribute('href'))
                    posts.append({
                        'title': title,
                        'link': link
                    })
            except Exception as e:
                print(f"Failed to retrieve page {page_number + 1}. Error: {e}")
                continue

        browser.close()
    return posts

# Fetch images from a specific post using Requests
def fetch_post_images(post_url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(post_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to retrieve post {post_url}. Error: {e}")
        time.sleep(random.uniform(1, 3))  # Random delay to avoid getting blocked
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img', {'class': 'BDE_Image'})
    image_urls = [img['src'] for img in images if img.get('src')]
    return image_urls

# Download an image from a URL and save it to a folder
def download_image(image_url, folder_path):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to download image {image_url}. Error: {e}")
        return None

    # Use hash to generate a unique filename
    hash_object = hashlib.md5(image_url.encode())
    file_extension = os.path.splitext(image_url)[1].split('?')[0]  # Get file extension
    filename = f"{hash_object.hexdigest()}{file_extension}"
    file_path = os.path.join(folder_path, filename)

    try:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_path
    except IOError as e:
        print(f"Failed to save image {file_path}. Error: {e}")
        return None

# Generate image description using BLIP
def generate_image_description(image_path):
    if blip_model is None or blip_processor is None:
        print("BLIP model is not loaded. Skipping description generation.")
        return None

    try:
        image = Image.open(image_path)
        inputs = blip_processor(images=image, return_tensors="pt")
        out = blip_model.generate(**inputs)
        description = blip_processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        print(f"Failed to generate description for image {image_path}. Error: {e}")
        return None

# Generate descriptions for all images in the images folder and update JSON data
def generate_descriptions_in_folder(folder_path, data):
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    for post in data:
        for image_path in post['images']:
            image_file = os.path.basename(image_path)
            if image_file in image_files:
                # Generate image description using BLIP
                description_result = generate_image_description(os.path.join(folder_path, image_file))
                if description_result:
                    print(f"Image: {image_file} - Description: {description_result}")
                    post.setdefault('descriptions', []).append({image_file: description_result})

# Main function to scrape posts, download images, and generate descriptions
def main():
    keyword = "福州大学"
    page_limit = 1  # Adjust the number of pages to scrape
    posts = fetch_tieba_posts(keyword, page_limit)

    # Create images folder if it doesn't exist
    images_folder = 'images'
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)
        print(f"Created folder: {images_folder}")

    # Prepare JSON data
    data = []
    if posts:
        for post in posts:
            print(f"Title: {post['title']}\nLink: {post['link']}\n")
            image_urls = fetch_post_images(post['link'])
            if image_urls:
                print("Images:")
                downloaded_images = []
                for img_url in image_urls:
                    print(img_url)
                    local_path = download_image(img_url, images_folder)
                    if local_path:
                        downloaded_images.append(local_path)
                post['images'] = downloaded_images  # Add local image paths to post
            else:
                print("No images found.\n")
                post['images'] = []
            data.append(post)
    else:
        print("No posts found. Loading images from folder.")
        # If no posts are found, load existing images from the images folder
        if os.path.exists(images_folder):
            image_files = [f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))]
            data.append({'title': 'Local Images', 'link': 'N/A', 'images': [os.path.join(images_folder, img) for img in image_files]})

    # Generate descriptions in the images folder and update JSON data
    generate_descriptions_in_folder(images_folder, data)

    # Write updated data to JSON file
    with open('images_to_text.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Data has been written to images_to_text.json")

if __name__ == "__main__":
    main()
