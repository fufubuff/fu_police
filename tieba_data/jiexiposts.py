import json
import os
from transformers import pipeline
from deepface import DeepFace  # 用于图片情感分析
import cv2  # 处理图片

# 示例图片情感分析函数
def analyze_image_emotions(image_path):
    try:
        # 使用 DeepFace 的 analyze 方法分析图片情感
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)

        # 初始化情感结果列表
        emotions_list = []

        # 检查 analysis 是否为列表
        if isinstance(analysis, list):
            for face_analysis in analysis:
                emotions_list.append(face_analysis['emotion'])
        elif isinstance(analysis, dict):
            emotions_list.append(analysis['emotion'])
        else:
            return {"error": "无法识别的分析结果格式"}

        return emotions_list  # 返回情感分布列表

    except Exception as e:
        return {"error": f"图片分析失败: {str(e)}"}

# 1. 加载 JSON 数据
print("开始加载数据...")
with open("posts.json", "r", encoding="utf-8") as file:
    posts = json.load(file)
print("数据加载完成。")

# 2. 初始化零样本分类模型（使用新的模型）
print("开始加载模型...")
emotion_analyzer = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    tokenizer="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    use_fast=False
)
print("模型加载完成。")

# 定义情感标签
candidate_labels = ["喜悦", "愤怒", "悲伤", "恐惧", "惊讶", "厌恶", "中性"]

# 3. 对标题和图片逐一进行分析
print("开始分析数据...")
for post in posts:
    # 标题情感分析
    title = post["title"]
    try:
        emotion_result = emotion_analyzer(title, candidate_labels, multi_label=True)
        # emotion_result 是一个包含序列、标签和分数的字典
        emotion_scores = dict(zip(emotion_result['labels'], emotion_result['scores']))
        post["title_emotions"] = emotion_scores
    except Exception as e:
        post["title_emotions"] = {"error": f"标题分析失败: {str(e)}"}
        print(f"标题分析失败: {title}, 错误: {e}")

    # 图片情感分析
    image_emotions = {}
    for image_path in post["images"]:
        try:
            full_image_path = os.path.join("images", os.path.basename(image_path))
            if os.path.exists(full_image_path):
                emotions_list = analyze_image_emotions(full_image_path)
                image_emotions[os.path.basename(image_path)] = emotions_list
            else:
                image_emotions[os.path.basename(image_path)] = {"error": "图片文件不存在"}
        except Exception as e:
            image_emotions[os.path.basename(image_path)] = {"error": str(e)}

    # 将图片情感分析结果存储到 JSON
    post["image_emotions"] = image_emotions
print("数据分析完成。")

# 4. 保存结果到新 JSON 文件
print("开始保存结果...")
with open("posts_with_analysis.json", "w", encoding="utf-8") as file:
    json.dump(posts, file, ensure_ascii=False, indent=4)
print("结果保存完成。")

# 输出标题和每张图片的情感分析
for post in posts:
    print(f"标题: {post['title']}")
    print("标题情感分析:")
    if isinstance(post["title_emotions"], dict):
        for emotion, score in post["title_emotions"].items():
            print(f"  {emotion}: {score:.4f}")
    else:
        print(f"  {post['title_emotions']}")
    if post["images"]:
        print("图片情感分析:")
        for image_name, emotions in post["image_emotions"].items():
            if isinstance(emotions, dict) and "error" in emotions:
                print(f"  {image_name}: {emotions['error']}")
            else:
                print(f"  {image_name}:")
                for idx, emotion_dict in enumerate(emotions):
                    print(f"    人脸 {idx + 1}:")
                    for emotion, score in emotion_dict.items():
                        print(f"      {emotion}: {score:.4f}")
    else:
        print("没有图片。")
    print()

print("分析完成，结果已保存到 posts_with_analysis.json。")
