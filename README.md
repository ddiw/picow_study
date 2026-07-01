# pico_init

Raspberry Pi Pico SDK(C/C++) 프로젝트 구조를 자동 생성하는 CLI 도구.

## 사용법

\\\
py -m pico_init my_project --board pico2w
\\\

## 지원 보드

- picow / pico_w (Pico W, RP2040)
- pico2w / pico2_w (Pico 2 W, RP2350)

## 구조

- cli.py : 인자 파싱/검증 (정책)
- generator.py : 파일/폴더 생성
- templates.py : 템플릿 문자열
- utils.py : 공통 유틸 함수
