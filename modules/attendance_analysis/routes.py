from flask import Blueprint, request, jsonify, make_response
from .services import AttendanceService
import logging

# 创建蓝图
bp = Blueprint('attendance_analysis', __name__)

# 初始化服务
service = AttendanceService()

# 配置日志
logger = logging.getLogger(__name__)


@bp.route('/get/week', methods=['GET'])
def get_week():
    """考勤周数获取接口"""
    try:
        # 获取带班级信息的周数据
        logger.info("用户获取考勤周数")
        weeks_data = service.get_available_weeks()
        return jsonify({"weeks": weeks_data}), 200

    except Exception as e:
        logger.error(f"考勤周数获取失败: {str(e)}")
        return jsonify({"error": "服务暂时不可用"}), 500


@bp.route('/get/data', methods=['POST'])
def get_data():
    """考勤数据获取接口"""
    try:
        # 参数基础校验
        if not request.is_json:
            return jsonify({"error": "请求格式应为JSON"}), 400

        data = request.get_json()
        if 'week' not in data:
            return jsonify({"error": "缺少周数参数"}), 400

        # 获取周数据
        logger.info("用户获取考勤数据")
        week_data = service.get_data(data['week'])

        return jsonify({
            "status": "success",
            "week": data['week'],
            "data": week_data
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"接口异常: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route('/download/result', methods=['POST'])
def download_result():
    """下载考勤文档"""
    try:
        # 参数基础校验
        if not request.is_json:
            return jsonify({"error": "请求格式应为JSON"}), 400

        week = request.get_json()
        if 'week' not in week:
            return jsonify({"error": "缺少周数参数"}), 400

        # 获取考勤文档
        logger.info("用户下载考勤文档")
        week_excel = service.download_result(week['week'])
        return week_excel
    except Exception as e:
        logger.error(f"下载考勤文档失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"下载失败: {str(e)}"}), 500
