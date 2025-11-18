import streamlit as st
import pandas as pd
import itertools
import random
from collections import Counter
import re
import json
import os
import datetime

# ===========================================================
# 1. 기본 설정 (무조건 맨 위에 있어야 함)
# ===========================================================
st.set_page_config(page_title="독서모임 운영 시스템", page_icon="📚", layout="wide")

DB_FILE = "meeting_db.json"

NAME_MAP = {
    "혜은": "담이", "노쥬": "노주", "지민": "이지민", "지민(한)": "한지민",
    "정석영": "석영", "윤승현": "승현", "정일근": "일근"
}

def clean_name(name):
    name = re.sub(r'\([^)]*\)', '', name).strip()
    return NAME_MAP.get(name, name)

# 초기 데이터 (1회~26회)
DEFAULT_DATA = [
    {"round": 1, "date": "23.10", "groups": [["혜은", "정은", "임구", "재성", "소희", "기창", "채니", "임정", "승현"]]},
    {"round": 2, "date": "23.11", "groups": [["채니", "사랑", "은하", "기창", "승현"]]},
    {"round": 3, "date": "23.12", "groups": [["석영", "기창", "승현", "일근", "정은", "채니", "사랑"]]},
    {"round": 4, "date": "24.01", "groups": [["석영", "태환", "기창", "은하", "소담", "승현", "원빈", "은천", "일근", "임정", "정은", "채니"]]},
    {"round": 5, "date": "24.02", "groups": [["석영", "태환", "기창", "무근", "정은", "혜은", "채니"]]},
    {"round": 6, "date": "24.03", "groups": [["석영", "태환", "은하", "선희", "원빈", "영모", "승현", "일근", "사랑", "미주", "은천"]]},
    {"round": 7, "date": "24.04", "groups": [["석영", "태환", "영건", "사랑", "진아", "정은"], ["승현", "임정", "채니", "무근"], ["일근", "영모", "은하", "하늘", "문형", "소담"]]},
    {"round": 8, "date": "24.05", "groups": [["기창", "태환", "수빈", "은하", "정은"], ["채니", "승현", "선희", "사랑", "석영"]]},
    {"round": 9, "date": "24.06", "groups": [["기창", "선희", "사랑", "문형", "성운", "수민"], ["정은", "석영", "영모", "수빈", "무근", "도아"], ["채니", "태환", "혜은", "은하", "은천"]]},
    {"round": 10, "date": "24.07", "groups": [["기창", "아론", "성은", "은하", "사랑", "진아"], ["정은", "채아", "문형", "수빈", "태환", "수민"], ["채니", "석영", "노주", "무근", "혜은", "은천"]]},
    {"round": 11, "date": "24.08", "groups": [["기창", "준오", "수빈", "민선", "동근", "진아", "선희"], ["영모", "노쥬", "수민", "아론", "석영", "채아"]]},
    {"round": 12, "date": "24.09", "groups": [["태환", "석영", "준오", "은하", "채니", "성은"], ["기창", "광현", "노주", "민선", "동근", "혜은", "영모"], ["무근", "아론", "채아", "수민", "승현", "정은"]]},
    {"round": 13, "date": "24.10", "groups": [["기창", "호형", "태환", "혜은", "선희", "은하", "성은"], ["무근", "세엘", "석영", "민선", "하영"], ["채니", "문형", "영모", "채아", "수민"], ["정은", "광현", "동근", "승현", "수빈", "노주"]]},
    {"round": 14, "date": "24.11", "groups": [["채니", "채아", "진아", "은천", "동근", "임구", "아론"], ["기창", "성은", "킴킴", "지완", "건호", "현영", "레이나", "도희", "지연"], ["영모", "태환", "미주", "민선", "호형", "원빈", "광현"], ["혜은", "무근", "은하", "문형", "준오", "대곤", "석영"]]},
    {"round": 15, "date": "24.12", "groups": [["태환", "수민", "은천", "노쥬", "성은", "미주"], ["무근", "미주", "대곤", "킴킴", "동근", "채아"], ["기창", "정은", "태선", "서희", "태리", "민규", "석영"], ["채니", "혜은", "은하", "호형", "지완", "준오", "도희"]]},
    {"round": 16, "date": "25.01", "groups": [["기창", "태선", "문형", "하영", "선희", "노주", "석영"], ["무근", "호형", "아론", "성은", "태리", "도희"], ["채니", "승현", "광현", "건호", "지연", "은하"], ["정은", "은천", "민규", "준오", "민선", "수빈", "담이"]]},
    {"round": 17, "date": "25.02", "groups": [["태환", "기창", "준오", "대곤", "은하", "채니"], ["영모", "석영", "민규", "광현", "태리", "담이"], ["무근", "건호", "아론", "은천", "선희", "민선"]]},
    {"round": 18, "date": "25.03", "groups": [["태환", "준오", "광현", "담희", "노쥬", "태리"], ["채니", "아론", "기창", "석영", "은하", "민선", "선희"], ["담이", "대곤", "건호", "호형", "지민", "채아"]]},
    {"round": 19, "date": "25.04", "groups": [["아론", "무근", "성은", "킴킴", "도희"], ["준오", "채니", "석영", "담희", "태리"], ["민선", "태환", "채아", "광현", "지민"], ["담이", "건호", "기창", "동근", "노주"]]},
    {"round": 20, "date": "25.05", "groups": [["기창", "태리", "동욱", "지연", "채니", "김민", "정연"], ["태환", "승현", "호형", "수민", "노쥬", "규찬", "민승2"], ["무근", "석영", "태선", "성은", "채아", "은하", "은천"], ["담이", "준오", "광현", "킴킴", "선희", "민승", "담희"]]},
    {"round": 21, "date": "25.06", "groups": [["채니", "규찬", "아론", "영모", "태선", "민선", "노주"], ["담이", "승현", "찬수", "동근", "준오", "성은", "채아"], ["태환", "건호", "기창", "호형", "동근", "태리", "지민"], ["무근", "세엘", "문형", "광현", "하늘", "수민", "킴킴"]]},
    {"round": 22, "date": "25.07", "groups": [["수민", "민선", "광현", "준오", "이지민", "태리"], ["담이", "성은", "기창", "태선", "영환", "한지민"], ["채니", "노주", "하리", "규찬", "동욱", "민승", "대곤"], ["은하", "선희", "담희", "건호", "무근", "찬수", "윤상"]]},
    {"round": 23, "date": "25.08", "groups": [["담이", "기창", "동욱", "찬수", "채아"], ["채니", "은천", "동근", "민승", "수민"], ["무근", "태선", "하리", "석영"], ["태환", "주영", "영모", "민선", "규찬"], ["건호", "태리", "담희"]]},
    {"round": 24, "date": "25.09", "groups": [["태환", "규찬", "동욱", "지민(한)", "민선"], ["채니", "승현", "태선", "준오", "은하", "채아"], ["기창", "대곤", "찬수", "광현", "노주", "담희"], ["무근", "건호", "석영", "윤서", "태리", "하리"]]},
    {"round": 25, "date": "25.10", "groups": [["채니", "영모", "동근", "담희", "수민", "광현"], ["담이", "태선", "재원", "채아", "민선", "석영"], ["태환", "호형", "아론", "민승", "은하", "태리"], ["기창", "동욱", "무근", "윤서", "노쥬", "승현"]]},
    {"round": 26, "date": "25.11", "groups": [["규찬", "대곤", "채아", "선희", "기창"], ["채니", "노주", "동근", "은하", "은천"], ["담이", "민승", "찬수", "성은", "하리"], ["수민", "무근", "윤서", "민선", "준오", "석영"]]},
]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@st.cache_data
def analyze_overlap(data_list):
    counter = Counter()
    all_people = set()
    
    for record in data_list:
        for group in record["groups"]:
            cleaned_group = [clean_name(m) for m in group if clean_name(m)]
            cleaned_group = list(set(cleaned_group))
            all_people.update(cleaned_group)
            for m1, m2 in itertools.combinations(cleaned_group, 2):
                pair = tuple(sorted([m1, m2]))
                counter[pair] += 1
    return counter, sorted(list(all_people))

# 데이터 로드
db_data = load_data()
overlap_counts, all_members = analyze_overlap(db_data)

# ===========================================================
# 2. UI 구현
# ===========================================================
st.title("📚 독서모임 운영 시스템")

# 세션 상태 초기화 (이 부분이 중요합니다!)
if 'generated_teams' not in st.session_state:
    st.session_state.generated_teams = None

tab1, tab2, tab3 = st.tabs(["🛠️ 조 편성", "📝 히스토리 관리", "📊 만남 분석"])

# -----------------------------------------------------------
# [탭 1] 조 편성 (Fix: session_state 사용)
# -----------------------------------------------------------
with tab1:
    st.header("새로운 조 만들기")
    col1, col2 = st.columns([1, 2])
    with col1:
        input_type = st.radio("명단 입력 방식", ["직접 입력", "전체 명단에서 선택"], horizontal=True)
        current_attendees = []
        if input_type == "직접 입력":
            raw = st.text_area("참석자 (콤마/엔터로 구분)", height=150, placeholder="기창, 채니, 무근...")
            if raw:
                current_attendees = [n.strip() for n in re.split(r'[,\n\t]+', raw) if n.strip()]
        else:
            current_attendees = st.multiselect("참석자 선택", all_members)
        
        st.info(f"참석: **{len(current_attendees)}명**")
        current_leaders = []
        if current_attendees:
            current_leaders = st.multiselect("조장 선택", current_attendees)
        
        run_btn = st.button("🚀 조 편성 실행", type="primary")

    with col2:
        # 실행 버튼을 누르면 조를 짜서 '세션'에 저장
        if run_btn:
            if not current_leaders:
                st.error("조장을 선택해주세요.")
            elif len(current_leaders) > len(current_attendees):
                st.error("조장이 참석자보다 많습니다.")
            else:
                # --- 알고리즘 실행 ---
                teams = {leader: [leader] for leader in current_leaders}
                pool = [p for p in current_attendees if clean_name(p) not in [clean_name(l) for l in current_leaders]]
                random.shuffle(pool)
                
                for person in pool:
                    p_name = clean_name(person)
                    best_leader = None
                    min_score = float('inf')
                    sorted_leaders = sorted(teams.keys(), key=lambda k: len(teams[k]))
                    for leader in sorted_leaders:
                        current_team = teams[leader]
                        score = 0
                        for member in current_team:
                            pair = tuple(sorted([p_name, clean_name(member)]))
                            score += overlap_counts[pair]
                        if score < min_score:
                            min_score = score
                            best_leader = leader
                    teams[best_leader].append(person)
                
                # 결과 세션에 저장 (화면이 새로고침돼도 유지됨)
                st.session_state.generated_teams = teams

        # 세션에 저장된 조 결과가 있으면 표시
        if st.session_state.generated_teams:
            teams = st.session_state.generated_teams
            
            st.subheader("🎉 편성 결과")
            result_cols = st.columns(len(teams))
            for idx, (leader, members) in enumerate(teams.items()):
                with result_cols[idx % len(result_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{idx+1}조 ({len(members)}명)**")
                        st.markdown(f"👑 **{leader}**")
                        for m in members:
                            if m != leader:
                                st.text(f"- {m}")
                        # 검증
                        warnings = []
                        for m1, m2 in itertools.combinations(members, 2):
                            if overlap_counts[tuple(sorted([clean_name(m1), clean_name(m2)]))] >= 3:
                                warnings.append(f"{m1}-{m2}")
                        if warnings:
                            st.warning(f"⚠️ {', '.join(warnings)}")
                        else:
                            st.success("OK")
            
            st.divider()
            # 저장 로직
            if st.button("💾 결과 저장하기 (DB 업데이트)"):
                new_record = {
                    "round": len(db_data) + 1,
                    "date": datetime.datetime.now().strftime("%y.%m"),
                    "groups": list(teams.values())
                }
                db_data.append(new_record)
                save_data(db_data)
                
                # 저장 후 세션 초기화 (중복 저장 방지)
                st.session_state.generated_teams = None
                st.success("저장되었습니다! 히스토리 탭에서 확인하세요.")
                st.rerun()

# -----------------------------------------------------------
# [탭 2] 히스토리 관리
# -----------------------------------------------------------
with tab2:
    st.header("📝 데이터 조회 및 삭제")
    flat_data = []
    for record in db_data:
        groups_str = []
        for group in record['groups']:
            groups_str.append(f"[{group[0]}(장): {', '.join(group[1:])}]")
        flat_data.append({"회차": record['round'], "시기": record['date'], "조 편성": " / ".join(groups_str)})
    
    df_hist = pd.DataFrame(flat_data)
    st.dataframe(df_hist, use_container_width=True, hide_index=True)
    
    st.divider()
    col_del1, col_del2 = st.columns([3, 1])
    with col_del1:
        delete_target = st.selectbox("삭제할 회차", df_hist['회차'].sort_values(ascending=False))
    with col_del2:
        st.write("")
        st.write("")
        if st.button("🗑️ 삭제", type="primary"):
            new_db = [r for r in db_data if r['round'] != delete_target]
            save_data(new_db)
            st.success("삭제 완료")
            st.rerun()

# -----------------------------------------------------------
# [탭 3] 만남 분석
# -----------------------------------------------------------
with tab3:
    st.header("📊 전체 만남 횟수 분석표")
    st.caption("누가 누구와 몇 번 같은 조였는지 한눈에 확인하세요.")
    
    search_members = st.multiselect("특정 인원만 보기 (비워두면 전체)", all_members)
    target_members = search_members if search_members else all_members
    
    if target_members:
        matrix_data = pd.DataFrame(index=target_members, columns=target_members)
        for m1 in target_members:
            for m2 in target_members:
                if m1 == m2:
                    matrix_data.loc[m1, m2] = 0
                else:
                    pair = tuple(sorted([clean_name(m1), clean_name(m2)]))
                    matrix_data.loc[m1, m2] = overlap_counts[pair]
        
        matrix_data = matrix_data.astype(int)
        st.dataframe(
            matrix_data.style.background_gradient(cmap="Reds", axis=None),
            use_container_width=True,
            height=600
        )
    else:
        st.info("데이터가 없습니다.")
