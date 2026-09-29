# -*- coding: utf-8 -*-
"""README 里所有外部图 URL 的可达性检查。

为什么用 urllib 而不是 subprocess curl
------------------------------------
URL 里全是 & (shields.io 的查询参数)。在 PowerShell 里把带 & 的 URL
传给 curl.exe 会被拆成多个参数，表现为"只回了 100 来字节"，
排查时极易误判成服务端故障。urllib 直接在进程内发请求，没有这层坑。
"""
import io
import os
import re
import ssl
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
txt = io.open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()

urls = sorted(set(re.findall(r'src="(https://[^"]+)"', txt)))
# badge 里有中文，urllib 不接受未编码的非 ASCII，补一下
from urllib.parse import quote
urls = [quote(u, safe=":/?&=%+#") for u in urls]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
bad = []
for u in urls:
    host = re.match(r"https://([^/]+)", u).group(1)
    try:
        req = urllib.request.Request(u, headers=UA)
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            body = r.read()
        # shields.io / skillicons 对无效参数会返回 200，所以还要看体积
        size = len(body)
        tiny = size < 300
        ok = (r.status == 200) and not tiny
        print("  %-4s %-30s %s  %d bytes%s"
              % ("OK" if ok else "FAIL", host, r.status, size,
                 "  <-- 体积过小，疑似空图" if tiny else ""))
        if not ok:
            bad.append(u)
    except Exception as e:
        print("  FAIL %-30s %s" % (host, type(e).__name__ + ": " + str(e)[:70]))
        bad.append(u)

print("-" * 66)
print("外部图 %d 个，可用 %d 个，异常 %d 个" % (len(urls), len(urls) - len(bad), len(bad)))
sys.exit(0 if not bad else 1)
