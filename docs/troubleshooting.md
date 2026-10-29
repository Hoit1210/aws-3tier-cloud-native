# 구축 중 해결한 문제

## 1. Docker 컨테이너 외부 접속 실패

Python WAS 컨테이너는 실행 중이었지만 Nginx에서 요청을 전달하면 응답하지 않았습니다.

원인은 Python 서버가 컨테이너 내부의 `127.0.0.1`에서만 요청을 받도록 설정된 것이었습니다. 이를 `0.0.0.0`으로 변경하고 이미지를 다시 빌드한 후 컨테이너를 재배포했습니다. 이후 Docker 포트 포워딩과 Nginx 프록시를 통한 접근이 정상화되었습니다.

## 2. Docker Compose 실행 오류

EC2 환경에서 `docker-compose` 명령 실행 시 아래 오류가 발생했습니다.

```text
KeyError: 'ContainerConfig'
```

구형 Docker Compose와 Docker Engine의 호환성 문제를 확인하고, 기존 Standalone Compose 대신 V2 플러그인을 설치했습니다. 실행 명령도 `docker-compose up`에서 `docker compose up`으로 변경했습니다.

## 3. PostgreSQL 드라이버 문제

Python WAS에서 PostgreSQL 드라이버를 불러오는 과정에 문제가 발생했습니다. 컨테이너에서 추가 빌드 의존성을 줄이기 위해 `psycopg2-binary`를 사용했고, 이미지를 다시 빌드해 RDS 연동을 확인했습니다.

## 실제 검증 기록

[Project 01 포트폴리오](https://app.notion.com/p/3b559c9412258075949de16542d5b774)에 단계별 화면과 해결 과정을 정리했습니다.
