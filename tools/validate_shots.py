# -*- coding: utf-8 -*-
"""按 workflow/01-小说转分镜.md 的校验规则检查分镜表 JSON。"""
import json
import sys
from pathlib import Path


def validate(data):
    errs = []
    shots = data.get("shots", [])
    total = sum(s.get("dur", 0) for s in shots)
    if abs(total - data.get("total_duration", 0)) > 5:
        errs.append(f"总时长偏差过大: {total}s vs {data.get('total_duration')}s")
    if len(shots) < 15:
        errs.append(f"镜数过少: {len(shots)}")

    segs = {s.get("seg") for s in shots}
    if segs != {1, 2, 3, 4, 5, 6}:
        errs.append(f"六段结构不完整，缺段: {set(range(1, 7)) - segs}")

    looks = {l for c in data.get("characters", []) for l in c.get("looks", {})}
    for s in shots:
        sid = s.get("shot", "?")
        if s.get("look") not in looks:
            errs.append(f"镜 {sid} 引用了未定义的 LOOK: {s.get('look')}")
        if len(s.get("content", "")) > 60:
            errs.append(f"镜 {sid} content 过长，可能塞了多个动作")
        if s.get("prompt"):
            errs.append(f"镜 {sid} prompt 应为空（由脚本拼接）")
        if not (1.0 <= s.get("dur", 0) <= 6.0):
            errs.append(f"镜 {sid} 时长越界: {s.get('dur')}")
        for f in ("size", "angle", "move", "lens", "light", "emotion"):
            if not s.get(f):
                errs.append(f"镜 {sid} 缺少字段 {f}")

    dup = len(shots) - len({s.get("shot") for s in shots})
    if dup:
        errs.append(f"镜号重复 {dup} 处")
    return errs


def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errs = validate(data)
    n = len(data.get("shots", []))
    total = sum(s.get("dur", 0) for s in data.get("shots", []))
    print(f"文件: {path}")
    print(f"镜数: {n}  总时长: {total}s  题材: {data.get('genre')}")
    if errs:
        print(f"\n发现 {len(errs)} 个问题:")
        for e in errs:
            print("  ERR", e)
        return 1
    print("\n校验通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "examples/都市甜宠-第1集-分镜表.json"))
