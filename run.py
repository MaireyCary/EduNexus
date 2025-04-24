from app import create_app
import argparse

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='EduNexus 教务平台后端服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='监听端口 (默认: 5000)')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    app = create_app()

    print(f"""
        =============================================
          EduNexus 后端服务启动
          访问地址: http://{args.host}:{args.port}
          健康检查: http://{args.host}:{args.port}/api/health

          排课API文档:
            - 教师表上传: POST /course-scheduling/upload/teacher
            - 课表上传: POST /course-scheduling/upload/courses
            - 执行排课: POST /course-scheduling/arrange
            - 下载排课结果: GET /course-scheduling/download/result
            - 下载教师表模板: GET /course-scheduling/download/teacher-template

          考勤API文档:
            - 获取考勤周数: GET /attendance_analysis/get/week
            - 获取考勤数据: GET /attendance_analysis/get/data
            - 下载考勤文档: GET /attendance_analysis/download/result
            
          请假模块API文档:
            - 获取所有请假记录: GET /leave/get_leave_records
            - 更改请假记录状态: POST /leave/change_leave_status
            - 退回请假状态: POST /leave/reset_leave_status

          考试API文档:
            - 获取考试信息: GET /exam_scheduling/get/exam
            - 考试安排上传: GET /exam_scheduling/upload/courses
            
          成绩分析API文档:
            - 获取班级成绩: GET /exam_result_analysis/download/report
            - 考试成绩上传: GET /exam_result_analysis/upload/exam_results
            - 下载成绩表模板: GET /course-scheduling/download/teacher-template

          调度中心API文档:
            - 任务调度中心: POST /dispatch_center/execute
            - 调度中心下载: POST /dispatch_center/download

          文件存储路径:
            排课模块
            - 教师表模板: modules/course_scheduling/example/教师表样表.xlsx
            - 上传文件: modules/course_scheduling/tmp/
            - 结果文件: modules/course_scheduling/result/

            考勤模块
            - 考勤数据: modules/attendance_analysis/example_data
            - 考勤文档: modules/attendance_analysis/results
            
            考试成绩模块
            - 成绩表模板: modules/exam_result_analysis/example
            - 成绩数据: modules/exam_result_analysis/exam_data
            - 成绩表: modules/exam_result_analysis/exam_reports
            
            考试信息模块
            - 考试信息数据: modules/exam_scheduling/example_data
            - 考试安排表模板: modules/exam_scheduling/excel
            - 考试安排表: modules/exam_scheduling/excel_data

            调度中心
            - 多语言嵌入模型: core/model/multilingual-e5-large
        =============================================
        """)

    app.run(
        host=args.host,
        port=args.port,
        threaded=True
    )