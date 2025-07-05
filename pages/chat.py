import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_main import show_main_app, Config, setup_logging

# 설정 및 로거 초기화
config = Config()
logger = setup_logging()

# 메인 앱 실행
show_main_app(config, logger) 