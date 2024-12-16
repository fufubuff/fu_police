import json
import csv

# 读取 emotions JSON 文件
with open('images_emotions.json', 'r', encoding='utf-8') as json_file:
    emotions_data = json.load(json_file)

# 读取 descriptions JSON 文件
with open('images_to_text.json', 'r', encoding='utf-8') as json_file:
    descriptions_data = json.load(json_file)

# 创建一个字典来存储合并后的数据
merged_data = {}

# 合并 emotions 数据
for emotion in emotions_data[0]['emotions']:
    for image_name, values in emotion.items():
        merged_data[image_name] = values

# 合并 descriptions 数据
for description in descriptions_data[0]['descriptions']:
    for image_name, desc in description.items():
        if image_name in merged_data:
            merged_data[image_name]['description'] = desc
        else:
            merged_data[image_name] = {'description': desc}

# 将数据按 image_name 排序
sorted_data = sorted(merged_data.items())

# 打开 CSV 文件进行写入
with open('merged_images.csv', 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # 写入表头
    csv_writer.writerow(['id', 'image_name', 'description', 'emotions'])
    
    # 写入数据
    for image_name, values in sorted_data:
        idx = int(image_name.split('_')[-1].split('.')[0])
        emotions_json = json.dumps({
            'angry': values.get('angry', 0),
            'disgust': values.get('disgust', 0),
            'fear': values.get('fear', 0),
            'happy': values.get('happy', 0),
            'sad': values.get('sad', 0),
            'surprise': values.get('surprise', 0),
            'neutral': values.get('neutral', 0)
        })
        csv_writer.writerow([
            idx,
            image_name,
            values.get('description', ''),
            emotions_json
        ])