import os
import shutil
import zipfile
import logging
import time
import hashlib

from flask import Blueprint, request, jsonify, make_response, send_file
from .services import DispatchService


# 创建蓝图
bp = Blueprint('dispatch_center', __name__)

# 初始化服务
service = DispatchService()

# 配置日志
logger = logging.getLogger(__name__)


@bp.route('/execute', methods=['POST', 'OPTIONS'])
def execute():
    """处理复合指令的任务识别和执行"""
    try:
        # 处理跨域请求
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
            return response

        # 获取指令和文件
        instruction = request.form.get('instruction', '').strip()
        files = request.files.getlist('CourseScheduleFiles')
        logger.info(f"接收指令: {instruction}")
        logger.info(f"接收文件数: {len(files)}")

        if not instruction:
            return jsonify({
                'code': 400,
                'message': '指令不能为空'
            }), 400

        # 处理指令和文件
        result = service.analyze_tasks(instruction, files if files else None)
        
        if not result['tasks']:
            return jsonify({
                'code': 400,
                'message': '未识别到有效任务'
            }), 400

        # 处理结果文件打包
        if result.get('result_files'):
            # 配置结果文件路径
            tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
            os.makedirs(tmp_dir, exist_ok=True)
            
            # 清空缓存文件夹
            for filename in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logger.error(f"清理缓存文件失败: {file_path}, 错误: {str(e)}")

            # 打包结果文件到tmp目录
            zip_path = os.path.join(tmp_dir, 'result_files.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in result['result_files']:
                    if os.path.exists(file_path):
                        # 将结果文件复制到tmp目录
                        dest_path = os.path.join(tmp_dir, os.path.basename(file_path))
                        shutil.copy2(file_path, dest_path)
                        # 添加到zip包
                        zipf.write(dest_path, os.path.basename(dest_path))
            
            # 生成校验token文件
            token = hashlib.md5(f"{time.time()}{os.urandom(4)}".encode()).hexdigest()
            with open(os.path.join(tmp_dir, '.token'), 'w') as f:
                f.write(token)
            
            return jsonify({
                'code': 200,
                'status': True,
                'message': '任务处理成功',
                'data': {
                    'has_file': True,
                    'file_token': token,
                    'tasks': result['tasks'],
                    'original_instruction': instruction
                }
            })

        # 没有结果文件时的返回样式
        return jsonify({
            'code': 200,
            'status': True,
            'message': '任务处理成功',
            'data': {
                'has_file': False,
                'file_token': None,
                'tasks': result['tasks'],
                'original_instruction': instruction
            }
        })
        
    except Exception as e:
        logger.error(f'任务处理异常: {str(e)}')
        return jsonify({
            'code': 500,
            'status': False,
            'message': '服务器内部错误',
            'data': None
        }), 500


@bp.route('/download', methods=['GET', 'OPTIONS'])
def download():
    """提供下载结果文件的接口"""
    # 处理跨域请求
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response

    token = request.args.get('token')
    if not token:
        logger.warning("无token进行访问结果文件下载")
        return jsonify({'code': 400, 'message': '缺少token参数'}), 400
    
    tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
    token_file = os.path.join(tmp_dir, '.token')
    
    # 验证token
    if not os.path.exists(token_file):
        logger.warning("非法token进行访问结果文件下载")
        return jsonify({'code': 403, 'message': '无效token'}), 403
    
    with open(token_file) as f:
        if f.read().strip() != token:
            logger.warning("非法token进行访问结果文件下载")
            return jsonify({'code': 403, 'message': 'token不匹配'}), 403
    
    # 验证通过后提供下载
    file_path = os.path.join(tmp_dir, 'result_files.zip')
    if not os.path.exists(file_path):
        return jsonify({'code': 404, 'message': '文件不存在'}), 404

    logger.info("token校验通过，下载结果文件")
    response = send_file(
        file_path,
        mimetype='application/zip',
        as_attachment=True,
        download_name='任务结果.zip'
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
