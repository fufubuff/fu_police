
from flask import Flask, send_file, jsonify
import json
import jieba
import jieba.posseg as pseg
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import numpy as np
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# 读取 comments.json 文件，只提取 title 字段
def get_titles():
    try:
        with open('comments.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        titles = [item['Title'] for item in data]  # 只提取 'title' 字段
        return titles
    except Exception as e:
        logging.error(f"Error reading comments.json: {e}")
        return []

# 生成词云图
@app.route('/wordcloud')
def generate_wordcloud():
    try:
        titles = get_titles()
        if not titles:
            return jsonify({"error": "No titles found"}), 500

        text = ' '.join(titles)  # 将所有标题合并为一个文本

        # 使用 jieba 分词，并过滤掉语气词、助词等非名词
        words = pseg.cut(text)
        filtered_words = [word for word, flag in words if flag.startswith('n')]

        filtered_text = ' '.join(filtered_words)

        # 创建词云
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            contour_width=1,
            contour_color='steelblue',
            font_path='C:/Windows/Fonts/AlibabaPuHuiTi-3-45-Light.ttf'  # 根据需要设置字体路径
        ).generate(filtered_text)

        # 绘制词云图
        plt.figure(figsize=(10, 10))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")

        # 将词云图保存为内存中的图像
        img = BytesIO()
        plt.savefig(img, format='PNG')
        img.seek(0)

        return send_file(img, mimetype='image/png')
    except Exception as e:
        logging.error(f"Error generating word cloud: {e}")
        return jsonify({"error": "Failed to generate word cloud"}), 500

if __name__ == '__main__':
    app.run(debug=True)