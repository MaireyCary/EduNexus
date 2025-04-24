import json
import logging

# 配置日志
logger = logging.getLogger(__name__)
# 定义合并后的 JSON 文件路径
LEAVE_RECORDS_FILE = "modules/leave_approval_system/parameter/leave_records.json"
# 定义有效的状态列表
VALID_STATUSES = ["approved", "rejected", "pending"]


class LeaveService:
    def load_leave_records(self):
        """从 JSON 文件中加载所有请假记录"""
        try:
            with open(LEAVE_RECORDS_FILE, 'r', encoding='utf-8') as file:
                records = json.load(file)
                logger.info(f"成功从 {LEAVE_RECORDS_FILE} 加载 {len(records)} 条请假记录。")
                return records
        except FileNotFoundError:
            logger.warning(f"未找到 {LEAVE_RECORDS_FILE} 文件，返回空记录列表。")
            return []
        except json.JSONDecodeError:
            logger.warning(f"解析 {LEAVE_RECORDS_FILE} 文件时出错，文件可能不是有效的 JSON 格式。")
            return []

    def save_leave_records(self, records):
        """将所有请假记录保存到 JSON 文件中"""
        try:
            with open(LEAVE_RECORDS_FILE, 'w', encoding='utf-8') as file:
                json.dump(records, file, ensure_ascii=False, indent=2)
            logger.info(f"请假记录已成功保存到 {LEAVE_RECORDS_FILE} 文件。")
        except PermissionError:
            logger.warning(f"保存请假记录到 {LEAVE_RECORDS_FILE} 文件时出错: 没有文件写入权限。")
        except Exception as e:
            logger.warning(f"保存请假记录到 {LEAVE_RECORDS_FILE} 文件时出错: {e}")

    def change_status_to_approved(self, record_id):
        """批量将指定请假记录的状态改为 approved"""
        new_status = "approved"

        # 检查 record_id 是否为列表
        if not isinstance(record_id, list):
            logger.warning(f"传入的 record_id 不是列表类型: {type(record_id)}")
            return False

        # 处理空列表
        if not record_id:
            logger.debug("传入的 ID 列表为空，无操作")
            return False

        records = self.load_leave_records()
        success_ids = []
        failed_ids = []
        # 1. 内存中预检查并标记修改（不直接操作原数据）
        for r_id in record_id:
            found = False
            for record in records:
                if record["id"] == r_id:
                    record["status"] = new_status  # 标记修改
                    success_ids.append(r_id)
                    found = True
                    break  # 找到即停止内层循环
            if not found:
                failed_ids.append(r_id)

        # 2. 结果判定与日志
        if len(failed_ids) == len(record_id):
            logger.warning(
                f"批量修改状态为 {new_status} 失败："
                f"失败 {len(failed_ids)} 条（未找到 ID: {failed_ids}）"
            )
            # 回滚内存中的修改（可选，保持原数据一致性）
            # 若不需要回滚，可省略此步骤（因未调用 save_leave_records）
            return False
        elif len(failed_ids) >= 0:
            self.save_leave_records(records)
            logger.info(
                f"批量修改状态为 {new_status} 成功："
                f"成功 {len(success_ids)} 条（ID: {success_ids}），"
                f"失败 {len(failed_ids)} 条（未找到 ID: {failed_ids}）"
            )
            return True

    def change_status_to_rejected(self, record_id):
        """批量将指定请假记录的状态改为 rejected"""
        new_status = "rejected"

        # 检查 record_id 是否为列表
        if not isinstance(record_id, list):
            logger.warning(f"传入的 record_id 不是列表类型: {type(record_id)}")
            return False

        # 处理空列表
        if not record_id:
            logger.debug("传入的 ID 列表为空，无操作")
            return False

        records = self.load_leave_records()
        success_ids = []
        failed_ids = []
        # 1. 内存中预检查并标记修改（不直接操作原数据）
        for r_id in record_id:
            found = False
            for record in records:
                if record["id"] == r_id:
                    record["status"] = new_status  # 标记修改
                    success_ids.append(r_id)
                    found = True
                    break  # 找到即停止内层循环
            if not found:
                failed_ids.append(r_id)

        # 2. 结果判定与日志
        if len(failed_ids) == len(record_id):
            logger.warning(
                f"批量修改状态为 {new_status} 失败："
                f"失败 {len(failed_ids)} 条（未找到 ID: {failed_ids}）"
            )
            # 回滚内存中的修改（可选，保持原数据一致性）
            # 若不需要回滚，可省略此步骤（因未调用 save_leave_records）
            return False
        elif len(failed_ids) >= 0:
            self.save_leave_records(records)
            logger.info(
                f"批量修改状态为 {new_status} 成功："
                f"成功 {len(success_ids)} 条（ID: {success_ids}），"
                f"失败 {len(failed_ids)} 条（未找到 ID: {failed_ids}）"
            )
            return True

    def get_all_leave_records(self):
        """获取所有请假记录"""
        return self.load_leave_records()