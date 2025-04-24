import os
import shutil
import logging

from flask import send_from_directory
from .utils import excel, arrangeCourses

logger = logging.getLogger(__name__)


class SchedulingService:
    def __init__(self):
        # 获取模块绝对路径
        module_dir = os.path.dirname(os.path.abspath(__file__))

        # 初始化路径（使用绝对路径）
        self.tmp_teacher_path = os.path.join(module_dir, "tmp/teacher")
        self.tmp_courses_path = os.path.join(module_dir, "tmp/courses")
        self.example_path = os.path.join(module_dir, "example")
        self.result_path = os.path.join(module_dir, "result")

        # 确保目录存在
        os.makedirs(self.tmp_teacher_path, exist_ok=True)
        os.makedirs(self.tmp_courses_path, exist_ok=True)
        os.makedirs(self.example_path, exist_ok=True)
        os.makedirs(self.result_path, exist_ok=True)

        logger.info(f"排课服务初始化完成，工作目录: {module_dir}")

    def download_example_template(self):
        """下载教师表样表（最终版）"""
        try:
            # 确认样表文件路径
            template_file = '教师表样表.xlsx'
            template_path = os.path.join(self.example_path, template_file)

            # 验证文件是否存在
            if not os.path.exists(template_path):
                logger.error(f"教师表样表不存在，路径: {template_path}")
                raise FileNotFoundError("教师表模板文件未配置，请联系管理员")

            logger.info(f"准备下载教师表模板: {template_path}")

            # 返回文件下载响应
            return send_from_directory(
                directory=self.example_path,
                path=template_file,
                as_attachment=True,
                download_name='教师表模板.xlsx',  # 前端显示的下载文件名
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            logger.error(f"教师表模板下载失败: {str(e)}", exc_info=True)
            raise Exception(f"模板下载服务暂时不可用: {str(e)}")

    def upload_teacher(self, file):
        """处理教师表上传"""
        try:
            # 清空目录
            if os.path.exists(self.tmp_teacher_path):
                shutil.rmtree(self.tmp_teacher_path)
            os.makedirs(self.tmp_teacher_path)

            # 保存文件
            save_path = os.path.join(self.tmp_teacher_path, file.filename)
            file.save(save_path)

            # 验证文件有效性
            if not os.path.exists(save_path):
                raise IOError("文件保存失败")
            return True
        except Exception as e:
            logger.error(f"教师表上传错误: {str(e)}", exc_info=True)
            raise Exception(f"教师表处理失败: {str(e)}")

    def upload_courses(self, file):
        """处理课表上传"""
        try:
            # 清空目录
            if os.path.exists(self.tmp_courses_path):
                shutil.rmtree(self.tmp_courses_path)
            os.makedirs(self.tmp_courses_path)

            # 保存文件
            save_path = os.path.join(self.tmp_courses_path, file.filename)
            file.save(save_path)

            # 解压处理
            if file.filename.lower().endswith('.zip'):
                excel.get_zip(self.tmp_courses_path)
            return True
        except Exception as e:
            logger.error(f"课表上传错误: {str(e)}", exc_info=True)
            raise Exception(f"课表处理失败: {str(e)}")

    def arrange_courses(self):
        """执行排课"""
        try:
            # 检查教师文件
            if not os.listdir(self.tmp_teacher_path):
                raise FileNotFoundError("教师表目录为空")

            teacher_file = os.path.join(self.tmp_teacher_path, os.listdir(self.tmp_teacher_path)[0])

            # 读取教师数据
            teacher_data = excel.get_teacher_data(teacher_file)
            if not teacher_data:
                raise ValueError("教师表数据解析失败")

            global_used_slots = {}
            arrangement_results = {}

            # 处理每个班级
            for class_name, classes in teacher_data.items():
                class_file = os.path.join(self.tmp_courses_path, f"{class_name}课表.xlsx")
                if not os.path.exists(class_file):
                    logger.warning(f"未找到班级课表: {class_name}")
                    continue

                # 获取占用信息
                public_positions = excel.class_get(class_file)

                # 执行排课算法
                best_schedule = arrangeCourses.genetic_algorithm(classes, public_positions)

                # 更新全局占用记录
                for (teacher, course), info in best_schedule.items():
                    place = info["教室"]
                    day = info["星期"]
                    period = info["时间段"]

                    global_used_slots.setdefault(place, {}).setdefault(day, {})[period] = True

                # 写入结果
                excel.write_excel(class_file, best_schedule)
                arrangement_results[class_name] = {
                    'courses': len(best_schedule),
                    'teachers': len({k[0] for k in best_schedule.keys()})
                }

            # 打包结果
            excel.set_zip(self.tmp_courses_path, self.result_path)

            logger.info(f"排课完成，处理班级数: {len(arrangement_results)}")
            return arrangement_results

        except Exception as e:
            logger.error(f"排课过程错误: {str(e)}", exc_info=True)
            raise Exception(f"排课失败: {str(e)}")

    def download_result(self):
        """下载排课结果"""
        try:
            result_file = os.path.join(self.result_path, '排课结果.zip')
            if not os.path.exists(result_file):
                raise FileNotFoundError("排课结果文件不存在")

            logger.debug(f"准备下载排课结果: {result_file}")
            return send_from_directory(
                directory=self.result_path,
                path='排课结果.zip',
                as_attachment=True,
                mimetype='application/zip'
            )
        except Exception as e:
            logger.error(f"下载排课结果错误: {str(e)}", exc_info=True)
            raise Exception(f"下载失败: {str(e)}")
