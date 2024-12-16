import os
import psycopg2
from PIL import Image
import io

# 数据库连接信息
conn = psycopg2.connect(
    host="101.132.80.183",
    port=5433,
    database="dbf72a0c3d7d054ef39b98488f2995d159zz",
    user="zzsthere",
    password="20020925Aa"  # 请替换为实际密码
)
cursor = conn.cursor()

# 文件夹路径
folder_path = 'images_kay'

# 遍历文件夹中的所有 JPG 文件
for filename in os.listdir(folder_path):
    if filename.endswith('.jpg'):
        file_path = os.path.join(folder_path, filename)
        
        # 打开并读取图像文件
        with open(file_path, 'rb') as file:
            img = Image.open(file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 更新图像数据到数据库
            cursor.execute(
                "UPDATE merged_images SET image_data = %s WHERE image_name = %s",
                (psycopg2.Binary(img_byte_arr), filename)
            )

# 提交事务并关闭连接
conn.commit()
cursor.close()
conn.close()