"""
阿里云"录音文件识别闲时版"批量识别小工具.

依赖:
    pip install 'aliyun-python-sdk-core==2.13.3'

凭证 (优先环境变量, 缺失则读 ~/.config/aliyun-asr/credentials):
    ALIYUN_AK_ID       阿里云 AccessKey ID
    ALIYUN_AK_SECRET   阿里云 AccessKey Secret
    NLS_APP_KEY        智能语音交互控制台里项目的 Appkey

用法:
    # 1. 准备 CSV (必须带 header), 例如 jobs.csv:
    #     url,output_name
    #     https://x.com/a.mp3,meeting_0501
    #     https://x.com/b.mp3,interview_li
    python aliyun_asr.py submit --csv jobs.csv

    # 2. 隔天 / 任何时刻回收结果
    python aliyun_asr.py poll                            # 扫所有未完成
    python aliyun_asr.py poll --since 2026-05-24         # 只查这天之后提交的
    python aliyun_asr.py poll --since 2026-05-24 --until 2026-05-25
    # 成功后会在 ./outputs/ 下生成:
    #   meeting_0501.txt   (纯文本, 一句一行)
    #   meeting_0501.json  (阿里云原始 Result, 含时间戳/声道/词级)

    # 3. 看看状态
    python aliyun_asr.py list
    python aliyun_asr.py list --status done
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

DOMAIN = "speechfiletranscriberlite.cn-shanghai.aliyuncs.com"
REGION = "cn-shanghai"
PRODUCT = "SpeechFileTranscriberLite"
API_VERSION = "2021-12-21"

STATUS_QUEUED = 21050002
STATUS_RUNNING = 21050001
STATUS_SUCCESS = 21050000

DEFAULT_STORE = Path("tasks.jsonl")
DEFAULT_OUTDIR = Path("outputs")

CREDENTIAL_KEYS = ("ALIYUN_AK_ID", "ALIYUN_AK_SECRET", "NLS_APP_KEY")
CONFIG_PATH = Path.home() / ".config" / "aliyun-asr" / "credentials"


def _parse_credential_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in CREDENTIAL_KEYS:
            out[key] = value
    return out


def load_credential(key: str) -> str | None:
    val = os.environ.get(key)
    if val:
        return val
    if CONFIG_PATH.exists():
        return _parse_credential_file(CONFIG_PATH).get(key)
    return None


def make_client() -> AcsClient:
    ak_id = load_credential("ALIYUN_AK_ID")
    ak_secret = load_credential("ALIYUN_AK_SECRET")
    if not ak_id or not ak_secret:
        sys.exit(
            f"缺少 ALIYUN_AK_ID / ALIYUN_AK_SECRET (环境变量或 {CONFIG_PATH})"
        )
    return AcsClient(ak_id, ak_secret, REGION)


def submit_one(client: AcsClient, app_key: str, file_link: str, enable_words: bool) -> dict:
    req = CommonRequest()
    req.set_domain(DOMAIN)
    req.set_version(API_VERSION)
    req.set_product(PRODUCT)
    req.set_action_name("SubmitTask")
    req.set_method("POST")
    task = {"appkey": app_key, "file_link": file_link, "enable_words": enable_words}
    req.add_body_params("Task", json.dumps(task))
    resp = client.do_action_with_exception(req)
    return json.loads(resp)


def query_one(client: AcsClient, task_id: str) -> dict:
    req = CommonRequest()
    req.set_domain(DOMAIN)
    req.set_version(API_VERSION)
    req.set_product(PRODUCT)
    req.set_action_name("GetTaskResult")
    req.set_method("GET")
    req.add_query_param("TaskId", task_id)
    resp = client.do_action_with_exception(req)
    return json.loads(resp)


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append_record(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def rewrite_records(path: Path, records: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_jobs(csv_path: Path) -> list[dict]:
    """读 CSV, 必须有 header: url, output_name. 返回 [{url, output_name}, ...]."""
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "url" not in reader.fieldnames or "output_name" not in reader.fieldnames:
            sys.exit(f"CSV 必须包含 header: url,output_name (当前: {reader.fieldnames})")
        jobs = []
        for i, row in enumerate(reader, start=2):  # 行号从 2 起 (1 是 header)
            url = (row.get("url") or "").strip()
            name = (row.get("output_name") or "").strip()
            if not url:
                continue
            if not name:
                sys.exit(f"第 {i} 行缺 output_name")
            if "/" in name or "\\" in name or name in (".", ".."):
                sys.exit(f"第 {i} 行 output_name 不能含路径分隔符: {name!r}")
            jobs.append({"url": url, "output_name": name})
    return jobs


def cmd_submit(args: argparse.Namespace) -> None:
    app_key = load_credential("NLS_APP_KEY")
    if not app_key:
        sys.exit(f"缺少 NLS_APP_KEY (环境变量或 {CONFIG_PATH})")

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"CSV 文件不存在: {csv_path}")

    jobs = read_jobs(csv_path)
    if not jobs:
        sys.exit("CSV 没有有效行")

    store = Path(args.tasks)
    existing_records = load_records(store)
    existing_urls = {r["file_link"] for r in existing_records} if not args.allow_dup else set()
    existing_names = {r.get("output_name") for r in existing_records if r.get("output_name")}

    # 提前检查 CSV 内部 output_name 冲突, 以及和已提交记录的冲突
    seen_names: dict[str, str] = {}
    for j in jobs:
        if j["output_name"] in seen_names and seen_names[j["output_name"]] != j["url"]:
            sys.exit(f"CSV 内 output_name 重复: {j['output_name']}")
        seen_names[j["output_name"]] = j["url"]
        if j["output_name"] in existing_names and j["url"] not in existing_urls:
            sys.exit(
                f"output_name {j['output_name']!r} 已被另一条 URL 使用, "
                f"换个名字或加 --allow-dup"
            )

    client = make_client()
    skip = sum(1 for j in jobs if j["url"] in existing_urls)
    print(f"准备提交 {len(jobs)} 条, 已存在跳过 {skip} 条")

    ok = fail = 0
    for j in jobs:
        if j["url"] in existing_urls:
            continue
        try:
            resp = submit_one(client, app_key, j["url"], args.enable_words)
        except Exception as exc:
            fail += 1
            print(f"  [FAIL] {j['url']}: {exc}")
            continue

        record = {
            "task_id": resp.get("TaskId"),
            "file_link": j["url"],
            "output_name": j["output_name"],
            "submitted_at": now_iso(),
            "status_code": resp.get("StatusCode"),
            "status_text": resp.get("StatusText", ""),
            "finished_at": None,
            "written_at": None,
        }
        append_record(store, record)
        ok += 1
        print(f"  [OK ] {record['task_id']}  -> {j['output_name']}.txt")

    print(f"完成: 成功 {ok}, 失败 {fail}, 状态文件: {store}")


def write_outputs(outdir: Path, name: str, result: dict) -> tuple[Path, Path]:
    """写两个文件: <name>.txt (拼接文本) + <name>.json (原始 Result)."""
    outdir.mkdir(parents=True, exist_ok=True)
    txt_path = outdir / f"{name}.txt"
    json_path = outdir / f"{name}.json"

    sentences = (result or {}).get("Sentences") or []
    lines = [(s.get("Text") or "").strip() for s in sentences]
    txt_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return txt_path, json_path


def cmd_poll(args: argparse.Namespace) -> None:
    store = Path(args.tasks)
    records = load_records(store)
    if not records:
        sys.exit(f"没有任务: {store}")

    outdir = Path(args.outdir)
    since = datetime.fromisoformat(args.since).astimezone() if args.since else None
    until = datetime.fromisoformat(args.until).astimezone() if args.until else None

    def in_window(r: dict) -> bool:
        if r.get("finished_at"):
            return False
        ts = datetime.fromisoformat(r["submitted_at"])
        if since and ts < since:
            return False
        if until and ts >= until:
            return False
        return True

    todo = [r for r in records if in_window(r)]
    print(f"待查询 {len(todo)} / 总计 {len(records)} 条, 输出目录: {outdir}")

    if not todo:
        return

    client = make_client()
    changed = 0
    for r in todo:
        try:
            resp = query_one(client, r["task_id"])
        except Exception as exc:
            print(f"  [ERR ] {r['task_id']}: {exc}")
            continue

        code = resp.get("StatusCode")
        r["status_code"] = code
        r["status_text"] = resp.get("StatusText", "")

        if code == STATUS_SUCCESS:
            name = r.get("output_name") or r["task_id"]
            txt_path, _ = write_outputs(outdir, name, resp.get("Result") or {})
            r["finished_at"] = now_iso()
            r["written_at"] = r["finished_at"]
            changed += 1
            print(f"  [DONE] {r['task_id']}  -> {txt_path}")
        elif code in (STATUS_QUEUED, STATUS_RUNNING):
            print(f"  [WAIT] {r['task_id']}  {r['status_text']}")
        else:
            r["finished_at"] = now_iso()
            changed += 1
            print(f"  [FAIL] {r['task_id']}  code={code} {r['status_text']}")

        if args.sleep:
            time.sleep(args.sleep)

    rewrite_records(store, records)
    print(f"更新 {changed} 条, 写回 {store}")


def cmd_list(args: argparse.Namespace) -> None:
    records = load_records(Path(args.tasks))
    if args.status == "pending":
        records = [r for r in records if not r.get("finished_at")]
    elif args.status == "done":
        records = [r for r in records if r.get("status_code") == STATUS_SUCCESS]
    elif args.status == "failed":
        records = [
            r
            for r in records
            if r.get("finished_at") and r.get("status_code") != STATUS_SUCCESS
        ]

    for r in records:
        marker = "✓" if r.get("status_code") == STATUS_SUCCESS else (
            "✗" if r.get("finished_at") else "…"
        )
        name = r.get("output_name") or "-"
        print(f"{marker} {r['submitted_at']}  {r['task_id']}  {name}  {r['file_link']}")
    print(f"--- {len(records)} 条")


def main() -> None:
    p = argparse.ArgumentParser(description="Aliyun ASR off-peak batch tool")
    p.add_argument("--tasks", default=str(DEFAULT_STORE), help="状态文件 (jsonl)")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("submit", help="提交 CSV 中的一批任务")
    ps.add_argument("--csv", required=True, help="CSV 文件, header: url,output_name")
    ps.add_argument("--enable-words", action="store_true", help="返回词级别时间戳")
    ps.add_argument("--allow-dup", action="store_true", help="不去重, 重复提交同一 URL")
    ps.set_defaults(func=cmd_submit)

    pp = sub.add_parser("poll", help="查询未完成任务的结果")
    pp.add_argument("--since", help="只查这个时间之后提交的 (ISO: 2026-05-24)")
    pp.add_argument("--until", help="只查这个时间之前提交的 (ISO)")
    pp.add_argument("--outdir", default=str(DEFAULT_OUTDIR), help="结果输出目录")
    pp.add_argument("--sleep", type=float, default=0.0, help="每次查询后 sleep 秒数")
    pp.set_defaults(func=cmd_poll)

    pl = sub.add_parser("list", help="列出任务")
    pl.add_argument(
        "--status",
        choices=["all", "pending", "done", "failed"],
        default="all",
    )
    pl.set_defaults(func=cmd_list)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
