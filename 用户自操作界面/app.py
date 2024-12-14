from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入CORS模块，用于处理跨域请求
import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import psycopg2
from psycopg2 import Error, extras
import requests
import json
from dotenv import load_dotenv
import logging



app = Flask(__name__)
CORS(app)  # 应用CORS配置，允许所有来源的跨域请求，可根据实际需求进行更精细的配置

# 配置数据库连接（使用你之前在WBParser类中类似的配置信息，这里假设不变）
db_config = {
    'host': '101.132.80.183',
    'port': '5433',
    'user': 'zzsthere',
    'password': '20020925Aa',
    'database': 'dbf72a0c3d7d054ef39b98488f2995d159zz'
}

# 初始化数据库连接函数
def connect_db():
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

# 函数功能：从指定路径加载数据（这里假设是CSV格式的数据文件），若加载失败则返回None并打印错误信息
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# 初始化情感分析模型，若初始化出现异常则返回None并打印错误信息
def initialize_emotion_model():
    try:
        model_name = r"models--MoritzLaurer--mDeBERTa-v3-base-mnli-xnli\snapshots\\8adb042d524ecd5c26d3e3ba0e3fbcf7e2d0864c"
        return pipeline("zero-shot-classification", model=model_name, tokenizer=model_name, use_fast=True)
    except Exception as e:
        print(f"Error initializing emotion model: {e}")
        return None

# 函数功能：对输入的文本进行情感分析，若文本为空或分析过程出现异常则返回相应的错误信息，否则返回包含各情感类别及对应得分的字典
def analyze_emotion(text, analyzer, candidate_labels):
    if pd.isna(text):
        return {"error": "文本为空"}
    try:
        results = analyzer(text, candidate_labels, multi_label=True)
        return dict(zip(results['labels'], results['scores']))
    except Exception as e:
        return {"error": str(e)}


@app.route('/sentiment-analysis', methods=['POST'])
def analyze_sentiment_api():
    data = request.get_json()  # 获取前端发来的JSON格式的数据
    text = data.get('text')  # 从数据中提取要分析的文本内容
    emotion_analyzer = initialize_emotion_model()  # 初始化情感分析模型
    if emotion_analyzer is None:
        return jsonify({"error": "情感分析模型初始化失败"}), 500
    candidate_labels = ["喜悦", "愤怒", "悲伤", "恐惧", "惊讶", "厌恶", "中性"]
    result = analyze_emotion(text, emotion_analyzer, candidate_labels)
    print("后端返回的情感分析结果:", result)  # 添加这行日志输出，方便查看返回给前端的数据情况
    return jsonify(result)




# 新增的路由处理函数，处理'/api/search'接口的GET请求，用于根据关键词搜索微博数据
@app.route('/api/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')  # 获取前端传来的关键词
    if not keyword:
        return jsonify({"message": "缺少关键词参数"}), 400
    conn = connect_db()
    if not conn:
        return jsonify({"message": "数据库连接失败"}), 500
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        # 构建查询语句，这里假设在main_content表的展示内容字段中搜索关键词，使用 LIKE 进行模糊查询
        # 注意这里使用了参数化查询，能有效防止SQL注入攻击
        query = "SELECT * FROM main_content WHERE 展示内容 LIKE %s"
        cursor.execute(query, ('%' + keyword + '%',))
        # 获取所有符合条件的查询结果，这里返回的结果是一个字典列表，每个字典对应数据库表中的一行数据
        results = cursor.fetchall()
    except Error as e:
        print(f"数据库查询出现错误: {e}")
        cursor.close()
        conn.close()
        return jsonify({"message": "数据库查询出现错误", "error_detail": str(e)}), 500
    cursor.close()
    conn.close()
    return jsonify(results)


def chat_with_ai(user_message, high_freq_topics, sentiment_summary):
    api_url = 'https://api.gptsapi.net/v1/chat/completions'  # 确认这个 URL 是否正确
    api_key = 'sk-mvOc5002d4fec6492dda97092933450e3daea29ad09eYKtV' # 从环境变量中获取 API 密钥

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'  # 假设 API 使用 Bearer Token 认证
    }

    # 构建提示内容，包含词频和情感摘要
    analysis_context = (
        f"以下是福州大学当前的舆情数据分析：\n"
		f"用户输入的文本: {user_message}\n"
        f"高频话题: {', '.join(high_freq_topics)}\n"
        f"情感分析:\n"
    )
    for emotion, count in sentiment_summary.items():
        analysis_context += f"- {emotion}: {count}\n"

    # 完整的用户提示
    full_user_message = (
        f"{analysis_context}\n"
        f"基于以上数据，请对福州大学的当前舆情进行详细分析，并提供相关建议。"
    )

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "你是一个帮助分析福州大学舆情的助手。请你尽可能地分析和猜测福州大学的舆论和学生情绪，大家目前关心什么话题"},
            {"role": "user", "content": full_user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()  # 如果响应状态码不是 2xx，会抛出异常

        data = response.json()
        print(f"API Response: {json.dumps(data, ensure_ascii=False, indent=2)}")  # 调试输出

        # 提取 AI 的回复
        ai_reply = data['choices'][0]['message']['content'].strip()
        return ai_reply

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err}")  # HTTP 错误
        return '抱歉，分析时出现了问题。请稍后再试。'
    except requests.exceptions.Timeout:
        print("请求超时")  # 超时
        return '抱歉，服务器响应超时。请稍后再试。'
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")  # 其他请求错误
        return '抱歉，出现了一个错误。请稍后再试。'
    except KeyError:
        print("响应结构异常")
        return '抱歉，收到的回复格式不正确。'

def chat_with_ai1(user_message):
    api_url = 'https://api.gptsapi.net/v1/chat/completions'  # 确认这个 URL 是否正确
    api_key = 'sk-mvOc5002d4fec6492dda97092933450e3daea29ad09eYKtV' # 从环境变量中获取 API 密钥

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'  # 假设 API 使用 Bearer Token 认证
    }

    # 构建提示内容，包含词频和情感摘要
    analysis_context = (
        f"以下是福州大学当前的舆情数据分析：\n"
		f"用户搜索到的关键词和数据: {user_message}\n"
    )

    # 完整的用户提示
    full_user_message = (
        f"{analysis_context}\n"
        f"基于以上数据，请对福州大学的当前舆情进行详细分析，并提供相关建议。"
    )

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "你是一个帮助分析福州大学舆情的助手。请你尽可能地分析和猜测福州大学的舆论和学生情绪，大家目前关心什么话题"},
            {"role": "user", "content": full_user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()  # 如果响应状态码不是 2xx，会抛出异常

        data = response.json()
        print(f"API Response: {json.dumps(data, ensure_ascii=False, indent=2)}")  # 调试输出

        # 提取 AI 的回复
        ai_reply = data['choices'][0]['message']['content'].strip()
        return ai_reply

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err}")  # HTTP 错误
        return '抱歉，分析时出现了问题。请稍后再试。'
    except requests.exceptions.Timeout:
        print("请求超时")  # 超时
        return '抱歉，服务器响应超时。请稍后再试。'
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")  # 其他请求错误
        return '抱歉，出现了一个错误。请稍后再试。'
    except KeyError:
        print("响应结构异常")
        return '抱歉，收到的回复格式不正确。'





@app.route('/api/search-and-analyze', methods=['GET'])
def search_and_analyze():
    """
    1. 根据关键字在数据库中搜索
    2. 将搜索到的数据整合后，对文本做进一步关键词提取
    3. 将提取的关键词和文本摘要发给 AI 做进一步的热点分析和总结
    4. 返回给前端搜索结果 + AI分析结果
    """
    keyword_str = request.args.get('keyword')  # 获取前端传来的关键词字符串
    if not keyword_str:
        return jsonify({"message": "缺少关键词参数"}), 400
    
        # 将用户输入的 keyword_str 用空格进行拆分，得到多个关键词
        # 例如 "福州大学 军训" -> ["福州大学", "军训"]
    split_keywords = keyword_str.split()
    
        # 如果你希望去除空字符串或者前后空白，可以再做一次过滤
    split_keywords = [kw.strip() for kw in split_keywords if kw.strip()]
    if not split_keywords:
        return jsonify({"message": "关键词为空"}), 400
    
    conn = connect_db()
    if not conn:
        return jsonify({"message": "数据库连接失败"}), 500
    
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
            # 动态构建 WHERE 子句，让所有关键词都通过 LIKE 匹配(AND 连接)
            # SELECT * FROM main_content WHERE 展示内容 LIKE %keyword1% AND 展示内容 LIKE %keyword2% ...
        where_clauses = []
        params = []
        for kw in split_keywords:
            where_clauses.append("展示内容 LIKE %s")
            params.append(f"%{kw}%")
    
            # 将各个条件用 AND 拼接
        where_condition = " AND ".join(where_clauses)
    
        query = f"SELECT * FROM main_content WHERE {where_condition}"
        cursor.execute(query, params)
        results = cursor.fetchall()
    except Error as e:
        print(f"数据库查询出现错误: {e}")
        cursor.close()
        conn.close()
        return jsonify({"message": "数据库查询出现错误", "error_detail": str(e)}), 500
    
    cursor.close()
    conn.close()
    
        # 如果没有搜索到数据，直接返回空结果
    if not results:
        return jsonify({
                "results": [],
                "analysis": "没有找到相关数据，无法进行AI分析。"
            })
    
        # 2. 整合所有搜索结果中的文本
        # 假设展示内容字段叫做 "展示内容"
    all_text = " ".join([row['展示内容'] for row in results if row.get('展示内容')])
    
        # 3. 提取关键词（可换成更复杂的NLP方法）
    extracted_keywords_str = extract_multiple_keywords(all_text, top_n=10)
    
        # 4. 构建给AI的提示
    ai_prompt = (
            f"以下是根据关键词 '{keyword_str}' 搜索得到的内容集合：\n\n"
            f"{all_text}\n\n"
            f"系统自动提取的多个关键词：{extracted_keywords_str}\n\n"
            "请基于以上内容，对这些话题进行简要分析，并给出热点话题的概括。"
        )
    
    public_opinion = chat_with_ai1(user_message=ai_prompt)
    
        # 5. 返回给前端
    response = {
            "results": results,              # 原始数据库搜索结果
            "analysis": public_opinion,      # AI分析结果
            "extractedKeywords": extracted_keywords_str
        }
    return jsonify(response)
    



def extract_multiple_keywords(text, top_n=10):
    """
    从文本中提取多个高频词，并返回用空格隔开的字符串。
    这里可以根据需要换成jieba分词或更复杂的NLP方法。
    """
    from collections import Counter
    import re

    # 用正则提取“单词/词语”
    words = re.findall(r'\b\w+\b', text.lower())

    # 可以添加更多停用词
    stop_words = set(['的', '和', '是', '在', '了', '有', '我', '也', '不', '就', 
                      '你', '我们', '他们', '她们', '没有', '这个', '那个', '什么'])

    # 过滤停用词及长度过短的词
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]

    word_counts = Counter(filtered_words)
    high_freq = [word for word, count in word_counts.most_common(top_n)]

    # 将关键词用空格连起来
    return " ".join(high_freq)



@app.route('/public-opinion-analysis', methods=['POST'])
def public_opinion_analysis_api():
    data = request.get_json()
    text = data.get('text')
    emotion_analyzer = initialize_emotion_model()  # 初始化情感分析模型
    if emotion_analyzer is None:
        return jsonify({"error": "情感分析模型初始化失败"}), 500
    candidate_labels = ["喜悦", "愤怒", "悲伤", "恐惧", "惊讶", "厌恶", "中性"]	
    sentiment_result = analyze_emotion(text, emotion_analyzer, candidate_labels) # 接收情感分析结果

    if not text:
        return jsonify({"error": "缺少文本内容"}), 400

    if not sentiment_result:
        return jsonify({"error": "缺少情感分析结果"}), 400


    high_freq_topics = extract_high_freq_topics(text)  

    # 调用 chat_with_ai 函数
    public_opinion = chat_with_ai(user_message=text, high_freq_topics=high_freq_topics, sentiment_summary=sentiment_result)

    if "error" in public_opinion:
        return jsonify(public_opinion), 500

    # 组合结果
    result = {
        'text': text,
        'sentimentResult': sentiment_result,
        'publicOpinionResult':  public_opinion
    }

    logging.info(f"后端返回的舆情分析结果: {result}")
    return jsonify(result)


def extract_high_freq_topics(text, top_n=10):
    """
    提取文本中的高频话题。
    这里只是一个简单的示例，实际应用中可以使用更复杂的自然语言处理技术。
    """
    from collections import Counter
    import re

    # 使用简单的单词分割和清理
    words = re.findall(r'\b\w+\b', text.lower())
    # 假设停用词列表
    stop_words = set(['的', '和', '是', '在', '了', '有', '我', '也', '不', '就'])
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    word_counts = Counter(filtered_words)
    high_freq = [word for word, count in word_counts.most_common(top_n)]
    return high_freq





if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)