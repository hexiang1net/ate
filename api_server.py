"""POST 接口: 触发 claude 命令生成 TestStand seq 文件。

启动:  pip install flask pymysql && python api_server.py
调用:  curl -X POST http://localhost:5050/api/run
      curl -X POST http://localhost:5050/api/addLog -H "Content-Type: application/json" -d "{\"plan_id\":\"xxx\",\"create_by\":\"admin\"}"
查询:  curl http://localhost:5050/api/status/<task_id>
"""

import logging
import re
import subprocess
import threading
import uuid
import os
from datetime import datetime
from typing import Any

import pymysql
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_DIR = r"e:\agent\ate"
LOG_FILE = os.path.join(BASE_DIR, "api_server.log")
TIMEOUT_SECONDS = 1800  # 30 分钟, 覆盖 20 分钟的 claude 执行

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


def _build_powershell_script(task_id: str, prompt: str, output_file: str) -> str:
    """构建 .ps1 脚本, 解决引号嵌套和编码问题。使用 cmd /c 来保留 > 的原生重定向。"""
    # 将 prompt 中的双引号转义
    safe_prompt = prompt.replace('"', '`"')
    # cmd /c 处理 > 重定向, 可避免 PowerShell 的 UTF-16 编码问题
    ps_script = (
        f'$cmd = \'claude -p "{safe_prompt}" --output-format stream-json --verbose --dangerously-skip-permissions > "{output_file}"\';'
        f"\n"
        f"cmd /c $cmd"
    )
    return ps_script


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


def _git_commit_files(excel_file: str, seq_name: str, output_file: str, log_id: str) -> None:
    """提交 3 个文件到 GitHub。"""
    git_output = os.path.join(BASE_DIR, "output_stream_github.json")
    prompt = (
        f"提交这3个文件到github "
        f"{{{os.path.basename(output_file)}}} "
        f"{{{seq_name}}} "
        f"{{{os.path.basename(excel_file)}}}"
    )
    logger.info(
        "_git_commit_files 开始: log_id=%s, files=[%s, %s, %s], git_output=%s",
        log_id, os.path.basename(output_file), seq_name, os.path.basename(excel_file), git_output,
    )
    ps_script = _build_powershell_script("git", prompt, git_output)
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", ps_script,
            ],
            cwd=BASE_DIR,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            stderr_tail = result.stderr.decode("utf-8", errors="replace")[-500:]
            logger.error(
                "_git_commit_files 失败: log_id=%s, returncode=%s, stderr=%s",
                log_id, result.returncode, stderr_tail,
            )
        else:
            logger.info("_git_commit_files 成功: log_id=%s", log_id)
    except subprocess.TimeoutExpired:
        logger.warning("_git_commit_files 超时: log_id=%s", log_id)
    except Exception:
        logger.exception("_git_commit_files 异常: log_id=%s", log_id)


def run_claude(
    task_id: str,
    prompt: str,
    output_file: str,
    log_id: str | None = None,
    excel_file: str = "",
    seq_name: str = "",
) -> None:
    """在后台线程中执行 claude 命令, 最长等待 TIMEOUT_SECONDS 秒。"""
    logger.info(
        "run_claude 入参: task_id=%s, prompt=%s, output_file=%s, log_id=%s, excel_file=%s, seq_name=%s",
        task_id, prompt, output_file, log_id, excel_file, seq_name,
    )
    with lock:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["started_at"] = datetime.now().isoformat()

    ps_script = _build_powershell_script(task_id, prompt, output_file)

    process: subprocess.Popen | None = None
    try:
        process = subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", ps_script,
            ],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        with lock:
            tasks[task_id]["pid"] = process.pid

        logger.info("run_claude 进程已启动: task_id=%s, pid=%s", task_id, process.pid)

        try:
            stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            logger.warning("run_claude 超时: task_id=%s, timeout=%ss", task_id, TIMEOUT_SECONDS)
            with lock:
                tasks[task_id]["status"] = "timeout"
                tasks[task_id]["finished_at"] = datetime.now().isoformat()
            if log_id:
                _update_log_end(log_id)
            return

        rc = process.returncode
        logger.info("run_claude 执行完毕: task_id=%s, returncode=%s", task_id, rc)
        with lock:
            tasks[task_id]["status"] = "completed" if rc == 0 else "failed"
            tasks[task_id]["returncode"] = rc
            tasks[task_id]["finished_at"] = datetime.now().isoformat()
            if stderr:
                stderr_tail = stderr.decode("utf-8", errors="replace")[-500:]
                tasks[task_id]["stderr_tail"] = stderr_tail
                if rc != 0:
                    logger.error("run_claude 失败: task_id=%s, stderr=%s", task_id, stderr_tail)

    except FileNotFoundError:
        logger.exception("run_claude 命令未找到: task_id=%s", task_id)
        with lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = "powershell 或 claude 命令未找到"
            tasks[task_id]["finished_at"] = datetime.now().isoformat()
    except Exception as exc:
        logger.exception("run_claude 异常: task_id=%s, error=%s", task_id, exc)
        with lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = str(exc)
            tasks[task_id]["finished_at"] = datetime.now().isoformat()

    if log_id:
        _update_log_end(log_id)

    # 提交 3 个文件到 GitHub
    if log_id and excel_file and seq_name:
        _git_commit_files(excel_file, seq_name, output_file, log_id)


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------

def _start_claude_task(excel_path: str, seq_name: str, output_file: str, log_id: str = "") -> str:
    """启动 claude 任务的通用逻辑, 返回 task_id。"""
    logger.info(
        "_start_claude_task 入参: excel_path=%s, seq_name=%s, output_file=%s, log_id=%s",
        excel_path, seq_name, output_file, log_id,
    )
    if not os.path.isabs(excel_path):
        excel_path = os.path.join(BASE_DIR, excel_path)
    if not os.path.isabs(output_file):
        output_file = os.path.join(BASE_DIR, output_file)

    prompt = (
        f"{excel_path} 根据这个excel的内容 "
        f"使用teststand mcp来生成一个seq文件，"
        f"文件命名为{seq_name} ,保存到当前目录即可"
    )

    task_id = str(uuid.uuid4())[:8]

    with lock:
        tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "prompt": prompt,
            "output_file": output_file,
            "log_id": log_id,
            "created_at": datetime.now().isoformat(),
        }

    thread = threading.Thread(
        target=run_claude,
        args=(task_id, prompt, output_file, log_id, excel_path, seq_name),
        daemon=True,
    )
    thread.start()
    logger.info("_start_claude_task 出参: task_id=%s", task_id)
    return task_id


@app.route("/api/run", methods=["POST"])
def run() -> tuple[Any, int]:
    """POST /api/run — 提交 claude 任务, 立即返回 task_id。

    可选 JSON body:
      {
        "excel_path":  "100-A18036D9-V1.0_report_v4.xlsx",
        "seq_name":    "bbb.seq",
        "output_file": "output_stream.json",
        "log_id":      ""
      }
    """
    data: dict[str, str] = request.get_json(silent=True) or {}

    excel_path = data.get("excel_path", "100-A18036D9-V1.0_report_v4.xlsx")
    seq_name = data.get("seq_name", "bbb.seq")
    output_file = data.get("output_file", "output_stream.json")
    log_id = data.get("log_id", "")

    task_id = _start_claude_task(excel_path, seq_name, output_file, log_id)

    return jsonify({
        "task_id": task_id,
        "status": "pending",
        "message": "任务已提交，通过 GET /api/status/<task_id> 查询进度",
    }), 202


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
    export_url = f"http://10.12.17.93:8282/jeecg-boot/ate/ateTestPlan/exportXls?id={plan_id}"
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

    # 下载成功后自动提交 claude 任务
    seq_name = f"{base}_{log_id}.seq"
    output_file = f"{base}_{log_id}.json"
    task_id = _start_claude_task(file_name, seq_name, output_file, log_id)

    return jsonify({
        "id": log_id,
        "status": "00",
        "message": "日志记录已创建",
        "file": file_name,
        "task_id": task_id,
    }), 201


@app.route("/api/status/<task_id>", methods=["GET"])
def status(task_id: str) -> tuple[Any, int]:
    """GET /api/status/<task_id> — 查询任务进度与结果。"""
    with lock:
        task = tasks.get(task_id)

    if task is None:
        return jsonify({"error": "任务不存在"}), 404

    return jsonify(task), 200


@app.route("/api/tasks", methods=["GET"])
def list_tasks() -> tuple[Any, int]:
    """GET /api/tasks — 列出所有任务记录。"""
    with lock:
        return jsonify(list(tasks.values())), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
