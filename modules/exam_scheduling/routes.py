from flask import Blueprint, jsonify
from .services import ExamService
import logging

# 创建蓝图
bp = Blueprint('exam_scheduling', __name__)

# 初始化服务
service = ExamService()

# 配置日志
logger = logging.getLogger(__name__)


@bp.route('/get/exam', methods=['GET'])
def get_week():
    """考试信息获取接口"""
    try:
        # 获取带班级信息的周数据
        logger.info("用户获取考试信息")
        exam_data = service.get_exam_data()
        return jsonify({"exam_data": exam_data}), 200

    except Exception as e:
        logger.error(f"考试信息获取失败: {str(e)}")
        return jsonify({"error": "服务暂时不可用"}), 500


@bp.route('/download/result', methods=['GET'])
def download_result():
    """下载考试文档"""
    try:
        # 获取考试文档
        logger.info("用户下载考试文档")
        return service.download_exam_data()
    except Exception as e:
        logger.error(f"下载考试文档失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"下载失败: {str(e)}"}), 500
