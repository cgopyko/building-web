import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, flash
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = "secret_key_for_flash_messages"

# Supabase 설정
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 관리할 테이블 목록
TABLES = ['companies', 'long_term_costs', 'elec_costs', 'etc_costs']

@app.route('/')
def index():
    # 각 테이블의 최근 데이터를 가져와서 메인 페이지에 표시
    data = {}
    for table in TABLES:
        response = supabase.table(table).select("*").limit(5).execute()
        data[table] = response.data
    return render_template('index.html', tables=TABLES, data=data)

@app.route('/upload/<table_name>', methods=['POST'])
def upload_file(table_name):
    if table_name not in TABLES:
        return "유효하지 않은 테이블입니다.", 400
    
    file = request.files.get('file')
    if not file or file.filename == '':
        flash("파일을 선택해주세요.")
        return redirect(url_for('index'))

    try:
        # 1. 2행부터 읽기 (skiprows=1)
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file, sep=r'\s*,\s*', skiprows=1, engine='python')
        else:
            df = pd.read_excel(file, sep=r'\s*,\s*', skiprows=1, engine='python')

        # 2. 앞뒤 공백 제거 (Trim) 및 결측치 처리
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df = df.where(pd.notnull(df), None)
        df = df.fillna("")

        # 3. Supabase 업로드
        data_dicts = df.to_dict(orient='records')
        supabase.table(table_name).insert(data_dicts).execute()
        
        flash(f"{table_name} 테이블 업로드 완료!")
    except Exception as e:
        flash(f"오류 발생: {str(e)}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)