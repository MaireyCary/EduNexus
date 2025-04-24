from flask import Blueprint, request, jsonify, make_response
from .services import ExamResultService
import logging

# 创建蓝图
bp = Blueprint('exam_result_analysis', __name__)

# 初始化服务
service = ExamResultService()

# 配置日志
logger = logging.getLogger(__name__)


@bp.route('/download/exam-analysis-template', methods=['GET'])
def download_score_template():
    """成绩表模板下载接口"""
    try:
        logger.info("用户下成绩表模板")
        return service.download_template()
    except Exception as e:
        logger.error(f"成绩表模板下载接口错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "solution": "请联系系统管理员确认模板文件已正确放置"
        }), 404


@bp.route('/upload/exam_results', methods=['POST'])
def upload_exam_results():
    """上传考试成绩 Excel 文件"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({"error": "未找到上传的文件"}), 400
        file = request.files['file']
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({"error": "上传的文件为空"}), 400
        # 获取班级名称
        class_name = request.form.get('class_name')
        # 调用服务方法上传文件
        success = service.upload_exam_results(file, class_name)
        if success:
            return jsonify({"status": "success", "message": "考试成绩文件上传成功"}), 200
        else:
            return jsonify({"error": "考试成绩文件上传失败"}), 500
    except Exception as e:
        logger.error(f"上传考试成绩文件时发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route('/get/classes', methods=['POST'])
def get_classes():
    """考试名称获取接口"""
    try:
        # 获取带班级信息的考试数据
        logger.info("用户获取班级名称")
        classes_data = service.get_classes()
        return jsonify({"classes": classes_data}), 200

    except Exception as e:
        logger.error(f"班级名称获取失败: {str(e)}")
        return jsonify({"error": "服务暂时不可用"}), 500


@bp.route('/get/classes_data', methods=['POST'])
def get_classes_data():
    """班级考试成绩数据获取接口"""
    try:
        # 参数基础校验
        if not request.is_json:
            return jsonify({"error": "请求格式应为JSON"}), 400

        data = request.get_json()
        if 'classes' not in data:
            return jsonify({"error": "缺少班级名称参数"}), 400

        classes_param = data['classes']
        if isinstance(classes_param, dict):
            logger.warning("接收到的班级参数为字典类型，尝试进行转换处理")
            className = classes_param.get('className')
            if className:
                classes_param = f"{className}.json"
            else:
                return jsonify({"error": "字典中未获取到有效的班级名称，无法转换为正确格式"}), 400

        # 获取考试数据
        logger.info("用户获取班级考试成绩数据")
        classes_data = service.get_classes_data(classes_param)

        return jsonify({
            "status": "success",
            "exam": data['classes'],
            "exam_result_analysis": classes_data
        }), 200

    except ValueError as e:
        logger.error(f"值错误: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"接口异常: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500


@bp.route('/download/report', methods=['POST'])
def download_report():
    """下载考试报告"""
    try:
        # 参数基础校验
        if not request.is_json:
            return jsonify({"error": "请求格式应为JSON"}), 400

        classes = request.get_json()
        if 'classes' not in classes:
            return jsonify({"error": "缺少考试名称参数"}), 400

        # 获取考试报告
        logger.info("用户下载班级考试报告")
        classes_report = service.download_report(classes['classes'])
        return classes_report
    except Exception as e:
        logger.error(f"下载班级考试报告失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"下载失败: {str(e)}"}), 500



