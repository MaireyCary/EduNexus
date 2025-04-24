import json
import logging
import os
import re

import pandas as pd
from flask import send_from_directory

logger = logging.getLogger(__name__)


class ExamResultService:
    def __init__(self):
        # 获取模块绝对路径
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # 初始化路径
        self.data_path = os.path.join(module_dir, "exam_data")
        self.report_path = os.path.join(module_dir, "exam_reports")
        self.example_path = os.path.join(module_dir, "example")

        # 确保目录存在
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.report_path, exist_ok=True)
        os.makedirs(self.example_path, exist_ok=True)

        logger.info(f"考试成绩服务初始化完成，工作目录: {module_dir}")

    def read_json_file(self, file_path):
        """读取 JSON 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"文件{file_path}解析失败", exc_info=True)
            raise ValueError("数据文件损坏")
        except FileNotFoundError:
            logger.error(f"文件{file_path}未找到", exc_info=True)
            raise

    def download_template(self):
        """下载考试成绩模板文件"""
        try:
            # 确认样表文件路径
            template_file = '考试成绩模板.xlsx'
            template_path = os.path.join(self.example_path, template_file)

            # 验证文件是否存在
            if not os.path.exists(template_path):
                logger.error(f"考试成绩表样表不存在，路径: {template_path}")
                raise FileNotFoundError("考试成绩模板文件未配置，请联系管理员")

            logger.info(f"准备下载考试成绩模板: {template_path}")

            # 返回文件下载响应
            return send_from_directory(
                directory=self.example_path,
                path=template_file,
                as_attachment=True,
                download_name='考试成绩模板.xlsx',  # 前端显示的下载文件名
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            logger.error(f"考试成绩模板下载失败: {str(e)}", exc_info=True)
            raise Exception(f"模板下载服务暂时不可用: {str(e)}")

    def upload_exam_results(self, file, class_name=None):
        """上传考试成绩 Excel 文件"""
        try:
            # 优先从文件名中提取班级名称
            extracted_class_name = self.extract_class_name(file.filename)
            if extracted_class_name:
                class_name = extracted_class_name
            else:
                if not class_name:
                    raise ValueError("无法从文件名中提取班级名称，请手动提供班级名称")

            # 验证班级名称是否符合命名样式规则
            if not self.validate_class_name(class_name):
                raise ValueError(f"班级名称 {class_name} 不符合命名样式规则")

            # 读取 Excel 文件
            df = pd.read_excel(file)

            # 转换为 JSON 格式
            new_json_data = self.excel_to_json(df)
            logger.info(f"转换后的 JSON 数据: {new_json_data}")

            # 检查路径
            logger.info(f"数据保存路径: {self.data_path}")
            json_file_path = os.path.join(self.data_path, f'{class_name}.json')
            logger.info(f"即将保存的文件路径: {json_file_path}")

            if os.path.exists(json_file_path):
                existing_data = self.read_json_file(json_file_path)
                updated_data = self.merge_exam_data(existing_data, new_json_data)
            else:
                updated_data = new_json_data

            # 保存为 JSON 文件
            try:
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_data, f, ensure_ascii=False, indent=2)
                logger.info(f"文件已成功保存到: {json_file_path}")
            except Exception as e:
                logger.error(f"保存文件时出现错误: {e}", exc_info=True)
                return False

            # 生成成绩分析报告
            self.generate_report(class_name)

            return True
        except Exception as e:
            logger.error(f"上传考试成绩文件失败: {str(e)}", exc_info=True)
            return False

    def extract_class_name(self, filename):
        """从文件名中提取班级名称"""
        # 通用班级命名样式：数字+专业名称+数字+班，增加更灵活的匹配，允许中间有空格等字符
        pattern = r'(\d+\s*[^\d]+\s*\d+\s*班)'
        match = re.search(pattern, filename)
        if match:
            return match.group(1).strip()  # 去除可能存在的多余空格
        return None

    def validate_class_name(self, class_name):
        """验证班级名称是否符合命名样式规则"""
        pattern = r'^\d+[^\d]+?\d+班$'
        return bool(re.match(pattern, class_name))

    def excel_to_json(self, df):
        json_data = {}
        for year in df['学年'].unique():
            year_data = df[df['学年'] == year]
            json_data[year] = {}
            for semester in year_data['学期'].unique():
                semester_data = year_data[year_data['学期'] == semester]
                subjects = {}
                for subject in semester_data['课程'].unique():
                    subject_data = semester_data[semester_data['课程'] == subject]
                    students = []
                    for index, row in subject_data.iterrows():
                        score = row['成绩']
                        if isinstance(score, str) and score.strip().lower() == '缺考':
                            score = None
                        students.append({
                            '姓名': row['姓名'],
                            '学号': row['学号'],
                            '成绩': score
                        })
                    subjects[subject] = students
                json_data[year][semester] = subjects
        return json_data

    def merge_exam_data(self, existing_data, new_data):
        for year, semesters in new_data.items():
            if year not in existing_data:
                existing_data[year] = {}
            for semester, subjects in semesters.items():
                if semester not in existing_data[year]:
                    existing_data[year][semester] = {}
                for subject, students in subjects.items():
                    # 若学科已存在则覆盖，不存在则添加
                    existing_data[year][semester][subject] = students
        return existing_data

    def generate_report(self, class_name):
        try:
            json_file_path = os.path.join(self.data_path, f'{class_name}.json')
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            rows = []
            for year, semesters in data.items():
                for semester, courses in semesters.items():
                    for course, students in courses.items():
                        for student in students:
                            score = student['成绩']
                            if score is None:
                                score = '缺考'
                            rows.append({
                                '学年': year,
                                '学期': semester,
                                '课程': course,
                                '学号': student['学号'],
                                '姓名': student['姓名'],
                                '成绩': score
                            })
            df = pd.DataFrame(rows)
            average_scores = df[df['成绩'] != '缺考'].groupby('课程')['成绩'].mean()
            bins = [0, 60, 70, 80, 90, 100]
            labels = ['不及格', '60 - 69', '70 - 79', '80 - 89', '90 - 100']
            grade_distribution = df[df['成绩'] != '缺考'].groupby('课程')['成绩'].apply(
                lambda x: pd.cut(x, bins=bins, labels=labels).value_counts()
            )
            report_file_path = os.path.join(self.report_path, f'{class_name}.xlsx')
            with pd.ExcelWriter(report_file_path) as writer:
                df.to_excel(writer, sheet_name='整体数据表', index=False)
                average_scores.to_excel(writer, sheet_name='平均分')
                grade_distribution.unstack().to_excel(writer, sheet_name='成绩分布')
            logger.info(f"成绩分析报告已生成: {report_file_path}")
        except Exception as e:
            logger.error(f"生成成绩分析报告时出现错误: {str(e)}", exc_info=True)

    def get_classes(self):
        """获取前端指定格式的班级数据"""
        result = []
        try:
            # 检查数据目录是否存在
            if not os.path.exists(self.data_path):
                logger.error("数据目录不存在")
                return []
            # 遍历数据目录
            for filename in os.listdir(self.data_path):
                # 验证文件名格式
                if not filename.endswith(".json"):
                    continue
                try:
                    # 解析班级
                    class_name = filename.split(".")[0]
                    file_path = os.path.join(self.data_path, filename)
                    # 读取文件内容
                    classes_data = self.read_json_file(file_path)
                    if not classes_data:
                        continue
                    # 存储每个班级各学年各学期的数据
                    class_years_data = {}
                    for year, semesters in classes_data.items():
                        if not isinstance(semesters, dict):
                            logger.warning(f"文件 {filename} 中 {year} 对应的数据不是字典类型")
                            continue
                        for semester, subjects in semesters.items():
                            if not isinstance(subjects, dict):
                                logger.warning(f"文件 {filename} 中 {year}-{semester} 对应的数据不是字典类型")
                                continue
                            subject_list = list(set(subjects.keys()) - {'姓名', '学号'})
                            if subject_list:
                                if year not in class_years_data:
                                    class_years_data[year] = {}
                                class_years_data[year][semester] = {
                                    '学科': subject_list
                                }
                    # 仅当包含有效数据时添加
                    if class_years_data:
                        result.append({
                            "班级名称": class_name,
                            "学年学期数据": class_years_data
                        })
                except KeyError as e:
                    logger.warning(f"文件 {filename} 解析异常: {str(e)}")
                    continue
            return result
        except Exception as e:
            logger.error(f"发生未知错误: {e}", exc_info=True)
            return []

    def get_classes_data(self, classes_str):
        """获取指定考试的完整成绩数据"""
        result = []
        try:
            if isinstance(classes_str, dict):
                className = classes_str.get('className')
                if className:
                    classes_str = f"{className}.json"
                else:
                    raise ValueError("字典中未获取到有效的班级名称")
            # 调整参数格式校验
            if not re.match(r'^.*\.json$', classes_str):
                raise ValueError("考试名称格式应为'班级.json'，如：23软件技术1班.json")
            # 构造文件路径
            file_path = os.path.join(self.data_path, classes_str)
            # 文件存在性校验
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"{classes_str}数据尚未录入")
            # 读取文件内容
            classes_data = self.read_json_file(file_path)
            class_years_data = {}
            for year, semesters in classes_data.items():
                for semester, subjects in semesters.items():
                    # 提取学科名称并去重
                    subject_names = list(set(subjects.keys()) - {'姓名', '学号'})
                    semester_data = {}
                    for subject in subject_names:
                        student_list = subjects[subject]
                        student_scores = []
                        subject_score_list = []
                        for student in student_list:
                            student_score = {
                                '姓名': student.get('姓名'),
                                '学号': student.get('学号'),
                                '成绩': student.get('成绩')
                            }
                            student_scores.append(student_score)
                            score = student.get('成绩')
                            if score is not None:
                                subject_score_list.append(score)
                        # 计算平均分
                        if subject_score_list:
                            subject_average = sum(subject_score_list) / len(subject_score_list)
                        else:
                            subject_average = 0
                        # 计算成绩分布
                        score_distribution = self.calculate_score_distribution(subject_score_list)
                        semester_data[subject] = {
                            '学生成绩': student_scores,
                            '学科平均分': subject_average,
                            '成绩分布': score_distribution
                        }
                    if year not in class_years_data:
                        class_years_data[year] = {}
                    class_years_data[year][semester] = semester_data
            result = {
                "班级名称": classes_str.replace('.json', ''),
                "学年学期数据": class_years_data
            }
            return result
        except Exception as e:
            logger.error(f"获取{classes_str}数据异常: {str(e)}", exc_info=True)
            raise

    def calculate_score_distribution(self, scores):
        """计算成绩分布"""
        distribution = {
            '0-59': 0,
            '60-69': 0,
            '70-79': 0,
            '80-89': 0,
            '90-100': 0
        }
        for score in scores:
            if 0 <= score < 60:
                distribution['0-59'] += 1
            elif 60 <= score < 70:
                distribution['60-69'] += 1
            elif 70 <= score < 80:
                distribution['70-79'] += 1
            elif 80 <= score < 90:
                distribution['80-89'] += 1
            elif 90 <= score <= 100:
                distribution['90-100'] += 1
        return distribution

    def download_report(self, classes):
        """下载考试报告"""
        try:
            # 统一文件类型为
            report_file = os.path.join(self.report_path, f'{classes}.xlsx')
            if not os.path.exists(report_file):
                raise FileNotFoundError("考试报告不存在")

            return send_from_directory(
                directory=self.report_path,
                path=f'{classes}.xlsx',
                as_attachment=True,
                mimetype='application/xlsx'
            )
        except Exception as e:
            logger.error(f"下载考试报告错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")
