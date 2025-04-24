from flask import Blueprint, request, jsonify
from .services import LeaveService

# 创建蓝图
bp = Blueprint('leave_approval', __name__)
# 初始化服务
service = LeaveService()

@bp.route('/get_leave_records', methods=['GET'])
def get_leave_records():
    """获取所有请假记录"""
    records = service.get_all_leave_records()
    return jsonify(records)

@bp.route('/change_leave_status_to_approved', methods=['POST'])
def change_leave_status_to_approved():
    """批量将指定请假记录的状态改为 approved"""
    data = request.get_json()
    record_id = data.get('record_id')

    if not record_id:
        return jsonify({"error": "缺少必要的参数（record_id）"}), 400

    if service.change_status_to_approved(record_id):
        return jsonify({"message": f"请假记录 {record_id} 的状态已更新为 approved。"})
    else:
        return jsonify({"error": f"未找到 ID 为 {record_id} 的请假记录。"}), 404

@bp.route('/change_leave_status_to_rejected', methods=['POST'])
def change_leave_status_to_rejected():
    """批量将指定请假记录的状态改为 rejected"""
    data = request.get_json()
    record_id = data.get('record_id')

    if not record_id:
        return jsonify({"error": "缺少必要的参数（record_id）"}), 400

    if service.change_status_to_rejected(record_id):
        return jsonify({"message": f"请假记录 {record_id} 的状态已更新为 rejected。"})
    else:
        return jsonify({"error": f"未找到 ID 为 {record_id} 的请假记录。"}), 404