from flask import Blueprint, jsonify, request,send_file
from .services import ExamService
import logging

# 创建蓝图
bp = Blueprint('exam_scheduling', __name__)

# 初始化服务
service = ExamService()

# 配置日志
logger = logging.getLogger(__name__)

@bp.route('/download/exam_template', methods=['GET'])
def download_template():
    """考试安排表模板下载接口"""
    try:
        logger.info("用户下考试安排表模板")
        return service.download_template()
    except Exception as e:
        logger.error(f"考试安排表模板下载接口错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "solution": "请联系系统管理员确认模板文件已正确放置"
        }), 404



@bp.route('/get/exam', methods=['GET'])
def get_week():
    """考试信息获取接口"""
    try:
        # 获取带班级信息的周数据
        logger.info("用户获取考试信息")
        exam_data = service.get_exam_data()
        if exam_data:
            return jsonify({"exam_data": exam_data}), 200
        else:
            return jsonify({"exam_data": "考试数据尚未录入"}), 200

    except Exception as e:
        logger.error(f"考试信息获取失败: {str(e)}")
        return jsonify({"error": "服务暂时不可用"}), 500


@bp.route('/upload/courses', methods=['POST'])
def upload_courses():
    """处理课表上传"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "未找到上传的文件"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400
        logger.info("用户上传课表文件")

        service.upload_courses(file)
        result = service.generate_exam_json_from_excel()

        if result:
            return jsonify({"message": "文件上传成功"}), 200
    except Exception as e:
        logger.error(f"上传错误: {str(e)}", exc_info=True)
        return jsonify({"error": f"处理失败: {str(e)}"}), 500