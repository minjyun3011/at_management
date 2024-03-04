"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

application = get_wsgi_application()

import os

# チルダを絶対パスに展開する
log_file_path = '/Users/satoso/Python/at_management/project/logs/file.log'
logger = logging.getLogger(__name__)
# ログファイルを設定する
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # ファイルハンドラーを追加
        logging.StreamHandler()  # コンソールハンドラー（任意）
    ]
)

def my_function():
    # 例: DEBUGレベルのログメッセージを記録する
    logger.debug('This is a debug message')
