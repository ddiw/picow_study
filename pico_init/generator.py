# -*- coding: utf-8 -*-
"""
generator.py
------------
프로젝트 폴더/파일을 실제로 만들어내는 '기계(mechanism)' 계층.

의존성 방향(위 -> 아래):
    generator  ->  templates (치환 토큰/템플릿 문자열)
    generator  ->  utils     (make_dir / write_file)
templates 와 utils 는 generator 를 절대 import 하지 않는다(순환 금지).
"""

import shutil  # [수정 1] SDK 파일 복사에 사용
from pathlib import Path

from .templates import (
    CMAKELISTS_TEMPLATE,
    GITIGNORE_TEMPLATE,
    MAIN_C_TEMPLATE,
    PICO_SDK_IMPORT_TEMPLATE,
    VSCODE_SETTINGS_TEMPLATE,
    render,
)
from .utils import make_dir, write_file


# [수정 1] pico_sdk_import.cmake 를 "실제 SDK 에서 복사" 하고, 실패 시 폴백.
def write_pico_sdk_import(dest: Path, sdk_path: str) -> None:
    """
    pico_sdk_import.cmake 를 생성한다.

    우선순위:
      1) <PICO_SDK_PATH>/external/pico_sdk_import.cmake 가 존재하면 그대로 복사
         (SDK 버전과 항상 일치하므로 가장 안전한 방식)
      2) 복사가 불가능하면(경로 없음/플레이스홀더/권한 오류 등) 내장 템플릿 기록

    이 함수는 SDK 내부 폴더 구조(external/...)를 '아는' 도메인 로직이므로
    범용 utils 가 아니라 generator 에 둔다.
    """
    # resolve_sdk_path 가 슬래시로 정규화한 경로지만, pathlib 는 슬래시를
    # 모든 OS 에서 그대로 받아주므로 그대로 사용해도 무방하다.
    src = Path(sdk_path) / "external" / "pico_sdk_import.cmake"

    if src.is_file():
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            print(f"[완료] SDK에서 복사: {dest}")
            print(f"        (원본: {src})")
            return
        except OSError as e:
            print(f"[경고] SDK 복사 실패({e}). 내장 템플릿으로 대체합니다.")
    else:
        print("[경고] 실제 SDK의 external/pico_sdk_import.cmake 를 찾지 못했습니다. "
              "내장 템플릿을 사용합니다.")

    # 폴백: 패키징된 표준 템플릿 기록
    write_file(dest, PICO_SDK_IMPORT_TEMPLATE)


def create_project(project: str, board: str, sdk_path: str) -> None:
    """프로젝트 폴더와 모든 파일을 생성."""
    root = Path(project).resolve()

    print(f"\n프로젝트 생성 시작: {root}")
    print(f"  - 보드(PICO_BOARD): {board}")
    print(f"  - SDK 경로        : {sdk_path}\n")

    # 1) 폴더 구조 생성
    make_dir(root)
    make_dir(root / "src")
    make_dir(root / "include")
    # [수정 3] build/ 폴더는 생성하지 않는다.
    #          cmake -B build 가 구성 시점에 자동으로 만들어 주므로 불필요.
    make_dir(root / ".vscode")

    # 2) CMakeLists.txt
    write_file(root / "CMakeLists.txt",
               render(CMAKELISTS_TEMPLATE, project, board, sdk_path))

    # 3) src/main.c (LED blink)
    write_file(root / "src" / "main.c",
               render(MAIN_C_TEMPLATE, project, board, sdk_path))

    # 4) pico_sdk_import.cmake
    # [수정 1] 단순 write_file 대신, SDK 복사 우선 + 실패 시 폴백 함수 사용.
    write_pico_sdk_import(root / "pico_sdk_import.cmake", sdk_path)

    # 5) .vscode/settings.json (SDK 경로 포함)
    write_file(root / ".vscode" / "settings.json",
               render(VSCODE_SETTINGS_TEMPLATE, project, board, sdk_path))

    # (보너스) .gitignore
    write_file(root / ".gitignore",
               render(GITIGNORE_TEMPLATE, project, board, sdk_path))
