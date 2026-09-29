# -*- coding: utf-8 -*-
"""README 引用的每一张本地图，是否真的都在 git 里。

背景：曾经加过一条 .gitignore 规则，文件在本地好好躺着，但同名新文件
一直没被提交，线上 404 才发现。所以"文件存在"不等于"线上有"，
必须拿 git ls-files（真正提交上去的清单）来对。

顺带查：外部图 URL 是否可访问、?v= 是否同一资产只有一个值。
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")

txt = open(README, encoding="utf-8").read()

tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.splitlines())
tracked = {p.replace("\\", "/") for p in tracked}

print("=" * 66)
print("1) 本地图是否都在 git 里")
local = re.findall(r'(?:\./)?(assets/[\w\-./]+\.(?:gif|svg|webp|png|jpg))', txt)
bad = 0
for a in sorted(set(local)):
    a = a.lstrip("./")
    in_disk = os.path.exists(os.path.join(ROOT, a))
    in_git = a in tracked
    ok = in_disk and in_git
    if not ok:
        bad += 1
    print("   %-4s %-46s disk=%-5s git=%s" % ("OK" if ok else "FAIL", a, in_disk, in_git))
print("   -> 引用 %d 张，失败 %d 张" % (len(set(local)), bad))

print("=" * 66)
print("2) 被 gitignore 挡住的资产（存在但没提交 = 线上 404）")
orphans = []
for a in sorted(set(local)):
    if os.path.exists(os.path.join(ROOT, a)) and a not in tracked:
        orphans.append(a)
print("   " + ("、".join(orphans) if orphans else "无"))

print("=" * 66)
print("3) 同一资产的 ?v= 是否唯一（camo 按 URL 缓存，值分裂 = 访客看到新旧混排）")
from collections import defaultdict
d = defaultdict(set)
for m in re.finditer(r'assets/([\w\-.]+)\?v=(\d+)', txt):
    d[m.group(1)].add(m.group(2))
split = 0
for k in sorted(d):
    v = sorted(d[k])
    if len(v) != 1:
        split += 1
        print("   FAIL %-24s %s" % (k, ",".join(v)))
print("   -> 版本号分裂的资产：%d 个" % split)

print("=" * 66)
print("4) 外部图 URL")
ext = sorted(set(re.findall(r'src="(https://[^"]+)"', txt)))
for u in ext:
    print("   %s" % u[:150])

print("=" * 66)
print("结论：%s" % ("全部通过" if (bad == 0 and split == 0 and not orphans) else "有问题，见上面 FAIL"))
sys.exit(0 if (bad == 0 and split == 0 and not orphans) else 1)
