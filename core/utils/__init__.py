from .instruction_analyzer import InstructionAnalyzer
from .dispatch_tasks import DispatchTasks
from modules import attendance_analysis, course_scheduling, exam_scheduling, exam_result_analysis, leave_approval_system

__all__ = [
    'InstructionAnalyzer',
    'DispatchTasks',
    'attendance_analysis',
    'leave_approval_system',
    'course_scheduling', 
    'exam_scheduling',
    'exam_result_analysis'
]
