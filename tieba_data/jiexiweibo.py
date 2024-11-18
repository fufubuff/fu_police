import pandas as pd
from transformers import pipeline
from tqdm import tqdm  # 引入进度条库

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def initialize_model():
    try:
        model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
        return pipeline("zero-shot-classification", model=model_name, tokenizer=model_name, use_fast=True)
    except Exception as e:
        print(f"Error initializing model: {e}")
        return None

def analyze_emotion(text, analyzer, candidate_labels):
    if pd.isna(text):
        return {"error": "文本为空"}
    try:
        results = analyzer(text, candidate_labels, multi_label=True)
        return dict(zip(results['labels'], results['scores']))
    except Exception as e:
        return {"error": str(e)}

def main():
    data_path = r'C:\Users\ASUS\WBData\demo.csv'
    data = load_data(data_path)
    if data is None:
        return
    emotion_analyzer = initialize_model()
    if emotion_analyzer is None:
        return

    candidate_labels = ["喜悦", "愤怒", "悲伤", "恐惧", "惊讶", "厌恶", "中性"]
    
    print("Starting emotion analysis...")
    for column in ['展示内容', '全部内容']:
        print(f"Analyzing emotions in {column}...")
        tqdm.pandas()  # 设置进度条
        data[f'{column}_情感分析'] = data[column].progress_apply(analyze_emotion, args=(emotion_analyzer, candidate_labels))
    
    output_path = r'C:\Users\ASUS\WBData\analyzed_demo.csv'
    data.to_csv(output_path, index=False)
    print(f"Analysis completed. Results are saved to {output_path}")

if __name__ == "__main__":
    main()
