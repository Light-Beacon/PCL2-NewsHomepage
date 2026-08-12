import os
import sys

import boto3
import requests
from bs4 import BeautifulSoup
from botocore.config import Config

from minecraft_version import MCVM, MinecraftVersion


# ============================================================
# 配置
# ============================================================

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0 Safari/537.36"
)


# ============================================================
# R2
# ============================================================

def create_r2_client():
    account_id = os.environ["R2_ACCOUNT_ID"]
    access_key = os.environ["R2_ACCESS_KEY_ID"]
    secret_key = os.environ["R2_SECRET_ACCESS_KEY"]

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=Config(
            signature_version="s3v4"
        ),
    )


# ============================================================
# 获取更新日志 URL
# ============================================================

def get_change_log_url(version_id: str) -> str:
    version = MCVM.get(version_id)

    if version is None:
        raise ValueError(
            f"MC 版本 {version_id} 不存在"
        )

    url = version.change_log_url

    if not url:
        raise ValueError(
            f"MC 版本 {version_id} 没有更新日志链接"
        )

    #print(f"版本: {version.id}")
    #print(f"更新日志: {url}")

    return url


# ============================================================
# 下载 HTML
# ============================================================

def download_html(url: str) -> str:
    #print("[1/4] 下载 HTML...")

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://www.minecraft.net/",
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    response.encoding = response.apparent_encoding

    return response.text

def find_hero_image(html: str, page_url: str) -> str:
    #print("[2/4] 获取图片路径...")

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    poster = soup.select_one(
        "div.MC_articleHeroA_poster"
    )

    if poster is None:
        raise RuntimeError(
            "找不到 div.MC_articleHeroA_poster"
        )

    img = poster.select_one(
        "picture img"
    )

    if img is None:
        raise RuntimeError(
            "找不到 picture img"
        )

    src = img.get("src")

    if not src:
        raise RuntimeError(
            "img 没有 src 属性"
        )

    from urllib.parse import urljoin

    image_url = urljoin(
        page_url,
        src,
    )

    #print(f"图片: {image_url}")

    return image_url

def download_image(
    image_url: str,
    page_url: str,
) -> tuple[bytes, str]:

    #print("[3/4] 下载图片...")

    headers = {
        "User-Agent": USER_AGENT,
        "Referer": page_url,
        "Accept": (
            "image/avif,image/webp,image/apng,"
            "image/svg+xml,image/*,*/*;q=0.8"
        ),
    }

    response = requests.get(
        image_url,
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    content_type = response.headers.get(
        "Content-Type",
        "application/octet-stream",
    )

    return response.content, content_type

def upload_to_r2(
    data: bytes,
    bucket: str,
    object_key: str,
    content_type: str,
):
    #print("[4/4] 上传 Cloudflare R2...")

    s3 = create_r2_client()
    s3.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=data,
        ContentType=content_type,
    )

def upload_header_image(version):
    if isinstance(version, str):
        version = MCVM.get(version)
    if not isinstance(version, MinecraftVersion):
        raise TypeError()
    change_log_url = version.change_log_url
    html = download_html(
        change_log_url
    )
    image_url = find_hero_image(
        html,
        change_log_url,
    )
    image_data, content_type = download_image(
        image_url,
        change_log_url,
    )
    bucket = "images"
    object_key = f"news/version/{version.major_version}/{version.id}.webp"
    upload_to_r2(
        image_data,
        bucket,
        object_key,
        content_type,
    )
    return f"https://images.bugjump.net/{object_key}"
    

def main():
    if len(sys.argv) != 2:
        print(
            f"用法: {sys.argv[0]} <Minecraft版本号>"
        )
        print()
        print("例如:")
        print(f"  {sys.argv[0]} 26.3")
        print(f"  {sys.argv[0]} 26.3-rc-1")
        sys.exit(1)

    version_id = sys.argv[1]
    version = MCVM.get(version_id)
    if not version:
        raise ValueError('错误：未找到版本')
    url = upload_header_image(version)

    print(f"已上传至{url}")


if __name__ == "__main__":
    main()
