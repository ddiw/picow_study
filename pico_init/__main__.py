#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__main__.py
-----------
패키지 진입점.  `python -m pico_init ...` 로 실행될 때 이 파일이 돈다.

[기준 D] sys.stdout.reconfigure 같은 '전역 부작용'은 import 시점이 아니라
진입 시점에 딱 한 번만 일어나야 한다. 그래서 이 코드를 임포트되는 모듈
(cli/utils 등)이 아니라 진입점인 여기 최상단에 둔다.
"""

import sys

# ---------------------------------------------------------------------------
# Windows 콘솔(cp949 등)에서도 한글/특수문자가 깨지지 않도록 UTF-8 재설정 시도
# (Python 3.7+ 에서만 reconfigure 사용 가능, 실패해도 무시)
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
