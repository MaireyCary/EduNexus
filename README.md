# EduNexus 教务智能调度系统

![Python](https://img.shields.io/badge/Python-3.11.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.2-green)

## 项目概述

EduNexus（学务云枢）是一个基于文本嵌入模型的教务集成系统，旨在为高校提供智能化的业务处理平台。
系统利用先进的多语言文本嵌入技术，实现智能分析用户指令，智能辅助用户批量完成任务，降低业务压力，提升高校运作效率。

## 环境参考

- Python>=3.11.11
- Flask>=2.3.2
- 核心依赖库：

  ```text
  flask>=2.3.2
  pandas>=2.1.4
  openpyxl>=3.1.2
  python-docx>=0.8.11
  python-dateutil>=2.8.2
  ```

## 使用说明

- app.py —— 系统路由工厂
- run.py —— 系统启动脚本
- serve.py —— 前端界面启动脚本

## API文档集合

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

考试API文档:

- 获取考试信息: GET /exam_scheduling/get/exam
- 下载考试文档: GET /exam_scheduling/download/result

调度中心API文档:

- 任务调度中心: POST /dispatch_center/execute

## 项目结构

```plaintext
EduNexus/
├── core/                     # 调度中心模块
│   ├── __init__.py           # 模块初始化
│   ├── config.py             # 全局配置
│   ├── routes.py             # API路由定义
│   ├── services.py           # 业务服务
│   ├── utils/                # 工具类
│   └── ……
├── dist/                     # 前端文件
├── modules/                  # 功能模块
│   ├── attendance_analysis/  # 考勤分析
│   ├── course_scheduling/    # 课程安排
│   └── exam_scheduling       # 考试安排
├── app.py                    # 系统路由工厂
├── README.md                 # 说明文档
├── requirements.txt          # 依赖清单
├── run.py                    # 系统启动脚本
└── serve.py                  # 前端界面启动脚本
```
