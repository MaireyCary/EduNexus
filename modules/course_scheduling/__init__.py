import logging
import os

from .routes import bp
from .services import SchedulingService


def init_app(app):
    """
    排课模块初始化函数
    :param app: Flask应用实例
    """
    # 配置模块日志
    logger = logging.getLogger(__name__)

    # 确保临时目录存在
    module_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(module_dir, "result")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # 注册蓝图
        app.register_blueprint(bp, url_prefix='/course-scheduling')

        # 初始化服务实例（挂载到app上下文）
        app.scheduling_service = SchedulingService()

        logger.info('排课模块初始化完成')
    except Exception as e:
        logger.error(f'排课模块初始化失败: {str(e)}', exc_info=True)
        raise
