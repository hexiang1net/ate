"""POST 接口: Excel → TestStand seq 文件转换。

启动:  pip install flask pymysql openpyxl && python api_server.py
调用:  curl -X POST http://localhost:5050/api/run
      curl -X POST http://localhost:5050/api/addLog -H "Content-Type: application/json" -d "{\"plan_id\":\"xxx\",\"create_by\":\"admin\"}"
查询:  curl http://localhost:5050/api/status/<task_id>
"""

import logging
import os
import re
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from typing import Any

import pymysql
import requests
from flask import Flask, request, jsonify, send_file

# 添加 excel_to_seq 所在目录到 sys.path
_EXCEL_TO_SEQ_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teststand-2012-mcp")
if _EXCEL_TO_SEQ_DIR not in sys.path:
    sys.path.insert(0, _EXCEL_TO_SEQ_DIR)

from excel_to_seq import ExcelParser, SeqGenerator

app = Flask(__name__)

BASE_DIR = r"D:\agent\ate"
LOG_FILE = os.path.join(BASE_DIR, "api_server.log")

# ---- 日志配置 ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(threadName)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---- MySQL 连接配置 ----
DB_CONFIG = {
    "host": "10.16.9.91",
    "port": 3306,
    "user": "jeecgboottest",
    "password": "Test@123",
    "database": "jeecg-boot",
    "charset": "utf8mb4",
}


def get_db() -> pymysql.Connection:
    return pymysql.connect(**DB_CONFIG)


# ---- 任务状态存储 ----
tasks: dict[str, dict[str, Any]] = {}
lock = threading.Lock()


def _update_log_end(log_id: str) -> None:
    """更新 ate_exe_log 的 end_time 和 status。"""
    logger.info("_update_log_end 入参: log_id=%s", log_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE ate_exe_log SET end_time=%s, status=%s WHERE id=%s",
                (now, "10", log_id),
            )
        conn.commit()
        logger.info("_update_log_end 成功: log_id=%s, end_time=%s, status=10", log_id, now)
    except Exception:
        conn.rollback()
        logger.exception("_update_log_end 异常: log_id=%s", log_id)
    finally:
        conn.close()


def _git_commit_files(seq_name: str, log_id: str) -> None:
    """提交 seq 文件到 GitHub (直接使用 git 命令)."""
    logger.info("_git_commit_files 开始: seq_name=%s, log_id=%s", seq_name, log_id)
    try:
        subprocess.run(["git", "add", seq_name], cwd=BASE_DIR, capture_output=True, timeout=30)
        result = subprocess.run(
            ["git", "commit", "-m", f"feat: 生成测试序列 {seq_name}"],
            cwd=BASE_DIR, capture_output=True, timeout=30,
        )
        if result.returncode != 0:
            stderr_msg = result.stderr.decode("utf-8", errors="replace")
            if "nothing to commit" in stderr_msg:
                logger.info("_git_commit_files: 无变更需要提交")
                return
            logger.error("_git_commit_files 提交失败: %s", stderr_msg[-500:])
            return
        subprocess.run(["git", "push"], cwd=BASE_DIR, capture_output=True, timeout=60)
        logger.info("_git_commit_files 成功: log_id=%s", log_id)
    except Exception:
        logger.exception("_git_commit_files 异常: log_id=%s", log_id)


def run_excel_to_seq(
    task_id: str,
    excel_path: str,
    seq_name: str,
    log_id: str | None = None,
) -> None:
    """在后台线程中执行 Excel → seq 转换。"""
    logger.info(
        "run_excel_to_seq 入参: task_id=%s, excel_path=%s, seq_name=%s, log_id=%s",
        task_id, excel_path, seq_name, log_id,
    )
    with lock:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["started_at"] = datetime.now().isoformat()

    try:
        seq_path = os.path.join(BASE_DIR, seq_name)

        # 解析 Excel
        parser = ExcelParser()
        test_cases, vi_params, variables = parser.parse(excel_path)
        tasks[task_id]["test_case_count"] = len(test_cases)
        logger.info("Excel 解析完成: task_id=%s, test_cases=%d, vi_params=%d, variables=%d",
                     task_id, len(test_cases), len(vi_params), len(variables))

        # 生成 seq 文件
        generator = SeqGenerator()
        generator.generate(test_cases, vi_params, seq_path, variables=variables)
        logger.info("seq 文件已生成: task_id=%s, path=%s", task_id, seq_path)

        with lock:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["seq_path"] = seq_path
            tasks[task_id]["finished_at"] = datetime.now().isoformat()

    except Exception as exc:
        logger.exception("run_excel_to_seq 异常: task_id=%s, error=%s", task_id, exc)
        with lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = str(exc)
            tasks[task_id]["finished_at"] = datetime.now().isoformat()

    if log_id:
        _update_log_end(log_id)


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------

def _start_excel_to_seq_task(excel_path: str, seq_name: str, log_id: str = "") -> str:
    """启动 Excel→seq 转换任务, 返回 task_id。"""
    logger.info(
        "_start_excel_to_seq_task 入参: excel_path=%s, seq_name=%s, log_id=%s",
        excel_path, seq_name, log_id,
    )
    if not os.path.isabs(excel_path):
        excel_path = os.path.join(BASE_DIR, excel_path)

    task_id = str(uuid.uuid4())[:8]

    with lock:
        tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "excel_path": excel_path,
            "seq_name": seq_name,
            "log_id": log_id,
            "created_at": datetime.now().isoformat(),
        }

    thread = threading.Thread(
        target=run_excel_to_seq,
        args=(task_id, excel_path, seq_name, log_id),
        daemon=True,
    )
    thread.start()
    logger.info("_start_excel_to_seq_task 出参: task_id=%s", task_id)
    return task_id


@app.route("/api/run", methods=["POST"])
def run() -> tuple[Any, int]:
    """POST /api/run — 接收 plan_id，下载 Excel 并启动转换任务。

    JSON body: {"plan_id": "xxx"}
    Response:  {"task_id": "xxx"}
    """
    data: dict[str, str] = request.get_json(silent=True) or {}
    plan_id = data.get("plan_id", "")

    if not plan_id:
        return jsonify({"error": "plan_id 不能为空"}), 400

    # 下载 exportXls 文件
    export_url = f"http://10.12.93.201:16060/jeecg-boot/ate/ateTestPlan/exportXls?id={plan_id}"
    try:
        resp = requests.get(export_url, timeout=30)
        resp.raise_for_status()
        cd = resp.headers.get("Content-Disposition", "")
        match = re.search(r'filename[^;=\n]*=((["\']).*?\2|[^;\n]*)', cd)
        original_name = match.group(1).strip(" \"'") if match else "export.xlsx"
        base, ext = os.path.splitext(original_name)
        file_name = f"{base}_{plan_id}{ext}"
        file_path = os.path.join(BASE_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(resp.content)
    except Exception as exc:
        return jsonify({"error": f"下载 Excel 失败: {exc}"}), 500

    seq_name = f"{base}_{plan_id}.seq"
    task_id = _start_excel_to_seq_task(file_name, seq_name)

    return jsonify({"task_id": task_id}), 202


@app.route("/api/addLog", methods=["POST"])
def add_log() -> tuple[Any, int]:
    """POST /api/addLog — 插入一条执行日志到 ate_exe_log 表。

    必填 JSON body:
      {
        "plan_id":   "xxx",
        "create_by": "admin"
      }
    """
    data: dict[str, str] = request.get_json(silent=True) or {}
    plan_id = data.get("plan_id", "")
    create_by = data.get("create_by", "")

    if not plan_id:
        return jsonify({"error": "plan_id 不能为空"}), 400
    if not create_by:
        return jsonify({"error": "create_by 不能为空"}), 400

    log_id = str(uuid.uuid4()).replace("-", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            sql = (
                "INSERT INTO ate_exe_log (id, plan_id, status, start_time, create_by, create_time, update_by, update_time) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(sql, (log_id, plan_id, "00", now, create_by, now, create_by, now))
        conn.commit()
    except Exception as exc:
        conn.rollback()
        return jsonify({"error": str(exc)}), 500
    finally:
        conn.close()

    # 下载 exportXls 文件到当前目录
    export_url = f"http://10.12.93.201:16060/jeecg-boot/ate/ateTestPlan/exportXls?id={plan_id}"
    file_name = None
    try:
        resp = requests.get(export_url, timeout=30)
        resp.raise_for_status()

        # 从 Content-Disposition 解析原始文件名
        cd = resp.headers.get("Content-Disposition", "")
        match = re.search(r'filename[^;=\n]*=((["\']).*?\2|[^;\n]*)', cd)
        original_name = match.group(1).strip(" \"'") if match else "export.xlsx"

        # 拆分为 基础名 + 扩展名
        base, ext = os.path.splitext(original_name)
        file_name = f"{base}_{log_id}{ext}"
        file_path = os.path.join(BASE_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(resp.content)
    except Exception as exc:
        # 下载失败不影响日志创建结果
        return jsonify({
            "id": log_id,
            "status": "00",
            "message": "日志记录已创建，文件下载失败",
            "download_error": str(exc),
        }), 201

    # 下载成功后自动提交 Excel→seq 转换任务
    seq_name = f"{base}_{log_id}.seq"
    task_id = _start_excel_to_seq_task(file_name, seq_name, log_id)

    return jsonify({
        "id": log_id,
        "status": "00",
        "message": "日志记录已创建",
        "file": file_name,
        "task_id": task_id,
    }), 201


def _build_status_response(task: dict) -> dict:
    """构建带文件信息的任务状态响应。"""
    resp = dict(task)
    if task.get("status") == "completed" and task.get("seq_path"):
        seq_path = task["seq_path"]
        if os.path.isfile(seq_path):
            stat = os.stat(seq_path)
            resp["fileName"] = os.path.basename(seq_path)
            resp["fileSize"] = stat.st_size
    return resp


@app.route("/api/status/<task_id>", methods=["GET"])
def status(task_id: str) -> tuple[Any, int]:
    """GET /api/status/<task_id> — 查询任务进度与结果。"""
    with lock:
        task = tasks.get(task_id)

    if task is None:
        return jsonify({"error": "任务不存在"}), 404

    return jsonify(_build_status_response(task)), 200


@app.route("/api/tasks", methods=["GET"])
def list_tasks() -> tuple[Any, int]:
    """GET /api/tasks — 列出所有任务记录。"""
    with lock:
        return jsonify([_build_status_response(t) for t in tasks.values()]), 200


@app.route("/api/files", methods=["GET"])
def list_files():
    """GET /api/files — 列出所有任务记录（内存 + 磁盘）。"""
    with lock:
        records = []
        seen = set()
        for t in tasks.values():
            seq_path = t.get("seq_path", "")
            rec = {
                "taskId": t["id"],
                "status": t["status"],
                "createTime": t.get("created_at", ""),
            }
            if seq_path and os.path.isfile(seq_path):
                rec["fileName"] = os.path.basename(seq_path)
                rec["fileSize"] = os.path.getsize(seq_path)
                seen.add(rec["fileName"])
            else:
                rec["fileName"] = ""
                rec["fileSize"] = 0
            records.append(rec)

        # 兜底：扫描磁盘上未被任务记录覆盖的 .seq 文件
        for f in sorted(os.listdir(BASE_DIR), reverse=True):
            if f.endswith(".seq") and f not in seen:
                fp = os.path.join(BASE_DIR, f)
                records.append({
                    "taskId": "",
                    "status": "unknown",
                    "createTime": datetime.fromtimestamp(os.path.getmtime(fp)).isoformat(),
                    "fileName": f,
                    "fileSize": os.path.getsize(fp),
                })

    return jsonify({"records": records}), 200


@app.route("/api/files/<task_id>", methods=["GET"])
def get_file(task_id: str) -> tuple[Any, int]:
    """GET /api/files/<task_id> — 下载 .seq 文件二进制流。"""
    with lock:
        task = tasks.get(task_id)

    if task is None:
        return jsonify({"error": "任务不存在"}), 404

    seq_path = task.get("seq_path")
    if not seq_path or not os.path.isfile(seq_path):
        return jsonify({"error": "文件尚未生成或已被删除"}), 404

    return send_file(seq_path, as_attachment=True, download_name=os.path.basename(seq_path))


@app.route("/api/push/<task_id>", methods=["POST"])
def push_to_git(task_id: str) -> tuple[Any, int]:
    """POST /api/push/<task_id> — 手动推送指定任务的 seq 文件到 GitHub。"""
    with lock:
        task = tasks.get(task_id)

    if task is None:
        return jsonify({"error": "任务不存在"}), 404

    if task["status"] != "completed":
        return jsonify({"error": f"任务未完成, 当前状态: {task['status']}"}), 400

    seq_name = task.get("seq_name")
    log_id = task.get("log_id", "")
    seq_path = task.get("seq_path")

    if not seq_name or not seq_path or not os.path.isfile(seq_path):
        return jsonify({"error": "seq 文件不存在, 无法推送"}), 404

    _git_commit_files(seq_name, log_id)

    with lock:
        tasks[task_id]["pushed"] = True
        tasks[task_id]["pushed_at"] = datetime.now().isoformat()

    return jsonify({
        "success": True,
        "message": f"已推送 {seq_name} 到 GitHub",
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
