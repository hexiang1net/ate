"""Flask API 服务: Excel ↔ TestStand seq + 文档 → 测试计划 Excel。

启动:  pip install -r requirements_api.txt && python api_server.py

端点:
  POST /api/run               plan_id 下载 Excel → 生成 .seq
  POST /api/addLog            写日志 → 下载 Excel → 生成 .seq
  POST /api/doc-to-testplan   文档路径 → 生成测试计划 Excel
  GET  /api/status/<task_id>  查询任务状态
  GET  /api/tasks             列出所有任务
  GET  /api/files             列出所有产出文件
  GET  /api/files/<task_id>   下载任务产出文件
  POST /api/push/<task_id>    推送 .seq 文件到 GitHub
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
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file

# 加载 .env 配置（从 teststand-2012-mcp/doc_to_testplan/.env）
_dotenv_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "teststand-2012-mcp", "doc_to_testplan", ".env",
)
load_dotenv(_dotenv_path)

# 添加 excel_to_seq 所在目录到 sys.path
_EXCEL_TO_SEQ_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teststand-2012-mcp")
if _EXCEL_TO_SEQ_DIR not in sys.path:
    sys.path.insert(0, _EXCEL_TO_SEQ_DIR)

from excel_to_seq import ExcelParser, SeqGenerator
from doc_to_testplan import TestPlanGenerator

app = Flask(__name__)

BASE_DIR = r"D:\agent\ate"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
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


def _ensure_output_dir() -> None:
    """确保 OUTPUT_DIR 存在。"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _find_file_in_output(task_id: str) -> str | None:
    """在 OUTPUT_DIR 中精确匹配 task_id (文件名前缀) 的文件, 返回完整路径或 None。

    匹配规则: 文件名(不含扩展名)以 task_id 开头，避免 8 位 uuid 子串误匹配。
    """
    if not os.path.isdir(OUTPUT_DIR):
        return None
    try:
        for f in os.listdir(OUTPUT_DIR):
            name_no_ext, ext = os.path.splitext(f)
            if name_no_ext == task_id or name_no_ext.startswith(task_id + "_"):
                return os.path.join(OUTPUT_DIR, f)
    except OSError:
        pass
    return None


def _build_orphan_record(filepath: str) -> dict:
    """从磁盘文件构建任务记录(用于内存中不存在该任务的情况)。"""
    fname = os.path.basename(filepath)
    name_no_ext = os.path.splitext(fname)[0]
    stat = os.stat(filepath)
    return {
        "id": name_no_ext,
        "status": "completed",
        "seq_path": filepath,
        "seq_name": fname,
        "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "finished_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "_orphan": True,
    }


def _recover_tasks_from_disk() -> None:
    """启动时从 OUTPUT_DIR 恢复已有文件的任务记录。"""
    if not os.path.isdir(OUTPUT_DIR):
        return
    try:
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".seq") or f.endswith("_TestPlan.xlsx"):
                fp = os.path.join(OUTPUT_DIR, f)
                name_no_ext = os.path.splitext(f)[0]
                if name_no_ext not in tasks:
                    tasks[name_no_ext] = _build_orphan_record(fp)
        logger.info("从磁盘恢复了 %d 个历史任务",
                     sum(1 for t in tasks.values() if t.get("_orphan")))
    except OSError:
        logger.exception("从磁盘恢复任务时出错")


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


def _git_commit_files(seq_name: str, log_id: str) -> bool:
    """提交 seq 文件到 GitHub (直接使用 git 命令). 返回 True 表示成功。"""
    logger.info("_git_commit_files 开始: seq_name=%s, log_id=%s", seq_name, log_id)
    try:
        seq_path = os.path.join(OUTPUT_DIR, seq_name)
        add_result = subprocess.run(
            ["git", "add", seq_path], cwd=BASE_DIR,
            capture_output=True, timeout=30,
        )
        if add_result.returncode != 0:
            add_err = add_result.stderr.decode("utf-8", errors="replace").strip()
            logger.error("_git_commit_files git add 失败: seq_path=%s, stderr=%s", seq_path, add_err)
            return False

        commit_result = subprocess.run(
            ["git", "commit", "-m", f"feat: 生成测试序列 {seq_name}"],
            cwd=BASE_DIR, capture_output=True, timeout=30,
        )
        if commit_result.returncode != 0:
            combined = (
                commit_result.stdout.decode("utf-8", errors="replace") + "\n"
                + commit_result.stderr.decode("utf-8", errors="replace")
            )
            if "nothing to commit" in combined or "nothing added to commit" in combined:
                logger.info("_git_commit_files: 无变更需要提交")
                return True
            logger.error("_git_commit_files 提交失败: stdout=%s stderr=%s",
                         commit_result.stdout.decode("utf-8", errors="replace")[-500:],
                         commit_result.stderr.decode("utf-8", errors="replace")[-500:])
            return False

        push_result = subprocess.run(
            ["git", "push"], cwd=BASE_DIR,
            capture_output=True, timeout=60,
        )
        if push_result.returncode != 0:
            push_err = push_result.stderr.decode("utf-8", errors="replace").strip()
            logger.error("_git_commit_files git push 失败: %s", push_err[-500:])
            return False

        logger.info("_git_commit_files 成功: log_id=%s", log_id)
        return True
    except Exception:
        logger.exception("_git_commit_files 异常: log_id=%s", log_id)
        return False


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
        seq_path = os.path.join(OUTPUT_DIR, seq_name)
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
        excel_path = os.path.join(OUTPUT_DIR, excel_path)

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


def run_doc_to_testplan(
    task_id: str,
    doc_path: str,
    output_name: str,
    provider: str | None = None,
    model: str | None = None,
    use_images: bool = True,
) -> None:
    """在后台线程中执行文档 → testplan Excel 转换。"""
    logger.info("run_doc_to_testplan 入参: task_id=%s, doc_path=%s", task_id, doc_path)
    with lock:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["started_at"] = datetime.now().isoformat()

    try:
        output_path = os.path.join(OUTPUT_DIR, output_name)
        generator = TestPlanGenerator()
        report = generator.generate(
            doc_path=doc_path,
            output_xlsx=output_path,
            provider=provider,
            model=model,
            verbose=False,
            use_images=use_images,
        )
        logger.info("testplan 生成完成: task_id=%s, test_cases=%d",
                     task_id, len(report.test_cases))

        with lock:
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["output_path"] = output_path
            tasks[task_id]["output_name"] = output_name
            tasks[task_id]["test_case_count"] = len(report.test_cases)
            tasks[task_id]["finished_at"] = datetime.now().isoformat()

    except Exception as exc:
        logger.exception("run_doc_to_testplan 异常: task_id=%s, error=%s", task_id, exc)
        with lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = str(exc)
            tasks[task_id]["finished_at"] = datetime.now().isoformat()


def _start_doc_to_testplan_task(
    doc_path: str,
    output_name: str,
    provider: str | None = None,
    model: str | None = None,
    use_images: bool = True,
) -> str:
    """启动文档→testplan 任务, 返回 task_id。"""
    logger.info("_start_doc_to_testplan_task 入参: doc_path=%s", doc_path)

    task_id = str(uuid.uuid4())[:8]

    with lock:
        tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "doc_path": doc_path,
            "output_name": output_name,
            "provider": provider,
            "model": model,
            "use_images": use_images,
            "created_at": datetime.now().isoformat(),
        }

    thread = threading.Thread(
        target=run_doc_to_testplan,
        args=(task_id, doc_path, output_name, provider, model, use_images),
        daemon=True,
    )
    thread.start()
    logger.info("_start_doc_to_testplan_task 出参: task_id=%s", task_id)
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
        file_path = os.path.join(OUTPUT_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(resp.content)
    except Exception as exc:
        return jsonify({"error": f"下载 Excel 失败: {exc}"}), 500

    seq_name = f"{base}_{plan_id}.seq"
    task_id = _start_excel_to_seq_task(file_name, seq_name)

    return jsonify({"task_id": task_id}), 202


@app.route("/api/doc-to-testplan", methods=["POST"])
def doc_to_testplan() -> tuple[Any, int]:
    """POST /api/doc-to-testplan — 上传测试文档或指定路径，生成测试计划 Excel。

    方式 1 — 文件上传 (multipart/form-data):
      file:        测试文档 (.docx/.pdf/.xlsx/.md/.txt 等)
      provider:    LLM 提供商 (可选, 默认 claude)
      model:       模型名称 (可选)
      use_images:  是否提取图片 (可选, 默认 true)

    方式 2 — 服务器路径 (JSON, 兼容旧版):
      { "doc_path": "D:\\docs\\test_spec.docx", "provider": "claude", ... }

    Response:  {"task_id": "xxx", "output": "xxx_TestPlan.xlsx"}
    """
    _ensure_output_dir()
    provider: str | None = None
    model: str | None = None
    use_images: bool = True
    doc_path: str = ""
    doc_name: str = ""

    # ── 方式 1: 文件上传 (multipart) ──
    uploaded = request.files.get("file")
    if uploaded and uploaded.filename:
        safe_name = f"upload_{str(uuid.uuid4())[:8]}_{uploaded.filename}"
        save_path = os.path.join(OUTPUT_DIR, safe_name)
        uploaded.save(save_path)
        doc_path = save_path
        doc_name = os.path.splitext(uploaded.filename)[0]
        provider = request.form.get("provider") or None
        model = request.form.get("model") or None
        use_images = request.form.get("use_images", "true").lower() in ("true", "1")
    else:
        # ── 方式 2: JSON body (doc_path, 兼容旧版) ──
        data: dict[str, str] = request.get_json(silent=True) or {}
        doc_path = data.get("doc_path", "")
        if not doc_path:
            return jsonify({"error": "请上传文件 (file) 或提供 doc_path"}), 400
        if not os.path.isfile(doc_path):
            return jsonify({"error": f"文档不存在: {doc_path}"}), 400
        provider = data.get("provider")
        model = data.get("model")
        use_images = data.get("use_images", True)
        if not isinstance(use_images, bool):
            use_images = True
        doc_name = os.path.splitext(os.path.basename(doc_path))[0]

    output_name = f"{doc_name}_TestPlan.xlsx"
    task_id = _start_doc_to_testplan_task(
        doc_path=doc_path,
        output_name=output_name,
        provider=provider,
        model=model,
        use_images=use_images,
    )

    return jsonify({"task_id": task_id, "output": output_name}), 202


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
        file_path = os.path.join(OUTPUT_DIR, file_name)

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

    # Excel→seq 任务: seq_path
    if task.get("status") == "completed" and task.get("seq_path"):
        fpath = task["seq_path"]
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            resp["fileName"] = os.path.basename(fpath)
            resp["fileSize"] = stat.st_size

    # 文档→testplan 任务: output_path
    if task.get("status") == "completed" and task.get("output_path"):
        fpath = task["output_path"]
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            resp["fileName"] = os.path.basename(fpath)
            resp["fileSize"] = stat.st_size

    return resp


@app.route("/api/status/<task_id>", methods=["GET"])
def status(task_id: str) -> tuple[Any, int]:
    """GET /api/status/<task_id> — 查询任务进度与结果。"""
    with lock:
        task = tasks.get(task_id)

    if task is None:
        # 内存中找不到时, 从 OUTPUT_DIR 扫描匹配文件
        seq_path = _find_file_in_output(task_id)
        if seq_path:
            return jsonify(_build_status_response(_build_orphan_record(seq_path))), 200
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
            out_path = t.get("output_path", "")
            # 优先使用实际存在的文件路径
            file_path = seq_path if os.path.isfile(seq_path) else (out_path if os.path.isfile(out_path) else "")
            rec = {
                "taskId": t["id"],
                "status": t["status"],
                "createTime": t.get("created_at", ""),
            }
            if file_path:
                rec["fileName"] = os.path.basename(file_path)
                rec["fileSize"] = os.path.getsize(file_path)
                seen.add(rec["fileName"])
            else:
                rec["fileName"] = ""
                rec["fileSize"] = 0
            records.append(rec)

        # 兜底：扫描 OUTPUT_DIR 中未被任务记录覆盖的 .seq / .xlsx 文件
        for f in sorted(os.listdir(OUTPUT_DIR), reverse=True):
            if (f.endswith(".seq") or f.endswith("_TestPlan.xlsx")) and f not in seen:
                fp = os.path.join(OUTPUT_DIR, f)
                name_no_ext = os.path.splitext(f)[0]
                records.append({
                    "taskId": name_no_ext,
                    "status": "completed",
                    "createTime": datetime.fromtimestamp(os.path.getmtime(fp)).isoformat(),
                    "fileName": f,
                    "fileSize": os.path.getsize(fp),
                })

    return jsonify({"records": records}), 200


@app.route("/api/files/<task_id>", methods=["GET"])
def get_file(task_id: str) -> tuple[Any, int]:
    """GET /api/files/<task_id> — 下载任务产出文件。"""
    with lock:
        task = tasks.get(task_id)

    # 内存中找不到时, 从 OUTPUT_DIR 扫描匹配文件
    if task is None:
        seq_path = _find_file_in_output(task_id)
        if seq_path:
            return send_file(seq_path, as_attachment=True, download_name=os.path.basename(seq_path))
        return jsonify({"error": "任务不存在"}), 404

    # Excel→seq: seq_path; 文档→testplan: output_path
    file_path = task.get("seq_path") or task.get("output_path")
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": "文件尚未生成或已被删除"}), 404

    return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))


@app.route("/api/push/<task_id>", methods=["POST"])
def push_to_git(task_id: str) -> tuple[Any, int]:
    """POST /api/push/<task_id> — 手动推送指定任务的 seq 文件到 GitHub。"""
    with lock:
        task = tasks.get(task_id)

    if task is None:
        # 内存中找不到时, 从 OUTPUT_DIR 扫描匹配文件
        seq_path = _find_file_in_output(task_id)
        if seq_path and os.path.isfile(seq_path):
            seq_name = os.path.basename(seq_path)
            ok = _git_commit_files(seq_name, "")
            if ok:
                return jsonify({
                    "success": True,
                    "message": f"已推送 {seq_name} 到 GitHub",
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": f"推送 {seq_name} 失败，详见 api_server.log",
                }), 500
        return jsonify({"error": "任务不存在"}), 404

    if task["status"] != "completed":
        return jsonify({"error": f"任务未完成, 当前状态: {task['status']}"}), 400

    seq_name = task.get("seq_name")
    log_id = task.get("log_id", "")
    seq_path = task.get("seq_path")

    if not seq_name or not seq_path or not os.path.isfile(seq_path):
        return jsonify({"error": "seq 文件不存在, 无法推送"}), 404

    ok = _git_commit_files(seq_name, log_id)

    if ok:
        with lock:
            tasks[task_id]["pushed"] = True
            tasks[task_id]["pushed_at"] = datetime.now().isoformat()
        return jsonify({
            "success": True,
            "message": f"已推送 {seq_name} 到 GitHub",
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": f"推送 {seq_name} 失败，详见 api_server.log",
        }), 500


if __name__ == "__main__":
    _ensure_output_dir()
    _recover_tasks_from_disk()
    app.run(host="0.0.0.0", port=5050, debug=False)
