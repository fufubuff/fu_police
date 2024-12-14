import requests
import hashlib
import time


def performSentimentAnalysis(text):
    # 你的讯飞平台相关信息
    APPID = "8d0ae61a"
    APISecret = "ZmE2NzcyMTM1YmM4YWFmNzFmOWRkZWJm"
    APIKey = "1dc9a42593b530da7189afa5bda65a6d"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

    # 根据接口要求构建请求数据
    data = {
        "max_tokens": 4096,
        "top_k": 4,
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的情感分析专家,请根据我给出的文字或者图片，分析出愤怒、厌恶、恐惧、喜悦、悲伤、惊讶、中性的情绪占比。"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "model": "4.0Ultra"
    }
    data["stream"] = True

    # 构建请求头，这里需要按照讯飞的鉴权规则来添加相关信息，示例中添加了时间戳、签名等信息
    cur_time = str(int(time.time()))
    param = {"text": text}
    param_str = str(param).encode('utf-8')
    base_string = APIKey + cur_time + hashlib.md5(param_str).hexdigest()
    check_sum = hashlib.md5(base_string.encode('utf-8')).hexdigest()
    header = {
        "Authorization": f"Bearer {APIKey}:{check_sum}",
        "Content-Type": "application/json",
        "X-Appid": APPID,
        "X-CurTime": cur_time,
        "X-Param": hashlib.md5(param_str).hexdigest()
    }

    try:
        response = requests.post(url, headers=header, json=data, stream=True)
        response.encoding = "utf-8"

        # 这里先简单示例解析返回结果，实际中要根据接口真实返回的数据结构准确提取对应情绪占比信息
        result_data = {}
        for line in response.iter_lines(decode_unicode="utf-8"):
            if line:
                # 假设返回的JSON数据里包含了情绪占比相关字段，这里要准确解析，以下是示例伪代码，需要按实际调整
                parsed_line = eval(line)  # 简单将每行文本转为字典对象，实际可能需要更严格的JSON解析
                if "emotion" in parsed_line:
                    emotion_data = parsed_line["emotion"]
                    result_data["anger"] = emotion_data.get("anger", 0)
                    result_data["disgust"] = emotion_data.get("disgust", 0)
                    result_data["fear"] = emotion_data.get("fear", 0)
                    result_data["joy"] = emotion_data.get("joy", 0)
                    result_data["sadness"] = emotion_data.get("sadness", 0)
                    result_data["surprise"] = emotion_data.get("surprise", 0)
                    result_data["neutral"] = emotion_data.get("neutral", 0)

        # 简单验证数值范围，这里假设合理范围是0 - 100，可以根据实际情况调整
        for value in result_data.values():
            if value < 0 or value > 100:
                print(f"情感分析结果数据中存在不合理的值: {value}")

        return result_data
    except requests.RequestException as e:
        print(f"情感分析接口请求失败: {e}")
        return {
            "anger": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "sadness": 0,
            "surprise": 0,
            "neutral": 0
        }

if __name__ == '__main__':
    text = "学校的饭太贵了，唉"
    result = performSentimentAnalysis(text)
    print(result)