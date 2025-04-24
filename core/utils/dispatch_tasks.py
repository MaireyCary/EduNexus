import logging
import os

from modules.course_scheduling.services import SchedulingService
from modules.attendance_analysis.services import AttendanceService
from modules.exam_scheduling.services import ExamService
from modules.exam_result_analysis.services import ExamResultService
from modules.leave_approval_system.services import LeaveService


class DispatchTasks:
    def __init__(self):
        """任务派遣器初始化"""
        self.logger = logging.getLogger(__name__)
        # 依赖注入
        self.course_scheduling = SchedulingService()
        self.attendance_analysis = AttendanceService()
        self.exam_scheduling = ExamService()
        self.exam_result_analysis = ExamResultService()
        self.leave_approval_system = LeaveService()
        # 模块路径声明
        self.course_module = os.path.join('modules', 'course_scheduling')
        self.attendance_module = os.path.join('modules', 'attendance_analysis')
        self.leave_approval_module = os.path.join('modules', 'leave_approval_system')
        self.exam_module = os.path.join('modules', 'exam_scheduling')
        self.exam_result_module = os.path.join('modules', 'exam_result_analysis')

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

    def upload_exam(self):
        """执行考试发布任务"""
        try:
            # 调用考试时间安排服务
            exam_schedule = ExamService.generate_exam_json_from_excel(self.exam_scheduling)
            return exam_schedule

        except Exception as e:
            self.logger.error(f"排课任务执行失败: {str(e)}")
            return False

    def upload_exam_result(self, file):
        """执行考试成绩上传任务"""
        try:
            # 调用考试成绩上传服务
            exam_result = ExamResultService.upload_exam_results(self.exam_result_analysis, file)
            class_name = file.filename.split("考试成绩表")[0].strip()
            # 返回结果文件路径
            result_file = os.path.join(self.exam_result_module, "exam_reports", f'{class_name}.xlsx')
            if exam_result:
                return result_file
            return False
        except Exception as e:
            self.logger.error(f"考试成绩上传任务执行失败: {str(e)}")
            return False

    def download_exam_result(self, class_name):
        """执行考试成绩下载任务"""
        try:
            # 获取目标文件
            result_file = os.path.join(self.exam_result_module, 'exam_reports', f'{class_name}.xlsx')
            if not os.path.exists(result_file):
                raise FileNotFoundError("该班级考试成绩文档不存在")
            return result_file
        except Exception as e:
            self.logger.error(f"下载考试成绩文档错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")

    def leave_approval(self, ids, names):
        """执行请假任务"""
        try:
            """根据ID和姓名验证并返回有效学号列表"""
            records = LeaveService.load_leave_records(self.leave_approval_system)
            self.logger.info(f"{ids},{names}")
            valid_ids = []

            for record in records:
                if record['id'] in ids or record['name'] in names:
                    valid_ids.append(record['id'])
            self.logger.info(f"匹配到的学号记录 IDs:{valid_ids}")
            if not valid_ids:
                self.logger.warning(f"未找到匹配的学号记录 IDs:{ids} Names:{names}")
                return []

            # 调用请假服务
            approval_results = LeaveService.change_status_to_approved(self.leave_approval_system, valid_ids)
            # 返回审批结果
            return approval_results
        except Exception as e:
            self.logger.error(f"请假任务执行失败: {str(e)}")
            return []
