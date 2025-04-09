import json
import logging
import os

from flask import send_from_directory

logger = logging.getLogger(__name__)


class ExamService:
    def __init__(self):
        # 获取模块绝对路径
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # 初始化路径
        self.data_path = os.path.join(module_dir, "example_data")
        self.excel_path = os.path.join(module_dir, "excel")

        # 确保目录存在
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.excel_path, exist_ok=True)

        logger.info(f"考勤服务初始化完成，工作目录: {module_dir}")

    def get_exam_data(self):
        """获取前端指定格式的考试信息数据"""
        try:
            # 数据文件校验
            if not os.path.exists(self.data_path):
                raise FileNotFoundError("考试信息数据尚未录入")

            # 获取考试信息数据文件
            filename = os.path.join(self.data_path, os.listdir(self.data_path)[0])

            # 读取数据文件
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data
        except Exception as e:
            logger.error(f"考试信息数据异常: {str(e)}", exc_info=True)
            raise

    def download_exam_data(self):
        """下载考试信息文档"""
        try:
            # 数据文件校验
            if not os.path.exists(self.excel_path):
                raise FileNotFoundError("考试信息文档尚未录入")

            return send_from_directory(
                directory=self.excel_path,
                path=f'{os.listdir(self.excel_path)[0]}',
                as_attachment=True,
                download_name='期末考试信息.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            logger.error(f"下载考试信息文档错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")
