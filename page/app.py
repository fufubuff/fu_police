# app.py
from flask import Flask, jsonify, render_template,request
from flask_cors import CORS
import psycopg2
import json
from datetime import datetime
import base64
import openai
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from dotenv import load_dotenv
import requests

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)


openai.api_key='sk-mvOc5002d4fec6492dda97092933450e3daea29ad09eYKtV'
openai.api_base ='https://api.gptsapi.net'


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='101.132.80.183',
            port='5433',
            database='dbf72a0c3d7d054ef39b98488f2995d159zz',
            user='zzsthere',
            password='20020925Aa'
        )
        return conn
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return None

def fetch_comments(query, params=None):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        comments = []
        for row in rows:
            if 'comment_analyse' in query:
                # 处理 comment_analyse 表数据
                score_data = row[3]
                try:
                    score = json.loads(score_data)
                except (TypeError, json.JSONDecodeError):
                    score = score_data

                comment = {
                    'id': row[0],
                    'text': row[1],
                    'sentiment': row[2],
                    'score': score
                }
            elif 'merged_images' in query:
                # 处理 merged_images 表数据
                sentiment_data = row[3]
                try:
                    sentiment = json.loads(sentiment_data)
                except (TypeError, json.JSONDecodeError):
                   sentiment = sentiment_data
# 将 image_data 转换为 Base64 编码的字符串
                image_data_base64 = base64.b64encode(row[4]).decode('utf-8')
                comment = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'sentiment': sentiment,
                    'image_data': image_data_base64
                }
            else:
                # 处理 analyzed_demo_one 表数据
                sentiment_data = row[3]
                try:
                    sentiment = json.loads(sentiment_data)
                except (TypeError, json.JSONDecodeError):
                    sentiment = sentiment_data

                comment = {
                    'id': row[0],
                    'nickname': row[1],
                    'content': row[2],
                    'sentiment': sentiment
                }
            comments.append(comment)

        return comments
    except Exception as e:
        print(f"查询错误: {e}")
        return None

@app.route('/api/comments', methods=['GET'])
def get_comments():
    try:
        print("接收到 /api/comments 请求")
        query = 'SELECT id, nickname, content, sentiment FROM analyzed_demo_one'
        comments = fetch_comments(query)
        if comments is None:
            return jsonify({'error': '无法获取评论数据'}), 500

        print(f"查询到 {len(comments)} 条评论")
        return jsonify({'comments': comments})
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/comments2', methods=['GET'])
def get_comments2():
    try:
        print("接收到 /api/comments2 请求")
        query = 'SELECT id, text, sentiment, score FROM comment_analyse'
        comments = fetch_comments(query)
        if comments is None:
            return jsonify({'error': '无法获取评论分析数据'}), 500

        print(f"查询到 {len(comments)} 条评论分析数据")
        return jsonify({'comments': comments})
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({'error': str(e)}), 500

# 新的 API 路由获取 merged_images 数据
@app.route('/api/merged_images', methods=['GET'])
def get_merged_images():
    try:
        print("接收到 /api/merged_images 请求")
        query = 'SELECT id, image_name, description, emotions, image_data FROM merged_images'
        comments = fetch_comments(query)
        if comments is None:
            return jsonify({'error': '无法获取 merged_images 数据'}), 500

        print(f"查询到 {len(comments)} 条 merged_images 数据")
        return jsonify({'merged_images': comments})
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({'error': str(e)}), 500



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



@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        print(f"Received data: {data}, type: {type(data)}")  # 调试输出

        if not isinstance(data, dict):
            raise ValueError("Invalid JSON data received")

        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'reply': '请输入您的消息。'}), 400

        # 获取高频话题
        high_freq_topics = get_high_frequency_topics()

        # 获取情感摘要
        sentiment_summary = get_sentiment_summary()

        # 调用 AI 进行分析
        ai_reply = chat_with_ai(user_message, high_freq_topics, sentiment_summary)

        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"AI 聊天错误: {e}")
        return jsonify({'reply': '抱歉，分析时出现了问题。请稍后再试。'}), 500
    
    
    
    
def get_sentiment_summary():
    try:
        # 查询情感数据
        query = 'SELECT sentiment FROM analyzed_demo_one'
        sentiments1 = fetch_sentiment_data(query)

        query = 'SELECT sentiment FROM comment_analyse'
        sentiments2 = fetch_sentiment_data(query)

        # 合并所有情感数据
        all_sentiments = sentiments1 + sentiments2

        # 统计情感类别
        sentiment_counts = Counter(all_sentiments)

        return sentiment_counts

    except Exception as e:
        print(f"情感摘要错误: {e}")
        return {}

def fetch_sentiment_data(query, params=None):
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        sentiments = []
        for row in rows:
            sentiment_data = row[0]
            try:
                sentiment = json.loads(sentiment_data)
            except (TypeError, json.JSONDecodeError):
                sentiment = sentiment_data

            if isinstance(sentiment, dict):
                # 假设 sentiment 是一个字典，包含各类情感的分数
                dominant_sentiment = max(sentiment, key=sentiment.get)
            elif isinstance(sentiment, str):
                dominant_sentiment = sentiment
            else:
                dominant_sentiment = 'unknown'

            sentiments.append(dominant_sentiment)

        return sentiments
    except Exception as e:
        print(f"查询情感数据错误: {e}")
        return []
    

def fetch_comments(query, params=None):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        comments = []
        for row in rows:
            if 'comment_analyse' in query:
                # 处理 comment_analyse 表数据
                score_data = row[3]
                try:
                    score = json.loads(score_data)
                except (TypeError, json.JSONDecodeError):
                    score = score_data

                sentiment = row[2]
                try:
                    sentiment_dict = json.loads(sentiment)
                except (TypeError, json.JSONDecodeError):
                    sentiment_dict = sentiment

                # 假设 sentiment_dict 是一个字典，统计主导情感
                if isinstance(sentiment_dict, dict):
                    dominant_emotion = max(sentiment_dict, key=sentiment_dict.get)
                else:
                    dominant_emotion = sentiment_dict

                comment = {
                    'id': row[0],
                    'text': row[1],
                    'sentiment': dominant_emotion,
                    'score': score
                }
            elif 'merged_images' in query:
                # 处理 merged_images 表数据
                sentiment_data = row[3]
                try:
                    sentiment = json.loads(sentiment_data)
                except (TypeError, json.JSONDecodeError):
                    sentiment = sentiment_data

                # 将 image_data 转换为 Base64 编码的字符串
                image_data_base64 = base64.b64encode(row[4]).decode('utf-8')
                comment = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'sentiment': sentiment,
                    'image_data': image_data_base64
                }
            else:
                # 处理 analyzed_demo_one 表数据
                sentiment_data = row[3]
                try:
                    sentiment = json.loads(sentiment_data)
                except (TypeError, json.JSONDecodeError):
                    sentiment = sentiment_data

                if isinstance(sentiment, dict):
                    dominant_emotion = max(sentiment, key=sentiment.get)
                else:
                    dominant_emotion = sentiment

                comment = {
                    'id': row[0],
                    'nickname': row[1],
                    'content': row[2],
                    'sentiment': dominant_emotion
                }
            comments.append(comment)

        return comments
    except Exception as e:
        print(f"查询错误: {e}")
        return None
    
def get_high_frequency_topics():
    try:
        conn = get_db_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        # 从 analyzed_demo_one 和 comment_analyse 表中获取文本
        query1 = 'SELECT content FROM analyzed_demo_one'
        cursor.execute(query1)
        rows1 = cursor.fetchall()

        query2 = 'SELECT text FROM comment_analyse'
        cursor.execute(query2)
        rows2 = cursor.fetchall()


        cursor.close()
        conn.close()

        # 合并所有文本
        all_text = ' '.join([row[0] for row in rows1] + [row[0] for row in rows2])

        # 分词
        tokens = word_tokenize(all_text)

        # 转为小写
        tokens = [word.lower() for word in tokens]

        # 去除标点符号和数字
        tokens = [word for word in tokens if word.isalpha()]

        # 去除停用词
        stop_words = set(stopwords.words('chinese') + stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]

        # 统计词频
        word_counts = Counter(filtered_tokens)

        # 获取前10个高频词
        high_freq = [word for word, count in word_counts.most_common(10)]

        return high_freq
    except Exception as e:
        print(f"高频话题统计错误: {e}")
        return []



if __name__ == '__main__':
    app.run(debug=True)