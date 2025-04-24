import logging
from .routes import bp
from flask_cors import CORS  # 导入 CORS

def init_app(app):
    """
    请假模块初始化函数
    :param app: Flask应用实例
    """
    # 配置模块日志
    logger = logging.getLogger(__name__)

    try:
        # 注册蓝图
        app.register_blueprint(bp, url_prefix='/leave')

        # 启用 CORS
        CORS(app)

        logger.info('请假模块初始化完成')
    except Exception as e:
        logger.error(f'请假模块初始化失败: {str(e)}', exc_info=True)
        raise