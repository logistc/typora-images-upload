import os
import sys
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import argparse
import logging

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

# 获取上传图片类型
def get_content_type(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    if ext == '.jpg' or ext == '.jpeg':
        return 'image/jpeg'
    elif ext == '.png':
        return 'image/png'
    elif ext == '.gif':
        return 'image/gif'
    elif ext == '.bmp':
        return 'image/bmp'
    else:
        return 'application/octet-stream'


def upload_to_cos(secret_id, secret_key, region, bucket_name, local_file_path):
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    file_name = os.path.basename(local_file_path)

    # 不能将参数 upload_path 用外部参数 --upload_path 设置，Typora不支持，报错。
    upload_path = os.getenv('COS_UPLOAD_PATH', '')
    # 参数 upload_path 只能从系统环境变量获取。在系统环境变量 COS_UPLOAD_PATH 中设置以/结尾，例如 noteimages/

    # 确保参数 upload_path 以斜杠结尾，除非它是根目录
    if upload_path and not upload_path.endswith('/'):
        upload_path += '/'

    upload_path = f"{upload_path}{file_name}"
    content_type = get_content_type(file_name)

    with open(local_file_path, 'rb') as f:
        response = client.put_object(
            Bucket=bucket_name,
            Body=f,
            Key=upload_path,
            StorageClass='STANDARD',
            ContentType=content_type
        )

    file_url = f"https://{bucket_name}.cos.{region}.myqcloud.com/{upload_path}"
    return file_url


def main():
    parser = argparse.ArgumentParser(description="Upload images to Tencent Cloud COS and generate Markdown links")
    parser.add_argument('--file', required=True, nargs='+', help="Local image file paths")

    args = parser.parse_args()

    secret_id = os.getenv('COS_SECRET_ID')
    secret_key = os.getenv('COS_SECRET_KEY')
    region = os.getenv('COS_REGION')
    bucket = os.getenv('COS_BUCKET')

    if not all([secret_id, secret_key, region, bucket]):
        print("Please set the environment variables: COS_SECRET_ID, COS_SECRET_KEY, COS_REGION, COS_BUCKET")
        sys.exit(1)

    for file_path in args.file:
        file_url = upload_to_cos(secret_id, secret_key, region, bucket, file_path)
        # markdown_link = f"![{os.path.basename(file_path)}]({file_url})"
        # Typora只需要图片上传后的URL并自动在Markdown中插入Markdown格式的图片引用![名称](图床链接)
        # 不要返回Markdown格式的图片链接否则报错。
        print(file_url)


if __name__ == "__main__":
    main()
