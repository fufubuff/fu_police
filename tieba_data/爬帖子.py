import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json
import shutil

def fetch_tieba_posts(keyword, page_limit=3):
    base_url = f"https://tieba.baidu.com/f?kw={keyword}&ie=utf-8"
    posts = []

    for page in range(page_limit):
        page_url = f"{base_url}&pn={page * 50}"
        response = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            threads = soup.find_all('div', {'class': 'threadlist_title'})

            for thread in threads:
                a_tag = thread.find('a', {'class': 'j_th_tit'})
                if a_tag:
                    title = a_tag.text.strip()
                    relative_link = a_tag['href']
                    link = urljoin("https://tieba.baidu.com", relative_link)
                    posts.append({
                        "title": title,
                        "link": link,
                        "images": []
                    })
        else:
            print(f"Failed to retrieve page {page + 1}. Status code: {response.status_code}")

    return posts

def fetch_post_images(post_url):
    response = requests.get(post_url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img', {'class': 'BDE_Image'})
        image_urls = [img['src'] for img in images if 'src' in img.attrs]
        return image_urls
    else:
        print(f"Failed to retrieve post {post_url}. Status code: {response.status_code}")
        return []

def download_image(image_url, folder_path, image_num):
    try:
        response = requests.get(image_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            # 获取图片扩展名
            ext = os.path.splitext(image_url)[1].split('?')[0]  # 去除URL参数
            if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                ext = '.jpg'  # 默认扩展名
            image_name = f"image_{image_num}{ext}"
            image_path = os.path.join(folder_path, image_name)
            with open(image_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            return image_path
        else:
            print(f"Failed to download image {image_url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        return None

def main():
    keyword = "福州大学"
    page_limit = 3
    output_json = "posts.json"
    images_folder = "images"

    # 创建图片文件夹
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    print(f"开始爬取关于'{keyword}'的贴吧帖子，爬取{page_limit}页...")
    posts = fetch_tieba_posts(keyword, page_limit)

    image_counter = 1  # 用于命名图片

    for post in posts:
        print(f"正在处理帖子: {post['title']}\n链接: {post['link']}\n")
        image_urls = fetch_post_images(post['link'])
        if image_urls:
            print(f"找到 {len(image_urls)} 张图片，开始下载...")
            for img_url in image_urls:
                image_path = download_image(img_url, images_folder, image_counter)
                if image_path:
                    post['images'].append(image_path)
                    image_counter += 1
            print("图片下载完成。\n")
        else:
            print("未找到图片。\n")

    # 将数据保存为JSON文件
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
    print(f"所有数据已保存到 {output_json} 文件中。")
    print(f"所有图片已下载到 {images_folder} 文件夹中。")

if __name__ == "__main__":
    main()
