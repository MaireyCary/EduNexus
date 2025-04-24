import logging

from typing import Dict, Any
from .utils.instruction_analyzer import InstructionAnalyzer
from .utils.files_analyzer import FilesAnalyzer
from .config import Config
from .utils.dispatch_tasks import DispatchTasks

logger = logging.getLogger(__name__)


class DispatchService:
    def __init__(self):
        self.analyzer = InstructionAnalyzer(
            task_modules=Config.TASK_MODULES,
            time_patterns=Config.TIME_PATTERNS
        )
        self.files_analyzer = FilesAnalyzer()

    def analyze_tasks(self, instruction: str, files=None) -> Dict[str, Any]:
        """分析用户指令并处理文件"""
        logger.info(f"开始分析指令: {instruction}")
        # 分析指令
        tasks = self.analyzer.analyze(instruction)
        logger.info(f"识别到的任务: {tasks}")
        flag = {}
        # 处理文件
        if files:
            flag = self.files_analyzer.course_schedule_analyser(files)

        # 初始化任务派遣器
        dispatcher = DispatchTasks()
        result_files = []
        
        # 执行任务
        for task in tasks:
            try: 
                if task['task_id'] == 'course_scheduling':
                    # 检查是否上传了必要文件
                    if not flag['签课计划']:
                        logger.warning("排课任务需要上传文件，跳过执行")
                        continue
                    file_path = dispatcher.arrange_course()
                    result_files.append(file_path)
                    logger.info("课程安排任务执行完成")
                        
                elif task['task_id'] == 'attendance_analysis':
                    week = task['parameters'].get('week_number')
                    file_path = dispatcher.download_attendance(week)
                    result_files.append(file_path)
                    logger.info("考勤导出任务执行完成")

                elif task['task_id'] == 'leave_approval_system':
                    student_ids = task['parameters'].get('student_ids')
                    student_names = task['parameters'].get('student_names')
                    dispatcher.leave_approval(student_ids, student_names)
                    logger.info("请假审批任务执行完成")

                elif task['task_id'] == 'exam_scheduling':
                    # 检查是否上传了必要文件
                    if not flag['考试安排表']:
                        logger.warning("考试安排任务需要上传文件，跳过执行")
                        continue
                    file_path = dispatcher.upload_exam()
                    # result_files.append(file_path)
                    logger.info("考试信息发布任务执行完成")

                elif task['task_id'] == 'exam_result_analysis':
                    if task['parameters'].get('operation_type') == 'upload':
                        if not flag['考试成绩表']:
                            logger.warning("考试成绩上传任务需要上传文件，跳过执行")
                            continue
                        file_path = dispatcher.upload_exam_result(flag['考试成绩表'])
                        # result_files.append(file_path)
                        logger.info("考试成绩上传任务执行完成")
                    elif task['parameters'].get('operation_type') == 'download':
                        class_name = task['parameters'].get('class_name')
                        file_path = dispatcher.download_exam_result(class_name)
                        result_files.append(file_path)

                    
                else:
                    logger.warning(f"未知任务类型: {task['task_id']}")
            except Exception as e:
                logger.error(f"任务执行失败: {str(e)}")
                continue

        return {
            'tasks': tasks,
            'result_files': result_files
        }

    
