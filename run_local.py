from waitress import serve
from app import app # app.py 파일 내 Flask 인스턴스 이름

if __name__ == '__main__':
    print("로컬 서버가 http://localhost:8080 에서 실행 중입니다.")
    serve(app, host='0.0.0.0', port=8080)