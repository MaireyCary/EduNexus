import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from modules.course_scheduling import init_app as init_courses
from modules.attendance_analysis import init_app as init_attendance
from modules.exam_scheduling import init_app as init_exam
from modules.exam_result_analysis import init_app as init_exam_result_analysis
from core import init_app as init_dispatch
from modules.leave_approval_system import init_app as init_leave

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)

    # 基础配置
    app.config.update({
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        'UPLOAD_FOLDER': os.path.join(os.path.dirname(__file__), 'uploads')
    })

    # 配置CORS（允许所有跨域）
    CORS(app, resources={
        r"/dispatch_center/*": {"origins": "*"},
        r"/course-scheduling/*": {"origins": "*"},
        r"/attendance_analysis/*": {"origins": "*"},
        r"/exam_scheduling/*": {"origins": "*"},
        r"/api/*": {"origins": "*"},
        r"/leave_approval_system/*": {"origins": "*"},
        r"/exam_result_analysis/*": {"origins": "*"},

    })

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 初始化各模块
    try:
        init_courses(app)
        logger.info("排课模块初始化成功")
        init_attendance(app)
        logger.info("考勤模块初始化成功")
        init_exam(app)
        logger.info("考试模块初始化成功")
        init_dispatch(app)
        logger.info("调度中心模块初始化成功")
        init_leave(app)
        logger.info("请假模块初始化成功")
        init_exam_result_analysis(app)
        logger.info("成绩考试初始化成功")

    except Exception as e:
        logger.error(f"模块初始化失败: {str(e)}", exc_info=True)
        raise

    # 健康检查端点
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": {
                "Course Scheduling": {
                    "endpoints": {
                        "upload_teacher": "POST /course-scheduling/upload/teacher",
                        "upload_courses": "POST /course-scheduling/upload/courses",
                        "arrange": "POST /course-scheduling/arrange",
                        "download_result": "GET /course-scheduling/download/excel",
                        "download_template": "GET /course-scheduling/download/teacher-template"
                    }
                },
                "Attendance Analysis": {
                    "endpoints": {
                        "get_week": "GET /attendance_analysis/get/week",
                        "get_data": "GET /attendance_analysis/get/data",
                        "download_result": "GET /attendance_analysis/download/excel"
                    }
                },
                "Exam Scheduling": {
                    "endpoints": {
                        "get_week": "GET /exam_scheduling/get/exam",
                        "download_result": "GET /exam_scheduling/download/excel"
                    }
                },
                "Dispatch Center": {
                    "endpoints": {
                        "execute": "POST /dispatch_center/execute",
                        "download": "POST /dispatch_center/download"
                    }
                },
                "Leave Approval": {
                    "endpoints": {
                        "get_leave_records": "GET /leave/get_leave_records",
                        "change_leave_status": "POST /leave/change_leave_status"
                    }
                }
            }
        })
    return app