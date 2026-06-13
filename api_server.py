"""POST 接口: 触发 claude 命令生成 TestStand seq 文件。

启动:  pip install flask && python api_server.py
调用:  curl -X POST http://localhost:8080/api/run
查询:  curl http://localhost:8080/api/status/<task_id>
"""

import subprocess
import threading
import uuid
import os
from datetime import datetime
from typing import Any

from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_DIR = r"e:\agent\ate"
TIMEOUT_SECONDS = 1800  # 30 分钟, 覆盖 20 分钟的 claude 执行

# ---- 任务状态存储 ----
tasks: dict[str, dict[str, Any]] = {}
lock = threading.Lock()


def _build_powershell_script(task_id: str, prompt: str, output_file: str) -> str:
    """构建 .ps1 脚本, 解决引号嵌套和编码问题。使用 cmd /c 来保留 > 的原生重定向。"""
    # 将 prompt 中的双引号转义
    safe_prompt = prompt.replace('"', '`"')
    # cmd /c 处理 > 重定向, 可避免 PowerShell 的 UTF-16 编码问题
    ps_script = (
        f'$cmd = \'claude -p "{safe_prompt}" --output-format stream-json > "{output_file}"\';'
        f"\n"
        f"cmd /c $cmd"
    )
    return ps_script


def run_claude(task_id: str, prompt: str, output_file: str) -> None:
    """在后台线程中执行 claude 命令, 最长等待 TIMEOUT_SECONDS 秒。"""
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

        try:
            stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            with lock:
                tasks[task_id]["status"] = "timeout"
                tasks[task_id]["finished_at"] = datetime.now().isoformat()
            return

        rc = process.returncode
        with lock:
            tasks[task_id]["status"] = "completed" if rc == 0 else "failed"
            tasks[task_id]["returncode"] = rc
            tasks[task_id]["finished_at"] = datetime.now().isoformat()
            if stderr:
                tasks[task_id]["stderr_tail"] = stderr.decode("utf-8", errors="replace")[-500:]

    except FileNotFoundError:
        with lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = "powershell 或 claude 命令未找到"
            tasks[task_id]["finished_at"] = datetime.now().isoformat()
    except Exception as exc:
        with lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = str(exc)
            tasks[task_id]["finished_at"] = datetime.now().isoformat()


# ---------------------------------------------------------------------------
# API 端点
# ---------------------------------------------------------------------------

@app.route("/api/run", methods=["POST"])
def run() -> tuple[Any, int]:
    """POST /api/run — 提交 claude 任务, 立即返回 task_id。

    可选 JSON body:
      {
        "excel_path":  "100-A18036D9-V1.0_report_v4.xlsx",
        "seq_name":    "bbb.seq",
        "output_file": "output_stream.json"
      }
    """
    data: dict[str, str] = request.get_json(silent=True) or {}

    excel_path = data.get("excel_path", "100-A18036D9-V1.0_report_v4.xlsx")
    seq_name = data.get("seq_name", "bbb.seq")
    output_file = data.get("output_file", "output_stream.json")

    if not os.path.isabs(excel_path):
        excel_path = os.path.join(BASE_DIR, excel_path)
    if not os.path.isabs(output_file):
        output_file = os.path.join(BASE_DIR, output_file)

    prompt = (
        f"{excel_path} 根据这个excle的内容 "
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
            "created_at": datetime.now().isoformat(),
        }

    thread = threading.Thread(
        target=run_claude,
        args=(task_id, prompt, output_file),
        daemon=True,
    )
    thread.start()

    return jsonify({
        "task_id": task_id,
        "status": "pending",
        "message": "任务已提交，通过 GET /api/status/<task_id> 查询进度",
    }), 202


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
    app.run(host="127.0.0.1", port=5050, debug=False)
