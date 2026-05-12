import os
from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv

load_dotenv() # .env 파일의 내용을 읽어옴.

app = Flask(__name__)

# 1. 접속 정보
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://nuzyippznvhwbfzftfhd.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51enlpcHB6bnZod2JmemZ0ZmhkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0Mzc5MDksImV4cCI6MjA5NDAxMzkwOX0.icNRPSCOLswwUj9GlQNZovSukNI-iMtFa1ZbbrFk4jE")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def admin_input():
    # 등록된 업체 목록을 가져와서 입력 표를 만듭니다.
    companies = supabase.table("companies").select("*").execute().data
    return render_template('index.html', companies=companies)

@app.route('/calculate', methods=['POST'])
def calculate():
    # 1. 폼 데이터 수집 (고지서 및 사용량)
    mmyy = request.form['mmyy']
    total_elec = int(request.form['total_elec'])
    total_water = int(request.form['total_water'])
    
    # 업체별 사용량 및 계산 로직 (앞서 만든 로직 활용)
    # ... 계산 후 monthly_company_fees에 저장 ...
    
    return "계산 및 저장 완료!"

@app.route('/view/<company_id>/<mmyy>')
def view_bill(company_id, mmyy):
    # 1. 당월 데이터 가져오기
    current_bill = supabase.table("monthly_company_fees")\
        .select("*").eq("company_id", company_id).eq("mmyy", mmyy).single().execute().data
    
    # 2. 직전 월 데이터 가져오기 (비교용)
    # mmyy가 '2405'라면 '2404'를 구하는 로직 필요
    prev_mmyy = str(int(mmyy)-1) # 단순 예시
    prev_bill = supabase.table("monthly_company_fees")\
        .select("*").eq("company_id", company_id).eq("mmyy", prev_mmyy).maybe_single().execute().data

    return render_template('bill.html', current=current_bill, prev=prev_bill)

def get_comparison(company_id, current_mmyy):
    # 1. 이번 달 데이터
    curr = supabase.table("monthly_company_fees")\
        .select("*").eq("company_id", company_id).eq("mmyy", current_mmyy).single().execute().data
    
    # 2. 지난달 데이터 (년월 계산 로직 필요)
    # 간단하게 mmyy를 숫자로 바꿔 -1을 하는 방식 혹은 날짜 라이브러리 사용
    prev_mmyy = str(int(current_mmyy) - 1) 
    prev = supabase.table("monthly_company_fees")\
        .select("*").eq("company_id", company_id).eq("mmyy", prev_mmyy).maybe_single().execute().data
    
    return curr, prev

# --- [페이지: 로그인 화면] ---
@app.route('/login')
def login_page():
    return render_template('login.html')

# --- [로직: 비밀번호 확인 및 조회] ---
@app.route('/view-bill', methods=['POST'])
def submit_view_bill():
    biz_last = request.form['biz_last']  # 사용자가 입력한 5자리
    mmyy = request.form['mmyy']
    
    try:
        # 1. 모든 업체 정보를 가져와서 사업자번호 뒷자리가 일치하는지 찾습니다.
        # (보안을 위해 실제 운영시는 더 정교한 쿼리가 좋지만, 일단 쉽게 구현합니다)
        companies = supabase.table("companies").select("*").execute().data
        
        target_company = None
        for comp in companies:
            # DB의 사업자번호(예: 123-45-67890)에서 하이픈 제거 후 끝 5자리 추출
            clean_biz = comp['biz_number'].replace('-', '')
            if clean_biz.endswith(biz_last):
                target_company = comp
                break
        
        if not target_company:
            return render_template('login.html', error="일치하는 업체 정보가 없습니다.")

        # 2. 일치하는 업체가 있다면 해당 월의 관리비 데이터를 가져옵니다.
        c_id = target_company['company_id']
        current_bill = supabase.table("monthly_company_fees")\
            .select("*").eq("company_id", c_id).eq("mmyy", mmyy).maybe_single().execute().data
            
        if not current_bill:
            return render_template('login.html', error=f"{mmyy}월 정산 데이터가 아직 없습니다.")

        # 3. 전월 대비 비교를 위해 지난달 데이터도 가져옵/니다.
        # (지난달 YYMM 구하기: 간단히 숫자로 변환해 -1)
        prev_mmyy = str(int(mmyy) - 1)
        prev_bill = supabase.table("monthly_company_fees")\
            .select("*").eq("company_id", c_id).eq("mmyy", prev_mmyy).maybe_single().execute().data

        # 4. 최종적으로 bill.html에 데이터를 뿌려줍니다.
        return render_template('bill.html', company=target_company, current=current_bill, prev=prev_bill)

    except Exception as e:
        return f"조회 중 오류 발생: {e}"

if __name__ == '__main__':
    # Render는 PORT 환경변수를 사용합니다.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)