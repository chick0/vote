# vote

QR 코드를 활용해 간단하게 투표를 진행 할 수 있는 프로그램입니다.

## 설치 및 실행
1. 환경변수
    - 이 프로그램은 설정 값을 환경변수에서 가져옵니다.
    - `.env.example` 파일을 복사하고 이름을 `.env` 로 수정합니다.
    - `.env` 파일을 본인의 상황에 맞게 수정합니다.
2. 의존성 설치
    - ```
      pip install -r requirements.txt
      ```
    - 또는 `pip-tools`의 `pip-sync`를 이용해도 됩니다.
3. 데이터베이스
    - ```
      flask db upgrade
      ```
    - 해당 명령어를 통해 데이터베이스에 테이블을 생성합니다.
4. 서버
    - ```
      gunicorn -c gunicorn.py
      ```
    - 해당 명령어를 통해 프로덕션 서버를 실행 할 수 있습니다.
    - `gunicorn`은 윈도우를 지원하지 않습니다.
