# 打包Python脚本

## 一、Windows

### 1. 使用PyInstaller打包脚本：

```sh
pyinstaller --onefile --noconsole uploadtocos.py
```

### 3. 在Typora中配置上传命令

在Typora的配置中，将上传图片的命令设置为带有云存储路径参数的可执行文件。例如：

```sh
"D:/path_to_executable/uploadtocos.exe" --file
```

这样，Typora在上传图片时会调用打包后的可执行文件，并将上传路径作为参数传递，从而实现灵活的路径配置。

##  二、Linux

使用 PyInstaller 可以将 Python 脚本打包成独立的可执行文件。然而，PyInstaller 打包出来的可执行文件是针对当前操作系统和架构的。这意味着你在 Windows 上打包的 `.exe` 文件不能在 Linux 上运行，同样地，在 Linux 上打包的文件也不能在 Windows 上运行。

为了在 Linux 上运行 PyInstaller 打包的可执行文件，需要在 Linux 上进行打包。下面是如何在 Linux 上使用 PyInstaller 打包和运行你的 `uploadtocos.py` 脚本的步骤。

### 在 Linux 上使用 PyInstaller 打包

#### 1. 安装 PyInstaller

首先，确保你已经安装了 Python 和 pip。然后使用 pip 安装 PyInstaller：

```sh
pip install pyinstaller
```

#### 2. 编写你的 `uploadtocos.py` 脚本

确保你的脚本是适合在 Linux 上运行的。以下是你的脚本（假设已经做了适当的修改）：

```python
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
        print(file_url)


if __name__ == "__main__":
    main()
```

#### 3. 使用 PyInstaller 打包

在你的脚本所在的目录下运行以下命令：

```shell
pyinstaller --onefile uploadtocos.py
```

这将生成一个独立的可执行文件，在 `dist` 目录下可以找到 `uploadtocos` 文件（在 Linux 上没有 `.exe` 扩展名）。

#### 4. 运行打包后的可执行文件

你可以直接运行生成的可执行文件：

```sh
./dist/uploadtocos --file "path_to_your_image.jpg"
```

确保环境变量已设置，例如：

```sh
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_REGION=your_region
export COS_BUCKET=your_bucket
export COS_UPLOAD_PATH=your_upload_path
```

### 在 Linux 上运行的完整流程

1. **设置环境变量**：

   ```sh
   export COS_SECRET_ID=your_secret_id
   export COS_SECRET_KEY=your_secret_key
   export COS_REGION=your_region
   export COS_BUCKET=your_bucket
   export COS_UPLOAD_PATH=your_upload_path
   ```

2. **运行可执行文件**：

   ```sh
   ./dist/uploadtocos --file "path_to_your_image.jpg"
   ```

通过这些步骤，你可以在 Linux 上打包并运行你的 `uploadtocos.py` 脚本。确保所有依赖项都在打包环境中安装，并且在打包和运行时都设置了适当的环境变量。