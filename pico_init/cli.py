# -*- coding: utf-8 -*-
"""
cli.py
------
명령행 인터페이스 = '정책(policy)' 계층.
무엇을 할지 결정(인자 해석/검증/종료코드)하고, 결정된 실행은 generator 에 맡긴다.

의존성 방향(위 -> 아래):
    cli  ->  generator (create_project)
generator 는 cli 를 절대 import 하지 않는다(순환 금지).

여기에 두는 것들과 그 근거:
  - BOARD_MAP            : 보드 별칭->정식명 매핑(정책). STAGE 12 에서 외부화 예정.
  - resolve_sdk_path     : --sdk-path 와 환경변수의 '우선순위 결정' = 정책.
  - --force 폴더 삭제 블록 : 사용자 의도 해석 + 종료코드 처리 = 정책.
  - print_next_steps     : 사용자 안내(UX) = 정책.
"""

import argparse
import os
import shutil  # [수정 2] 폴더 삭제(rmtree)에 사용
from pathlib import Path

from .generator import create_project


# ---------------------------------------------------------------------------
# 보드 별칭 -> Pico SDK 의 PICO_BOARD 값 매핑
#   사용자가 어떻게 입력하든(picow/pico_w, pico2w/pico2_w) 정규화해서 처리
# ---------------------------------------------------------------------------
BOARD_MAP = {
    "picow": "pico_w",
    "pico_w": "pico_w",
    "pico2w": "pico2_w",
    "pico2_w": "pico2_w",
}


def resolve_sdk_path(arg_sdk_path: str) -> str:
    """
    settings.json 에 넣을 PICO_SDK_PATH 결정.
    우선순위: --sdk-path 인자 > 환경변수 PICO_SDK_PATH > 안내용 플레이스홀더
    경로는 Windows 에서도 안전하도록 forward slash 로 통일.
    """
    raw = arg_sdk_path or os.environ.get("PICO_SDK_PATH", "")
    if not raw:
        # 못 찾으면 사용자에게 직접 채우라고 안내
        print("[경고] PICO_SDK_PATH 를 찾지 못했습니다. "
              ".vscode/settings.json 의 경로를 직접 수정하세요.")
        raw = "/path/to/pico-sdk"
    # 백슬래시 -> 슬래시 (CMake/JSON 모두 슬래시를 허용)
    return raw.replace("\\", "/")


def print_next_steps(project: str, board: str) -> None:
    """생성 후 다음 단계 안내."""
    print("\n========================================")
    print(" 생성 완료! 다음 단계:")
    print("========================================")
    # [수정 4] 빌드 안내를 cmake -B build 방식으로 변경.
    #          (build/ 로 cd 하지 않고, 프로젝트 루트에서 바로 구성/빌드)
    print(f"  cd {project}")
    print("  cmake -B build -G Ninja      # build/ 를 구성 (-G Ninja 는 생략 가능)")
    print("  cmake --build build          # 빌드 실행 (Ninja/Make 자동)")
    print("\n  빌드 후 build/ 안의 .uf2 파일을 보드에 드래그하여 업로드하세요.")
    if board == "pico2_w":
        print("\n  [참고] Pico 2 W(pico2_w) 는 Pico SDK 2.1.0 이상 + RP2350 툴체인이 필요합니다.")
    print("========================================\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="pico_init",
        description="Raspberry Pi Pico SDK(C/C++) 프로젝트 구조 자동 생성 도구",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "project",
        help="생성할 프로젝트 이름 (폴더명으로 사용)",
    )
    # [수정 5] --board 는 argparse 의 choices 를 쓰지 않는다.
    #          choices 를 쓰면 영어 에러가 자동 출력되고 대소문자도 막히므로,
    #          여기서는 자유 입력으로 받은 뒤 아래에서 직접 검증한다(대소문자 허용).
    parser.add_argument(
        "--board",
        default="picow",
        help="대상 보드 선택 (기본값: picow / 대소문자 무관)\n"
             "  picow / pico_w   -> Pico W (RP2040)\n"
             "  pico2w / pico2_w -> Pico 2 W (RP2350)",
    )
    parser.add_argument(
        "--sdk-path",
        default="",
        help="Pico SDK 경로 직접 지정 (미지정 시 환경변수 PICO_SDK_PATH 사용)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="대상 폴더가 이미 있으면 통째로 삭제 후 재생성",
    )

    args = parser.parse_args()

    # [수정 5] 대소문자 허용: 입력을 소문자로 정규화한 뒤 매핑 키와 비교.
    board_key = args.board.lower()

    # [수정 6] 잘못된 보드명일 때 한글 에러 메시지 출력.
    if board_key not in BOARD_MAP:
        print(f"[오류] 지원하지 않는 보드입니다 : {args.board}")
        print(f"       사용 가능한 보드: {', '.join(sorted(BOARD_MAP))}")
        return 1

    # 보드 별칭 정규화 (picow -> pico_w, pico2w -> pico2_w)
    pico_board = BOARD_MAP[board_key]

    # 프로젝트명 간단 검증 (경로 구분자 포함 금지)
    if os.sep in args.project or (os.altsep and os.altsep in args.project):
        print(f"[오류] 프로젝트 이름에 경로 구분자를 포함할 수 없습니다: {args.project}")
        return 1

    # 기존 폴더 충돌 처리
    root = Path(args.project)
    if root.exists():
        if args.force:
            # [수정 2] --force: 기존 폴더(또는 파일)를 통째로 삭제 후 재생성.
            #          rmtree 로 내부 산출물까지 깔끔하게 비운 뒤 새로 만든다.
            try:
                if root.is_dir() and not root.is_symlink():
                    shutil.rmtree(root)
                else:
                    # 동일 이름의 파일/심볼릭 링크인 경우
                    root.unlink()
                print(f"[완료] 기존 항목 삭제(--force): {root.resolve()}")
            except OSError as e:
                print(f"[오류] 기존 항목 삭제에 실패했습니다: {e}")
                return 1
        elif root.is_dir() and any(root.iterdir()):
            print(f"[오류] '{root}' 폴더가 이미 존재하며 비어있지 않습니다.")
            print("       덮어쓰려면 --force 옵션을 사용하세요.")
            return 1
        # 위 두 경우가 아니면(빈 폴더 등) 그대로 진행 (mkdir exist_ok=True)

    # SDK 경로 결정
    sdk_path = resolve_sdk_path(args.sdk_path)

    # 생성 실행
    try:
        create_project(args.project, pico_board, sdk_path)
    except OSError as e:
        print(f"[오류] 파일/폴더 생성 중 문제가 발생했습니다: {e}")
        return 1

    print_next_steps(args.project, pico_board)
    return 0
