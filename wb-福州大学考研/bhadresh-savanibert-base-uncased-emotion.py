import json
from transformers import pipeline
import pandas as pd

# 1. 读取JSON文件
try:
    with open(r"C:\Users\lenovo\Desktop\tieba_data1111(1).json", "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading JSON file: {e}")
    data = []

# 2. 加载公开可用的中文情感分析模型
try:
    emotion_analyzer = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")
except Exception as e:
    print(f"Error loading sentiment analysis model: {e}")
    emotion_analyzer = None

# 3. 设置最大输入长度，截断过长的文本
def analyze_text(text):
    # BERT 最大输入长度为 512 tokens
    return emotion_analyzer(text, truncation=True, max_length=512) if emotion_analyzer else []

# 4. 分析标题和评论
results = []
for post in data:
    title = post.get("Title", "")
    comments = post.get("Comments", [])
    
    # 分析标题情绪
    if title.strip():  # 避免分析空标题
        title_result = analyze_text(title)
        if title_result:
            sentiment = title_result[0]["label"]
            score = title_result[0]["score"]
            results.append({"Text": title, "Sentiment": sentiment, "Score": score})
    
    # 分析每条评论情绪
    for comment in comments:
        if comment.strip():  # 避免分析空评论
            comment_result = analyze_text(comment)
            if comment_result:
                sentiment = comment_result[0]["label"]
                score = comment_result[0]["score"]
                results.append({"Text": comment, "Sentiment": sentiment, "Score": score})

# 5. 保存结果至文件
output_file = r"C:\Users\lenovo\Desktop\sentiment_analysis_results.csv"
try:
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Results saved to {output_file}")
except Exception as e:
    print(f"Error saving results to CSV: {e}")
