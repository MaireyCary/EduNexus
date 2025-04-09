import logging
from typing import Dict, Any, List


class Config:
    # 模型配置
    MODEL_PATH = "model/multilingual-e5-large"
    MODEL_MAX_LENGTH = 512
    MODEL_BATCH_SIZE = 32

    # 模型参数
    MODEL_NAME = "model/multilingual-e5-large"
    MODEL_DEVICE = "auto"

    # 文本处理配置
    DEFAULT_LANGUAGE = "zh"
    MAX_TEXT_LENGTH = 1000

    # 任务调度配置
    TASK_MODULES: Dict[str, Dict[str, Any]] = {
        "course_scheduling": {
            "name": "课程安排",
            "module_path": "modules.course_scheduling",
            "keywords": [
                "课程", "安排课程", "排课", "课程表", "教学计划",
                "学期课程", "上课安排", "课程计划"
            ],
            "required_params": ["semester"]
        },
        "attendance_analysis": {
            "name": "考勤情况导出",
            "module_path": "modules.attendance_analysis",
            "keywords": [
                "导出考勤", "考勤记录", "考勤报表", "考勤数据",
                "考勤情况", "考勤明细", "考勤报告"
            ],
            "required_params": ["week_number"]
        },
        "exam_scheduling": {
            "name": "考试信息导出",
            "module_path": "modules.exam_scheduling",
            "keywords": [
                "考试安排", "考试时间", "考试科目",
                "考试信息", "考试日程", "考试日程表"
            ],
            "required_params": ["exam_type"]
        }
    }

    # 指令分割配置
    INSTRUCTION_SPLITTERS = [
        "然后", "并且", "接着", "再", "同时",
        "之后", "最后", "下一步", "随后"
    ]

    # 时间相关配置
    TIME_PATTERNS: Dict[str, List[str]] = {
        "this_semester": ["这学期", "本学期", "当前学期"],
        "next_semester": ["下学期", "下个学期"],
        "last_semester": ["上学期", "上个学期"],
        "this_week": ["本周", "这周", "本周"],
        "next_week": ["下周", "下个星期"],
        "last_week": ["上周", "上星期", "上一周"],
        "specific_week": ["第\d+周", "第\d+星期"],
        "today": ["今天", "今日"],
        "tomorrow": ["明天", "明日"],
        "yesterday": ["昨天", "昨日"]
    }

    # 任务状态定义
    TASK_STATUS = {
        "pending": "pending",
        "processing": "processing",
        "completed": "completed",
        "failed": "failed"
    }

    # 错误消息
    ERROR_MESSAGES = {
        "no_tasks_found": "未识别到任何有效任务",
        "invalid_instruction": "无效的指令格式",
        "module_not_found": "未找到指定的任务模块",
        "execution_failed": "任务执行失败"
    }

    # 性能配置
    PERFORMANCE = {
        "cache_enabled": True,
        "cache_ttl": 3600,  # 缓存时间（秒）
        "max_concurrent_tasks": 5,
        "task_timeout": 300  # 任务超时时间（秒）
    }

    # 日志配置
    LOGGING = {
        "level": logging.INFO,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }

    @classmethod
    def setup_logging(cls):
        """设置日志配置"""
        logging.basicConfig(
            level=cls.LOGGING["level"],
            format=cls.LOGGING["format"]
        )
