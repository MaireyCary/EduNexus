import logging
import os

from flask import Blueprint, request, jsonify
from .services import SchedulingService

# 创建蓝图
bp = Blueprint('course-scheduling', __name__)

# 初始化服务
service = SchedulingService()

# 配置日志
logger = logging.getLogger(__name__)


@bp.route('/download/teacher-template', methods=['GET'])
def download_teacher_template():
    """教师表模板下载接口"""
    try:
        logger.info("用户下载教师表模板")
        return service.download_example_template()
    except Exception as e:
        logger.error(f"教师表模板下载接口错误: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "solution": "请联系系统管理员确认模板文件已正确放置"
        }), 404


@bp.route('/upload/teacher', methods=['POST'])
def upload_teacher():
    """教师表上传接口"""
    if 'teacherFile' not in request.files:
        logger.warning('教师表上传请求中未包含文件')
        return jsonify({'error': '请选择要上传的教师表文件'}), 400

    file = request.files['teacherFile']
    if file.filename == '':
        logger.warning('教师表上传请求中文件名为空')
        return jsonify({'error': '无效的文件名'}), 400

    try:
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise ValueError("只支持Excel文件(.xlsx, .xls)")

        service.upload_teacher(file)
        logger.info(f'教师表上传成功: {file.filename}')
        return jsonify({
            'message': '教师表上传成功',
            'filename': file.filename
        }), 200
    except Exception as e:
        logger.error(f"教师表上传失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"上传失败: {str(e)}"}), 500


@bp.route('/upload/courses', methods=['POST'])
def upload_courses():
    """课表上传接口"""
    if 'file' not in request.files:
        logger.warning('课表上传请求中未包含文件')
        return jsonify({'error': '请选择要上传的课表文件'}), 400

    file = request.files['file']
    if file.filename == '':
        logger.warning('课表上传请求中文件名为空')
        return jsonify({'error': '无效的文件名'}), 400

    try:
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.zip')):
            raise ValueError("只支持Excel或Zip文件(.xlsx, .xls, .zip)")

        service.upload_courses(file)
        logger.info(f'课表上传成功: {file.filename}')
        return jsonify({
            'message': '课表上传成功',
            'filename': file.filename
        }), 200
    except Exception as e:
        logger.error(f"课表上传失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"上传失败: {str(e)}"}), 500


@bp.route('/arrange', methods=['POST'])
def arrange():
    """排课接口"""
    try:
        result = service.arrange_courses()
        logger.info('排课成功完成')
        return jsonify({
            'message': '排课成功',
            'download_url': '/course-scheduling/download/result',
            'excel': result
        }), 200
    except Exception as e:
        logger.error(f"排课失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"排课失败: {str(e)}"}), 500


@bp.route('/download/result', methods=['GET'])
def download_result():
    """下载排课结果"""
    try:
        result_file = os.path.join(service.result_path, '排课结果.zip')
        if not os.path.exists(result_file):
            logger.error('排课结果文件不存在')
            return jsonify({'error': '排课结果不存在，请先执行排课'}), 404
        logger.info('用户下载排课结果')
        return service.download_result()
    except Exception as e:
        logger.error(f"下载排课结果失败: {str(e)}", exc_info=True)
        return jsonify({'error': f"下载失败: {str(e)}"}), 500
