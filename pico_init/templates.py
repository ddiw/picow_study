# -*- coding: utf-8 -*-
"""
templates.py
------------
프로젝트 생성에 쓰이는 파일 템플릿 문자열 모음 + 토큰 치환 함수.

이 모듈은 '잎(leaf) 모듈'이다: 같은 패키지의 다른 모듈을 import 하지 않는다.
(generator 가 이 모듈을 import 하지, 그 반대는 없다.)

  CMake/JSON 의 ${...} 와 파이썬 str.format 충돌을 피하기 위해
  치환 토큰은 __PROJECT__ / __BOARD__ / __SDK_PATH__ 형태로 둔다.
"""


# CMakeLists.txt 템플릿 (Pico SDK 기본 구조)
CMAKELISTS_TEMPLATE = """\
# ===== CMake 최소 버전 =====
cmake_minimum_required(VERSION 3.13)

# ===== C/C++ 표준 설정 =====
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# ===== 대상 보드 설정 =====
# pico_w  : RP2040 기반 Pico W
# pico2_w : RP2350 기반 Pico 2 W (platform/아키텍처는 보드 헤더가 자동 선택)
set(PICO_BOARD __BOARD__ CACHE STRING "Target board type")

# ===== Pico SDK import =====
# project() 보다 반드시 먼저 include 해야 함
include(pico_sdk_import.cmake)

# ===== 프로젝트 선언 =====
project(__PROJECT__ C CXX ASM)

# ===== Pico SDK 초기화 =====
pico_sdk_init()

# ===== 실행 파일 정의 =====
add_executable(__PROJECT__
    src/main.c
)

# ===== include 디렉터리 등록 =====
target_include_directories(__PROJECT__ PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/include
)

# ===== 라이브러리 링크 =====
# 온보드 LED 가 CYW43 무선 칩에 연결되어 있어 cyw43_arch 가 필요함
# (Pico W / Pico 2 W 공통)
target_link_libraries(__PROJECT__
    pico_stdlib
    pico_cyw43_arch_none
)

# ===== 표준 입출력(stdio) 경로 설정 =====
pico_enable_stdio_usb(__PROJECT__ 1)   # USB 시리얼 출력 ON
pico_enable_stdio_uart(__PROJECT__ 0)  # UART 출력 OFF

# ===== 추가 출력 파일 생성 (.uf2, .bin, .hex 등) =====
pico_add_extra_outputs(__PROJECT__)
"""


# src/main.c 템플릿 (온보드 LED Blink 보일러플레이트)
MAIN_C_TEMPLATE = """\
/*
 * __PROJECT__ - 온보드 LED Blink 예제
 *
 * Pico W / Pico 2 W 의 온보드 LED 는 GPIO 가 아니라
 * CYW43 무선 칩에 연결되어 있으므로 cyw43_arch 를 통해 제어한다.
 */

#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

int main(void)
{
    // 표준 입출력 초기화 (USB 시리얼)
    stdio_init_all();

    // CYW43 무선 칩 아키텍처 초기화
    // (온보드 LED 제어를 위해 필수)
    if (cyw43_arch_init()) {
        printf("CYW43 초기화 실패\\n");
        return -1;
    }

    printf("__PROJECT__ 시작: LED Blink\\n");

    while (true) {
        // 온보드 LED 켜기
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(250);

        // 온보드 LED 끄기
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(250);
    }

    return 0;
}
"""


# pico_sdk_import.cmake (Raspberry Pi 공식 표준 파일, BSD-3-Clause)
# SDK 위치를 찾아 pico_sdk_init.cmake 를 include 한다.
#
# [수정 1] 이 템플릿은 "폴백(fallback)" 용도로만 사용된다.
#          실제 SDK(external/pico_sdk_import.cmake)가 있으면 그쪽을 복사하고,
#          못 찾았을 때만 이 내장본을 기록한다.
PICO_SDK_IMPORT_TEMPLATE = """\
# This is a copy of <PICO_SDK_PATH>/external/pico_sdk_import.cmake
# This can be dropped into an external project to help locate this SDK
# It should be include()ed prior to project()

if (DEFINED ENV{PICO_SDK_PATH} AND (NOT PICO_SDK_PATH))
    set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
    message("Using PICO_SDK_PATH from environment ('${PICO_SDK_PATH}')")
endif ()

if (DEFINED ENV{PICO_SDK_FETCH_FROM_GIT} AND (NOT PICO_SDK_FETCH_FROM_GIT))
    set(PICO_SDK_FETCH_FROM_GIT $ENV{PICO_SDK_FETCH_FROM_GIT})
    message("Using PICO_SDK_FETCH_FROM_GIT from environment ('${PICO_SDK_FETCH_FROM_GIT}')")
endif ()

if (DEFINED ENV{PICO_SDK_FETCH_FROM_GIT_PATH} AND (NOT PICO_SDK_FETCH_FROM_GIT_PATH))
    set(PICO_SDK_FETCH_FROM_GIT_PATH $ENV{PICO_SDK_FETCH_FROM_GIT_PATH})
    message("Using PICO_SDK_FETCH_FROM_GIT_PATH from environment ('${PICO_SDK_FETCH_FROM_GIT_PATH}')")
endif ()

set(PICO_SDK_PATH "${PICO_SDK_PATH}" CACHE PATH "Path to the Raspberry Pi Pico SDK")
set(PICO_SDK_FETCH_FROM_GIT "${PICO_SDK_FETCH_FROM_GIT}" CACHE BOOL "set to ON to fetch copy of SDK from git if not otherwise locatable")
set(PICO_SDK_FETCH_FROM_GIT_PATH "${PICO_SDK_FETCH_FROM_GIT_PATH}" CACHE FILEPATH "location to download SDK")

if (NOT PICO_SDK_PATH)
    if (PICO_SDK_FETCH_FROM_GIT)
        include(FetchContent)
        set(FETCHCONTENT_BASE_DIR_SAVE ${FETCHCONTENT_BASE_DIR})
        if (PICO_SDK_FETCH_FROM_GIT_PATH)
            get_filename_component(FETCHCONTENT_BASE_DIR "${PICO_SDK_FETCH_FROM_GIT_PATH}" REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")
        endif ()
        # GIT_SUBMODULES_RECURSE was added in 3.17
        if (${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.17.0")
            FetchContent_Declare(
                    pico_sdk
                    GIT_REPOSITORY https://github.com/raspberrypi/pico-sdk
                    GIT_TAG master
                    GIT_SUBMODULES_RECURSE FALSE
            )
        else ()
            FetchContent_Declare(
                    pico_sdk
                    GIT_REPOSITORY https://github.com/raspberrypi/pico-sdk
                    GIT_TAG master
            )
        endif ()

        if (NOT pico_sdk)
            message("Downloading Raspberry Pi Pico SDK")
            # GIT_SUBMODULES_RECURSE was added in 3.17
            if (${CMAKE_VERSION} VERSION_GREATER_EQUAL "3.17.0")
                FetchContent_MakeAvailable(pico_sdk)
            else ()
                if (NOT pico_sdk_POPULATED)
                    FetchContent_Populate(pico_sdk)
                endif ()
            endif ()
            set(PICO_SDK_PATH ${pico_sdk_SOURCE_DIR})
        endif ()
        set(FETCHCONTENT_BASE_DIR ${FETCHCONTENT_BASE_DIR_SAVE})
    else ()
        message(FATAL_ERROR
                "SDK location was not specified. Please set PICO_SDK_PATH or set PICO_SDK_FETCH_FROM_GIT to on to fetch from git."
                )
    endif ()
endif ()

get_filename_component(PICO_SDK_PATH "${PICO_SDK_PATH}" REALPATH BASE_DIR "${CMAKE_BINARY_DIR}")
if (NOT EXISTS ${PICO_SDK_PATH})
    message(FATAL_ERROR "Directory '${PICO_SDK_PATH}' not found")
endif ()

set(PICO_SDK_INIT_CMAKE_FILE ${PICO_SDK_PATH}/pico_sdk_init.cmake)
if (NOT EXISTS ${PICO_SDK_INIT_CMAKE_FILE})
    message(FATAL_ERROR "Directory '${PICO_SDK_PATH}' does not appear to contain the Raspberry Pi Pico SDK")
endif ()

set(PICO_SDK_PATH ${PICO_SDK_PATH} CACHE PATH "Path to the Raspberry Pi Pico SDK" FORCE)

include(${PICO_SDK_INIT_CMAKE_FILE})
"""


# .vscode/settings.json 템플릿 (VSCode 는 JSONC 라 주석 허용)
VSCODE_SETTINGS_TEMPLATE = """\
{
    // CMake 프로젝트를 열 때 자동 구성
    "cmake.configureOnOpen": true,

    // 빌드 디렉터리 위치 (cmake -B build 와 동일 위치)
    "cmake.buildDirectory": "${workspaceFolder}/build",

    // CMake 구성 시 환경 변수로 Pico SDK 경로 전달
    "cmake.configureEnvironment": {
        "PICO_SDK_PATH": "__SDK_PATH__"
    },

    // IntelliSense 가 CMake Tools 정보를 사용하도록 지정
    "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",

    // 파일 확장자 연결
    "files.associations": {
        "*.h": "c",
        "*.c": "c",
        "*.cmake": "cmake",
        "pico_sdk_import.cmake": "cmake"
    }
}
"""


# .gitignore 템플릿 (빌드 산출물 제외 - 편의용 보너스)
# [수정 3] 폴더 자체는 만들지 않지만, 추후 cmake -B build 로 생성되는
#          build/ 산출물은 git 에서 제외되도록 항목은 그대로 유지한다.
GITIGNORE_TEMPLATE = """\
# 빌드 산출물
/build/
*.uf2
*.elf
*.bin
*.hex
*.map

# 에디터 캐시
.cache/
"""


def render(template: str, project: str, board: str, sdk_path: str) -> str:
    """템플릿의 치환 토큰을 실제 값으로 바꿔서 반환.

    토큰 규칙(__PROJECT__/__BOARD__/__SDK_PATH__)은 위 템플릿들과 짝을 이루는
    '계약'이므로, 이 함수는 utils 가 아니라 templates 에 둔다.
    """
    return (
        template
        .replace("__PROJECT__", project)
        .replace("__BOARD__", board)
        .replace("__SDK_PATH__", sdk_path)
    )
