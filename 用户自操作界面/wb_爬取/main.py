import os
import pandas as pd
from rich.progress import track
from get_main_body import get_all_main_body
from get_comments_level_one import get_all_level_one
from get_comments_level_two import get_all_level_two
import logging
import psycopg2
from psycopg2 import Error, extras
from datetime import datetime

logging.basicConfig(level=logging.INFO)


class MemFireConnection:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.conn
        except Error as e:
            logging.error(f"Error connecting to MemFire: {e}")
            raise

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


class WBParser:
    def __init__(self, cookie, db_connection):
        self.cookie = cookie
        self.db = db_connection

        os.makedirs("./WBData", exist_ok=True)
        os.makedirs("./WBData/Comments_level_1", exist_ok=True)
        os.makedirs("./WBData/Comments_level_2", exist_ok=True)
        self.main_body_filepath = "./WBData/demo.csv"
        self.comments_level_1_filename = "./WBData/demo_comments_one.csv"
        self.comments_level_2_filename = "./WBData/demo_comments_two.csv"
        self.comments_level_1_dirpath = "./WBData/Comments_level_1/"
        self.comments_level_2_dirpath = "./WBData/Comments_level_2/"

        # 更新列名映射
        self.column_maps = {
            'main_content': {
                'mid': 'mid',
                'uid': 'uid',
                '个人昵称': '个人昵称',
                '个人主页': '个人主页',
                '发布时间': '发布时间',
                '内容来自': '内容来自',
                '展示内容': '展示内容',
                '全部内容': '全部内容',
                '转发数量': '转发数量',
                '评论数量': '评论数量',
                '点赞数量': '点赞数量',
                'topic': 'topic',
                'search_type': 'search_type'
            },
            'comments_level_one': {
                'main_body_mid': 'main_body_mid',
                'main_body_uid': 'main_body_uid',
                '发布时间': '发布时间',
                '处理内容': '处理内容',
                '评论地点': '评论地点',
                'mid': 'mid',
                '回复数量': '回复数量',
                '点赞数量': '点赞数量',
                '原生内容': '原生内容',
                'uid': 'uid',
                '用户昵称': '用户昵称',
                '用户主页': '用户主页',
                '用户认证信息': '用户认证信息',
                '用户描述': '用户描述',
                '用户地理位置': '用户地理位置',
                '用户性别': '用户性别',
                '用户粉丝数量': '用户粉丝数量',
                '用户关注数量': '用户关注数量',
                '用户全部微博': '用户全部微博',
                '用户累计评论': '用户累计评论',
                '用户累计转发': '用户累计转发',
                '用户累计获赞': '用户累计获赞',
                '用户转评赞': '用户转评赞'
            },
            'comments_level_two': {
                'comments_level_1_mid': 'comments_level_1_mid',
                'main_body_uid': 'main_body_uid',
                '发布时间': '发布时间',
                '处理内容': '处理内容',
                '评论地点': '评论地点',
                'mid': 'mid',
                '点赞数量': '点赞数量',
                '原生内容': '原生内容',
                'uid': 'uid',
                '用户昵称': '用户昵称',
                '用户主页': '用户主页',
                '用户认证信息': '用户认证信息',
                '用户描述': '用户描述',
                '用户地理位置': '用户地理位置',
                '用户性别': '用户性别',
                '用户粉丝数量': '用户粉丝数量',
                '用户关注数量': '用户关注数量',
                '用户全部微博': '用户全部微博',
                '用户累计评论': '用户累计评论',
                '用户累计转发': '用户累计转发',
                '用户累计获赞': '用户累计获赞',
                '用户转评赞': '用户转评赞'
            }
        }

    def clean_df(self, df):
        """清理数据框"""
        # 移除 Unnamed 列
        unnamed_cols = [col for col in df.columns if 'Unnamed' in col]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)

        # 替换特殊字符和空格
        df = df.replace({',': '', ' ': ''}, regex=True)

        # 转换数值列
        numeric_cols = ['回复数量', '点赞数量', '用户粉丝数量', '用户关注数量', '用户全部微博',
                        '用户累计评论', '用户累计转发', '用户累计获赞', '用户转评赞']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace({',': ''}, regex=True), errors='coerce')

        return df

    def save_to_db(self, table, data):
        try:
            if data.empty:
                logging.warning(f"No data to insert into {table}")
                return

            # 清理和处理数据
            processed_data = self.clean_df(data.copy())

            # 映射列名
            if table in self.column_maps:
                processed_data = processed_data.rename(columns=self.column_maps[table])

            cursor = self.db.conn.cursor()
            placeholders = ', '.join(['%s'] * len(processed_data.columns))
            columns = ', '.join(processed_data.columns)
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"

            # 转换为列表并处理空值
            values = [tuple(None if pd.isna(val) else val for val in row)
                      for row in processed_data.values]

            extras.execute_batch(cursor, sql, values)
            self.db.conn.commit()
            logging.info(f"Successfully inserted {len(values)} rows into {table}")

        except Exception as e:
            logging.error(f"Error inserting data into {table}: {e}")
            logging.error(f"Data columns: {data.columns.tolist()}")
            if hasattr(e, 'message'):
                logging.error(f"MemFire Error: {e.message}")
            self.db.conn.rollback()
        finally:
            if 'cursor' in locals():
                cursor.close()

    def get_main_body(self, q, kind):
        data = get_all_main_body(q, kind, self.cookie)
        data = data.reset_index(drop=True).astype(str).drop_duplicates()
        data.to_csv(self.main_body_filepath, encoding="utf_8_sig")

        # 添加话题和搜索类型
        data['topic'] = q
        data['search_type'] = kind
        self.save_to_db('main_content', data)

    def get_comments_level_one(self):
        data_list = []
        main_body = pd.read_csv(self.main_body_filepath, index_col=0)

        logging.info(f"主体内容一共有{main_body.shape[0]:5d}个，现在开始解析...")

        for ix in track(range(main_body.shape[0]), description=f"解析中..."):
            try:
                uid = main_body.iloc[ix]["uid"]
                mid = main_body.iloc[ix]["mid"]
                final_file_path = f"{self.comments_level_1_dirpath}{uid}_{mid}.csv"

                if os.path.exists(final_file_path):
                    data = pd.read_csv(final_file_path)
                    if not data.empty:
                        data_list.append(data)
                        self.save_to_db('comments_level_one', data)
                        continue

                data = get_all_level_one(uid=uid, mid=mid, cookie=self.cookie)
                if not data.empty:
                    data.drop_duplicates(inplace=True)
                    data.to_csv(final_file_path, encoding="utf_8_sig")
                    data_list.append(data)
                    self.save_to_db('comments_level_one', data)
            except Exception as e:
                logging.error(f"Error processing comment for uid={uid}, mid={mid}: {e}")
                continue

        if data_list:
            data = pd.concat(data_list).reset_index(drop=True).astype(str).drop_duplicates()
            data.to_csv(self.comments_level_1_filename)

    def get_comments_level_two(self):
        data_list = []
        comments_level_1_data = pd.read_csv(self.comments_level_1_filename, index_col=0)

        logging.info(f"一级评论一共有{comments_level_1_data.shape[0]:5d}个，现在开始解析...")

        for ix in track(range(comments_level_1_data.shape[0]), description=f"解析中..."):
            try:
                main_body_uid = comments_level_1_data.iloc[ix]["main_body_uid"]
                mid = comments_level_1_data.iloc[ix]["mid"]
                final_file_path = f"{self.comments_level_2_dirpath}{main_body_uid}_{mid}.csv"

                if os.path.exists(final_file_path):
                    data = pd.read_csv(final_file_path)
                    if not data.empty:
                        data_list.append(data)
                        self.save_to_db('comments_level_two', data)
                        continue

                data = get_all_level_two(uid=main_body_uid, mid=mid, cookie=self.cookie)
                if not data.empty:
                    data.drop_duplicates(inplace=True)
                    data.to_csv(final_file_path, encoding="utf_8_sig")
                    data_list.append(data)
                    self.save_to_db('comments_level_two', data)
            except Exception as e:
                logging.error(f"Error processing comment for uid={main_body_uid}, mid={mid}: {e}")
                continue

        if data_list:
            data = pd.concat(data_list).reset_index(drop=True).astype(str).drop_duplicates()
            data.to_csv(self.comments_level_2_filename)


def run_parser():
    # Database configuration
    db_config = {
        'host': '101.132.80.183',
        'port': 5433,
        'user': 'zzsthere',
        'password': '20020925Aa',
        'database': 'dbf72a0c3d7d054ef39b98488f2995d159zz'
    }

    # Your cookie value
    cookie = "ALF=02_1735982031; ALF=02_1735982029; Apache=9933642903213.377.1733390391236; SCF=AryA5ulGoQutM0Brn5JuaBLnC_Er88u_COtFFNpTgLU0elCInD4xyZHHjh1TCDQB4bYtCgF1qyBz3hKZqvibV-0.; SINAGLOBAL=9933642903213.377.1733390391236; SUB=_2A25KVR6eDeRhGeNL6FER8yfKyDmIHXVpKx5WrDV8PUNbmtAYLULTkW9NSQBhVRNarPa140tUt-wCaJqdOpaxj-3d; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF1gg6yzM5Kyniie2qDfrg45NHD95QfSKe0ehe4SoefWs4DqcjzwrD0UsyLMJ-t; ULV=1733390391237:1:1:1:9933642903213.377.1733390391236:; WBPSESS=Dt2hbAUaXfkVprjyrAZT_AlCh9ppinvkix2th9eLuRvb6Krpe8IbdB9lY2QaNnkGfA-kOClRSFQrCefsBiDFvh8mANrKwGm-1FBB36PGz4MQNPMPe2D8oJAhihGdadvwfzk_YY64gKVnHUPYtL44DsxIFwAoxTXcX-bPV5xG1BNtVxBcIZxHYG0N0qeEzbEnab9qDGoOtiuwzSXcCrJxdg==; XSRF-TOKEN=gS5mhgtp1i-w1jPHDqRmydle; _s_tentry=weibo.com"  # 设置你的cookie

    # 初始化数据库连接
    db_connection = MemFireConnection(**db_config)

    try:
        # 连接数据库
        db_connection.connect()

        print("\n=== 微博话题爬虫 (MemFire版) ===")
        topic = input("请输入要搜索的话题 (例如: #福州大学考研#): ")
        if not topic.startswith('#'):
            topic = f"#{topic}#"

        print("\n请选择搜索类型:")
        print("1. 综合")
        print("2. 实时")
        print("3. 热门")
        print("4. 高级")

        type_map = {
            "1": "综合",
            "2": "实时",
            "3": "热门",
            "4": "高级"
        }

        while True:
            choice = input("请输入选项 (1-4): ")
            if choice in type_map:
                search_type = type_map[choice]
                break
            print("无效选项，请重新输入!")

        print(f"\n开始爬取话题: {topic}")
        print(f"搜索类型: {search_type}")

        # 创建爬虫实例并执行爬取
        wbparser = WBParser(cookie, db_connection)
        wbparser.get_main_body(topic, search_type)
        wbparser.get_comments_level_one()
        wbparser.get_comments_level_two()

        print("\n爬取完成! 数据已保存到数据库中.")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        print("爬取过程中出现错误，请检查网络连接、数据库配置和cookie是否有效。")
        logging.error(f"Detailed error: {str(e)}", exc_info=True)
    finally:
        db_connection.close()


if __name__ == "__main__":
    run_parser()