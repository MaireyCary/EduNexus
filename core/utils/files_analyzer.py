import logging
import os
import shutil

from modules.course_scheduling.utils import excel


class FilesAnalyzer:
    def __init__(self):
        """文件分析器初始化"""
        self.logger = logging.getLogger(__name__)
        # 初始化模块路径
        self.schedule_teacher_path = os.path.join("modules", "course_scheduling", "tmp", "teacher")
        self.schedule_courses_path = os.path.join("modules", "course_scheduling", "tmp", "courses")

        # 确保目录存在
        os.makedirs(self.schedule_teacher_path, exist_ok=True)
        os.makedirs(self.schedule_courses_path, exist_ok=True)

    def course_schedule_analyser(self, files):
        """分析并保存排课模块文件"""
        try:
            for file in files:
                filename = file.filename.lower()
                # 处理教师表文件
                if "签课计划" in filename and filename.endswith(('.xlsx', '.xls')):
                    try:
                        # 清空目录
                        if os.path.exists(self.schedule_teacher_path):
                            shutil.rmtree(self.schedule_teacher_path)
                        os.makedirs(self.schedule_teacher_path)

                        # 保存文件
                        save_path = os.path.join(self.schedule_teacher_path, file.filename)
                        file.save(save_path)
                    except Exception as e:
                        self.logger.error(f"教师表上传错误: {str(e)}", exc_info=True)
                        continue
                # 处理课表文件
                elif filename.endswith('.zip'):
                    try:
                        # 清空目录
                        if os.path.exists(self.schedule_courses_path):
                            shutil.rmtree(self.schedule_courses_path)
                        os.makedirs(self.schedule_courses_path)

                        # 保存文件
                        save_path = os.path.join(self.schedule_courses_path, file.filename)
                        file.save(save_path)

                        # 解压处理
                        if file.filename.lower().endswith('.zip'):
                            excel.get_zip(self.schedule_courses_path)
                    except Exception as e:
                        self.logger.error(f"课表上传错误: {str(e)}", exc_info=True)
                        continue
                else:
                    continue
            return True
        except Exception as e:
            self.logger.error(f"文件处理失败: {str(e)}")
            raise
        