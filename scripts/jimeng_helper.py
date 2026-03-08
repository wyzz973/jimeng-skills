#!/usr/bin/env python3
"""即梦 AI 通用辅助脚本 - 提交任务、轮询结果、下载文件"""

import json, os, sys, time, base64, requests
from volcengine.visual.VisualService import VisualService


def get_service():
    config_path = os.path.expanduser("~/.jimeng/config.json")
    if not os.path.exists(config_path):
        print(json.dumps({"error": "未配置密钥，请先配置 ~/.jimeng/config.json"}))
        sys.exit(1)
    with open(config_path) as f:
        config = json.load(f)
    vs = VisualService()
    vs.set_ak(config["access_key"])
    vs.set_sk(config["secret_key"])
    return vs


def read_file_base64(path):
    with open(os.path.expanduser(path), "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def submit_task(form):
    vs = get_service()
    resp = vs.cv_sync2async_submit_task(form)
    print(json.dumps(resp, ensure_ascii=False, indent=2))


def submit_task_sync(form):
    """用于主体识别等同步任务"""
    vs = get_service()
    resp = vs.cv_submit_task(form)
    print(json.dumps(resp, ensure_ascii=False, indent=2))


def poll_result(req_key, task_id, max_wait=300, interval=5):
    vs = get_service()
    elapsed = 0
    while elapsed < max_wait:
        form = {"req_key": req_key, "task_id": task_id}
        resp = vs.cv_sync2async_get_result(form)
        data = resp.get("data", {})
        status = str(data.get("status", ""))
        if status == "done" or data.get("image_urls") or data.get("video_url") or data.get("resp_data"):
            print(json.dumps(resp, ensure_ascii=False, indent=2))
            return
        if "fail" in status.lower() or "error" in status.lower():
            print(json.dumps(resp, ensure_ascii=False, indent=2))
            return
        time.sleep(interval)
        elapsed += interval
    print(json.dumps({"error": "任务超时", "task_id": task_id, "elapsed": elapsed}))


def download_file(url, save_dir, prefix, ext):
    save_dir = os.path.expanduser(save_dir)
    os.makedirs(save_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    filepath = os.path.join(save_dir, filename)
    r = requests.get(url, stream=True)
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    size_mb = os.path.getsize(filepath) / 1024 / 1024
    print(json.dumps({"path": filepath, "size_mb": round(size_mb, 2)}))


def save_input_file(url, ext="jpg"):
    save_dir = os.path.expanduser("~/jimeng-images/input")
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, f"input_{int(time.time())}.{ext}")
    r = requests.get(url)
    with open(filepath, "wb") as f:
        f.write(r.content)
    print(filepath)
    return filepath


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p_submit = sub.add_parser("submit")
    p_submit.add_argument("--form", required=True, help="JSON form data")

    p_submit_sync = sub.add_parser("submit-sync")
    p_submit_sync.add_argument("--form", required=True, help="JSON form data")

    p_poll = sub.add_parser("poll")
    p_poll.add_argument("--req-key", required=True)
    p_poll.add_argument("--task-id", required=True)
    p_poll.add_argument("--max-wait", type=int, default=300)
    p_poll.add_argument("--interval", type=int, default=5)

    p_dl = sub.add_parser("download")
    p_dl.add_argument("--url", required=True)
    p_dl.add_argument("--dir", default="~/jimeng-videos")
    p_dl.add_argument("--prefix", default="jimeng")
    p_dl.add_argument("--ext", default="mp4")

    p_b64 = sub.add_parser("base64")
    p_b64.add_argument("--file", required=True)

    p_save = sub.add_parser("save-url")
    p_save.add_argument("--url", required=True)
    p_save.add_argument("--ext", default="jpg")

    args = parser.parse_args()

    if args.cmd == "submit":
        submit_task(json.loads(args.form))
    elif args.cmd == "submit-sync":
        submit_task_sync(json.loads(args.form))
    elif args.cmd == "poll":
        poll_result(args.req_key, args.task_id, args.max_wait, args.interval)
    elif args.cmd == "download":
        download_file(args.url, args.dir, args.prefix, args.ext)
    elif args.cmd == "base64":
        print(read_file_base64(args.file))
    elif args.cmd == "save-url":
        save_input_file(args.url, args.ext)
    else:
        parser.print_help()
