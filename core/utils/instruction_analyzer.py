import logging
import re

from typing import Dict, Any, List, Optional
from ..config import Config


class InstructionAnalyzer:
    def __init__(self, task_modules: Dict[str, Any], time_patterns: Dict[str, Any]):
        """指令分析器初始化"""
        self.logger = logging.getLogger(__name__)
        self.task_modules = task_modules
        self.time_patterns = time_patterns

    def analyze(self, instruction: str) -> List[Dict[str, Any]]:
        """完整分析指令并返回任务列表"""
        instruction = instruction.lower().strip()
        sub_instructions = self._split_instructions(instruction)
        self.logger.info(f"分割后的指令: {sub_instructions}")
        tasks = []

        for sub_instr in sub_instructions:
            matched_keywords = self._match_keywords(sub_instr)
            for task_id, keywords in matched_keywords.items():
                params = self._extract_parameters(sub_instr, self.task_modules[task_id])
                if params:
                    tasks.append(self._build_task(task_id, keywords, params))

        return self._sort_tasks(tasks, instruction)

    def _split_instructions(self, instruction: str) -> List[str]:
        """分割复合指令"""
        split_pattern = "|".join([re.escape(s) for s in Config.INSTRUCTION_SPLITTERS])
        return [s.strip() for s in re.split(split_pattern, instruction) if s.strip()]

    def _match_keywords(self, sub_instruction: str) -> Dict[str, List[str]]:
        """匹配关键词"""
        matched = {}
        for task_id, module_config in self.task_modules.items():
            for kw in module_config["keywords"]:
                if kw.lower() in sub_instruction:
                    if task_id not in matched:
                        matched[task_id] = []
                    matched[task_id].append(kw)
        return matched

    def _extract_parameters(self, instruction: str, module_config: Dict[str, Any]) -> Dict[str, str]:
        """提取参数"""
        params = {}
        for param in module_config.get("required_params", []):
            if param == "week_number":
                params[param] = self._extract_week_number(instruction)
            elif param == "semester":
                params[param] = self._extract_semester(instruction)
            elif param == "exam_type":
                # params[param] = self._extract_exam_type(instruction)
                params[param] = self._extract_course_name(instruction)
            elif param == "student_ids" or param == "student_name":
                params["student_ids"] = self._extract_student_id(instruction)
                params["student_names"] = self._extract_student_name(instruction)
            elif param == "operation_type":
                params[param], params["class_name"] = self._extract_operation_type(instruction)
        return params

    def _extract_exam_type(self, text: str) -> Optional[str]:
        """提取考试类型"""
        if "期中" in text:
            return "midterm"
        elif "期末" in text:
            return "final"
        elif "补考" in text:
            return "makeup"
        return None

    def _extract_week_number(self, text: str) -> Optional[str]:
        """提取周数"""
        if match := re.search(r"第(\d+)周", text):
            return match.group(1)
        for key, patterns in self.time_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                if key in ["this_week", "next_week", "last_week"]:
                    return key
        return None

    def _extract_student_id(self, text: str) -> Optional[str]:
        """提取学生学号"""
        # 初始化候选列表
        student_ids = []
        # 精确匹配模式（带关键词）
        id_matches = re.search(
            r'学号[为是]?[:：]?(\d+(?:[ 和、与及，,]\d+)*)',
            text.replace(" ", "")
        )
        if id_matches:
            student_ids.extend(re.split(r'[和、与及，,\s]+', id_matches.group(1)))
            return student_ids
        return []

    def _extract_student_name(self, text: str) -> Optional[str]:
        """提取学生姓名"""
        student_names = []
        # 姓名精确匹配
        name_matches = re.search(
            r'(?:姓名|学生)[为是]?[:：]?([\u4e00-\u9fa5]+(?:[ 和、与及，,][\u4e00-\u9fa5]+)*)',
            text
        )
        if name_matches:
            student_names.extend(re.split(r'[和、与及，,\s]+', name_matches.group(1)))
            return student_names
        return []

    def _extract_semester(self, text: str) -> Optional[str]:
        """提取学期"""
        for key, patterns in self.time_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                if key in ["this_semester", "next_semester", "last_semester"]:
                    return key
        return None

    def _extract_operation_type(self, text: str) -> Optional[str]:
        """使用正则判断上传/导出动作"""
        # 独立动作判断（当组合匹配失败时使用）
        if re.search(r'上传|提交|添加', text):
            return 'upload', None
        elif re.search(r'导出|下载|获取', text):
            return 'download', self._extract_class_name(text)
        return None, None

    def _extract_course_name(self, text: str) -> Optional[str]:
        """提取班级名称"""
        if match := re.search(r"(\d{2,4}[级届]?)\s*([\u4e00-\u9fa5]+)\s*(\d+)班", text):
            return f"{match.group(1)}{match.group(2)}{match.group(3)}班"
        return None

    def _extract_class_name(self, text: str) -> Optional[str]:
        """提取班级名称"""
        if match := re.search(r"(\d{2,4}[级届]?)\s*([\u4e00-\u9fa5]+)\s*(\d+)班", text):
            return f"{match.group(1)}{match.group(2)}{match.group(3)}班"
        return None

    def _build_task(self, task_id: str, keywords: List[str], params: Dict[str, str]) -> Dict[str, Any]:
        """构建任务字典"""
        return {
            "task_id": task_id,
            "module_path": self.task_modules[task_id]["module_path"],
            "parameters": params,
            "matched_keywords": keywords
        }

    def _sort_tasks(self, tasks: List[Dict[str, Any]], instruction: str) -> List[Dict[str, Any]]:
        """排序任务"""
        if len(tasks) > 1:
            tasks.sort(key=lambda t: min(
                instruction.find(kw.lower()) for kw in t["matched_keywords"]
            ))
        return tasks
