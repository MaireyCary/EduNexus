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
        
        # 处理文件
        if files:
            file_result = self.files_analyzer.course_schedule_analyser(files)
        else:
            file_result = None

        # 初始化任务派遣器
        dispatcher = DispatchTasks()
        result_files = []
        
        # 执行任务
        for task in tasks:
            try: 
                if task['task_id'] == 'course_scheduling':
                    # 检查是否上传了必要文件
                    if not files:
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

                elif task['task_id'] == 'exam_scheduling':
                    file_path = dispatcher.download_exam()
                    result_files.append(file_path)
                    logger.info("考试导出任务执行完成")
                    
                else:
                    logger.warning(f"未知任务类型: {task['task_id']}")
            except Exception as e:
                logger.error(f"任务执行失败: {str(e)}")
                continue

        return {
            'tasks': tasks,
            'file_result': file_result,
            'result_files': result_files
        }

    
