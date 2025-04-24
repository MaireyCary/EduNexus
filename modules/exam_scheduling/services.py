import logging
import os
import pandas as pd
import json
import shutil
from .tools import test12, excel2
from flask import send_from_directory

logger = logging.getLogger(__name__)


class ExamService:
    def __init__(self):
        # 获取模块绝对路径
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # 初始化路径
        self.data_path = os.path.join(module_dir, "example_data")
        self.output_path = os.path.join(module_dir, "example_data")
        self.excel_file_path = os.path.join(module_dir, "excel_data")
        self.excel_path = os.path.join(module_dir, "excel")

        # 确保目录存在
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.excel_file_path, exist_ok=True)
        os.makedirs(self.excel_path, exist_ok=True)

        logger.info(f"考勤服务初始化完成，工作目录: {module_dir}")

    def get_exam_data(self):
        """获取前端指定格式的考试信息数据"""
        try:
            # 数据文件校验
            if not os.path.exists(self.data_path):
                return False

            # 检查目录是否为空
            files = os.listdir(self.data_path)
            if not files:
                return False

            # 获取考试信息数据文件
            filename = os.path.join(self.data_path, os.listdir(self.data_path)[0])

            # 读取数据文件
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data
        except Exception as e:
            logger.error(f"考试信息数据异常: {str(e)}", exc_info=True)
            raise

    def download_template(self):
        """下载考试安排模板文件"""
        try:
            # 确认样表文件路径
            template_file = '考试安排样表.xlsx'
            template_path = os.path.join(self.excel_path, template_file)

            # 验证文件是否存在
            if not os.path.exists(template_path):
                logger.error(f"考试安排表样表不存在，路径: {template_path}")
                raise FileNotFoundError("考试安排样表文件未配置，请联系管理员")

            logger.info(f"准备下载考试安排样表: {template_path}")

            # 返回文件下载响应
            return send_from_directory(
                directory=self.excel_path,
                path=template_file,
                as_attachment=True,
                download_name='考试安排样表.xlsx',  # 前端显示的下载文件名
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            logger.error(f"考试安排样表下载失败: {str(e)}", exc_info=True)
            raise Exception(f"模板下载服务暂时不可用: {str(e)}")

    def generate_exam_json_from_excel(self):
        """从 Excel 文件生成考试信息的 JSON 数据"""
        try:
            # 检查 Excel 文件目录
            if not os.path.exists(self.excel_file_path):
                raise FileNotFoundError("Excel 文件目录不存在")

            # 获取 Excel 文件
            excel_files = [f for f in os.listdir(self.excel_file_path) if f.endswith('.xlsx') or f.endswith('.xls')]
            if not excel_files:
                raise FileNotFoundError("未找到 Excel 文件")
            excel_file = os.path.join(self.excel_file_path, excel_files[0])

            # 读取 Excel 文件
            df = pd.read_excel(excel_file)

            # 查找表头行
            required_columns = {'班级名称', '课程名称', '授课教师'}
            header_row = excel2.ExcelDataProcessor.find_header_row(df, required_columns)
            if header_row is None:
                raise KeyError("未找到包含所有必需列名的行")

            # 设置表头
            df.columns = df.iloc[header_row]
            df = df[header_row + 1:]
            df = df.reset_index(drop=True)

            # 使用 excel2 中的方法获取班级与课程的映射关系
            class_course_mapping = excel2.ExcelDataProcessor.get_class_course_mapping(df)

            # 创建 test12 中的 ExamScheduler 实例
            scheduler = test12.ExamScheduler(class_course_mapping)
            scheduler.class_course_dict = class_course_mapping
            scheduler._preprocess_data()

            # 运行遗传算法生成最佳考试安排
            best_schedule = scheduler.run()

            # 生成 JSON 文件
            output_json_path = os.path.join(self.output_path, "exam_schedule.json")
            scheduler.generate_json_schedule(best_schedule, output_json_path)

            logger.info(f"JSON 文件已生成: {output_json_path}")
            return True
        except Exception as e:
            logger.error(f"生成考试信息 JSON 数据时出错: {str(e)}", exc_info=True)
            raise

    def upload_courses(self, file):
        """处理课表上传"""
        try:
            # 清空目录
            if os.path.exists(self.excel_file_path):
                shutil.rmtree(self.excel_file_path)
            os.makedirs(self.excel_file_path)

            # 保存文件
            save_path = os.path.join(self.excel_file_path, file.filename)
            file.save(save_path)
            return True
        except Exception as e:
            logger.error(f"上传错误: {str(e)}", exc_info=True)
            raise Exception(f"处理失败: {str(e)}")
