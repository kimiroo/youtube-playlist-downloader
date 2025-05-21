@echo off

rem Activate venv
call "%~dp0.venv\Scripts\activate.bat"

rem 【양아지 다시보기】 블루 아카이브 시간순 정렬
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLzuuMcIDefmBzPlSewvroJ7POtLfZySrW -n "양아지 블아 시간순"

rem 양아지 블루아카이브 메인스토리 모음
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLleWExaRXKzy5AYwaoHE_QiLxwS9AIQHY -n "양아지 블아 메인스토리"

rem 양아지 블루아카 이벤트
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLsHXcRZN-OyHipJJ_hTNsOkJtoZFCBsov -n "양아지 블아 이벤트"

rem 【 블루아카이브 】 (러끼) (reverse)
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLCjUIFHSKVGZT4KzaCPw3BiL28hMduazA -n "러끼 블루 아카이브" -r

rem [블루아카이브] 스토리 함께 보기 (긴실장)
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLWc5YBbIq2o9NgBHpc4vcM1L6h-kmkf3O -n "긴실장 블루 아카이브"

rem 긴실장 정규(?) 저스트 채팅 (긴실장)
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLdZSd0cK0j-AHn2raOne4A8gKm6kfvmr5 -n "긴실장 저스트 채팅"

rem 김실장 정규(?) 저스트 채팅 (김실장)
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLdZSd0cK0j-AZHluxSGH0gHrrZfG8cIwe -n "긴실장 저스트 채팅"

rem 김실장과 PD의 협동 게임 모음 (긴실장)
python "%~dp0main.py" https://www.youtube.com/playlist?list=PLWc5YBbIq2o8aZo2T__TVFvzaEYWme4Nr -n "긴실장 협동 게임 모음"

rem Deactivate venv
call "%~dp0.venv\Scripts\deactivate.bat"