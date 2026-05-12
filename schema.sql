-- 1. 입주 업체 정보 테이블
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL, -- 상호명
    biz_number VARCHAR(20) NOT NULL,    -- 사업자등록번호
    ceo_name VARCHAR(50),               -- 대표자 이름
    phone VARCHAR(14),                  -- 연락처
    deposit BIGINT DEFAULT 0,           -- 보증금
    monthly_rent BIGINT DEFAULT 0,      -- 월세금
    contract_start DATE,                -- 계약 시작일
    contract_end DATE,                  -- 계약 종료일

    manage_fee_rate NUMERIC(5, 4),      -- 공동 관리비 분배 비율
    water_fee_rate NUMERIC(5, 4),       -- 공용 수도료 분배 비율
    memo TEXT                           -- 메모
);

-- 2. 월별 공용 비용 테이블 (건물 전체 고지서용)
CREATE TABLE common_costs (
    cost_id SERIAL PRIMARY KEY,
    mmyy VARCHAR(7) NOT NULL,           -- 정산년월

    total_elec_fee BIGINT DEFAULT 0,    -- 공용 전기료 총액
    total_water_fee BIGINT DEFAULT 0,   -- 공용 수도료 총액
    total_manage_fee BIGINT DEFAULT 0,  -- 공용 관리비 총액
    UNIQUE(mmyy)
);

-- 3. 업체별 월간 부담액 테이블 (최종 계산 결과 저장용)
CREATE TABLE monthly_company_fees(
    fee_id SERIAL PRIMARY KEY,
    mmyy VARCHAR(7) NOT NULL,           -- 년월
    
    company_id INTEGER REFERENCES Companies(company_id), -- 업체 코드
    elec_fee BIGINT,                    -- 전기료 분담액
    water_fee BIGINT,                   -- 수도료 분담액
    manage_fee BIGINT,                  -- 관리비 분담액
    total_fee BIGINT                    -- 총 분담액
);

-- 4. 장기 고정 비용 세부 내역
-- 매달 지불: 인건비, 전기/소방/승강기 안전 관리
-- 년 1회 지불: 정화조 청소, 소방 설비 점검 등 1/12 안분
-- 년 1회 지불되는 비용은 입력하면서 안분되어 저장
CREATE TABLE long_term_costs (
    cost_id SERIAL PRIMARY KEY,
    mmyy_start VARCHAR(7) NOT NULL,     -- 시작 년월
    mmyy_end VARCHAR(7),                -- 종료 년월(NULL이면 계속)

    cost_title VARCHAR(100) NOT NULL,   -- 항목명
    monthly_cost BIGINT DEFAULT 0       -- 월 지불액
);

-- 5. 월별 기타 비용 내역
CREATE TABLE etc_costs (
    cost_id SERIAL PRIMARY KEY,
    mmyy VARCHAR(7) NOT NULL,           -- 년월

    cost_title VARCHAR(100) NOT NULL,   -- 항목명
    other_cost BIGINT DEFAULT 0         -- 지불액
);

-- 6. 업체별 전기 사용량과 분배 비율
CREATE TABLE elec_costs (
    cost_id SERIAL PRIMARY KEY,
    mmyy VARCHAR(7) NOT NULL,           -- 년월

    company_id INTEGER REFERENCES Companies(company_id), -- 업체 코드
    elec_usage BIGINT DEFAULT 0,        -- 전기사용량 
    elec_fee_rate NUMERIC(5,4)          -- 전기료 분배 비율
);