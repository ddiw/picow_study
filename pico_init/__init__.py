# -*- coding: utf-8 -*-
"""
pico_init
---------
Raspberry Pi Pico SDK(C/C++) 프로젝트 구조 자동 생성 CLI 도구.

모듈 구성(의존성 방향: 위 -> 아래):
    __main__  ->  cli  ->  generator  ->  templates
                   └------------------->  utils  <--- generator

  - __main__.py  : 진입점 (UTF-8 설정 + main 호출)
  - cli.py       : 정책(인자 파싱/검증/--force/안내)
  - generator.py : 생성 오케스트레이션 + SDK 복사
  - templates.py : 템플릿 문자열 + render (잎)
  - utils.py     : 범용 파일시스템 함수 (잎)

실행: python -m pico_init my_project --board pico2w
"""

__version__ = "0.1.0"
