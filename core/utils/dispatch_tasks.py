import logging
import os

from modules.course_scheduling.services import SchedulingService
from modules.attendance_analysis.services import AttendanceService
from modules.exam_scheduling.services import ExamService


class DispatchTasks:
    def __init__(self):
        """任务派遣器初始化"""
        self.logger = logging.getLogger(__name__)
        # 依赖注入
        self.course_scheduling = SchedulingService()
        self.attendance_analysis = AttendanceService()
        self.exam_scheduling = ExamService()
        # 模块路径声明
        self.course_module = os.path.join('modules', 'course_scheduling')
        self.attendance_module = os.path.join('modules', 'attendance_analysis')
        self.exam_module = os.path.join('modules', 'exam_scheduling')

    def arrange_course(self):
        """执行排课任务"""
        try:
            # 调用排课服务
            arrangement_results = SchedulingService.arrange_courses(self.course_scheduling)
            
            # 返回结果文件路径
            result_file = os.path.join(self.course_module, "result", '排课结果.zip')
            if arrangement_results:
                return result_file
            return False
            
        except Exception as e:
            self.logger.error(f"排课任务执行失败: {str(e)}")
            return False

    def download_attendance(self, week):
        """执行考勤任务"""
        try:
            # 获取目标文件
            result_file = os.path.join(self.attendance_module, 'results', f'第{week}周.xlsx')
            if not os.path.exists(result_file):
                raise FileNotFoundError("考勤文档不存在")
            return result_file
        except Exception as e:
            self.logger.error(f"下载考勤文档错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")

    def download_exam(self):
        """执行考试任务"""
        try:
            # 获取目标文件
            result_file = os.path.join(self.exam_module, 'excel', '期末考试信息.xlsx')
            if not os.path.exists(result_file):
                raise FileNotFoundError("考试文档不存在")
            return result_file
        except Exception as e:
            self.logger.error(f"下载考试文档错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")
