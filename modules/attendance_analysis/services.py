import json
import logging
import os
import re

from flask import send_from_directory

logger = logging.getLogger(__name__)


class AttendanceService:
    def __init__(self):
        # 获取模块绝对路径
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # 初始化路径
        self.data_path = os.path.join(module_dir, "example_data")
        self.excel_path = os.path.join(module_dir, "results")

        # 确保目录存在
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.excel_path, exist_ok=True)

        logger.info(f"考勤服务初始化完成，工作目录: {module_dir}")

    def get_available_weeks(self):
        """获取前端指定格式的周数据"""
        result = []

        try:
            # 遍历数据目录
            for filename in os.listdir(self.data_path):
                # 验证文件名格式
                if not (filename.startswith("第") and filename.endswith("周.json")):
                    continue

                try:
                    # 解析周数
                    week_num = int(filename[1:-6])
                    file_path = os.path.join(self.data_path, filename)

                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        week_data = json.load(f)

                    # 构建每日班级数据
                    days_classes = {}
                    for day in ["星期一", "星期二", "星期三", "星期四", "星期五"]:
                        if day in week_data:
                            # 提取班级名称并去重
                            classes = list({c["班级"] for c in week_data[day] if c.get("班级")})
                            days_classes[day] = sorted(classes)

                    # 过滤空日期数据
                    days_classes = {k: v for k, v in days_classes.items() if v}

                    # 仅当包含有效数据时添加
                    if days_classes:
                        result.append({
                            "week_name": f"第{week_num}周",
                            "days": days_classes
                        })

                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"文件{filename}解析异常: {str(e)}")
                    continue

            # 按周数降序排序
            return sorted(result, key=lambda x: int(x["week_name"][1:-1]), reverse=True)

        except FileNotFoundError:
            logger.error("数据目录不存在", exc_info=True)
            return []

    def get_data(self, week_str):
        """获取指定周的完整考勤数据"""
        filename = ""
        try:
            # 参数格式校验
            if not re.match(r'^第\d+周$', week_str):
                raise ValueError("周数格式应为'第X周'，如：第5周")

            # 构造文件路径
            filename = f"{week_str}.json"
            file_path = os.path.join(self.data_path, filename)

            # 文件存在性校验
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{week_str}数据尚未录入")

            # 读取并返回数据
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except json.JSONDecodeError:
            logger.error(f"文件{filename}解析失败", exc_info=True)
            raise ValueError("数据文件损坏")
        except Exception as e:
            logger.error(f"获取{week_str}数据异常: {str(e)}", exc_info=True)
            raise

    def download_result(self, week):
        """下载考勤文档"""
        try:
            result_file = os.path.join(self.excel_path, f'{week}.xlsx')
            if not os.path.exists(result_file):
                raise FileNotFoundError("考勤文档不存在")

            return send_from_directory(
                directory=self.excel_path,
                path=f'{week}.xlsx',
                as_attachment=True,
                mimetype='application/zip'
            )
        except Exception as e:
            logger.error(f"下载考勤文档错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")
