# -*- coding: utf-8 -*-
"""
utils.py
--------
도메인(보드/SDK/템플릿)을 전혀 모르는 범용 파일시스템 함수 모음.

이 모듈은 '잎(leaf) 모듈'이다: 같은 패키지의 다른 모듈을 import 하지 않는다.
여기에는 '경로와 내용만 받아 처리하는' 함수만 둔다. 우리 프로젝트 고유 지식
(SDK 폴더 구조, 보드 매핑 등)이 들어오면 그건 utils 가 아니라 generator/cli 로
가야 한다. 그래야 utils 가 '잡동사니 서랍'이 되지 않는다.
"""

from pathlib import Path


def make_dir(path: Path) -> None:
    """디렉터리 생성 후 완료 메시지 출력 (cross-platform)."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"[완료] 폴더 생성: {path}")


def write_file(path: Path, content: str) -> None:
    """파일 생성 후 완료 메시지 출력. 항상 UTF-8 / LF 로 기록."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" 으로 고정하여 OS 와 무관하게 LF 사용 (Pico 빌드 환경 친화)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[완료] 파일 생성: {path}")
