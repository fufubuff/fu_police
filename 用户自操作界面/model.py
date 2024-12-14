from huggingface_hub import snapshot_download

# 指定模型名称和本地保存路径
model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
local_path = "D:/aynz"  # 这里替换为你实际想要保存模型的本地路径，注意路径写法符合系统规范

try:
    # 使用snapshot_download函数下载模型，去掉request_timeout参数
    downloaded_path = snapshot_download(
        repo_id=model_name,
        local_dir=local_path
    )
    print(f"模型已成功下载到 {downloaded_path}")
except Exception as e:
    print(f"模型下载出现错误: {e}")