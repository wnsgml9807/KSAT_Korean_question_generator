import streamlit as st
import json
import os
import glob

st.title("저장된 지문 목록")

# 영구 저장된 파일 목록 로드 함수
def load_permanently_saved_passages():
    temp_dir = os.path.join("DB", "temp")
    if not os.path.exists(temp_dir):
        return []
    
    # 영구 저장 파일 패턴 (세션 ID와 UUID 포함)
    # 모든 passage_*.json 파일을 가져오고 latest는 제외
    files = glob.glob(os.path.join(temp_dir, "passage_*.json"))
    files = [f for f in files if os.path.basename(f) != "latest_passage.json"] 
    
    # 수정 시간 역순 정렬
    files = sorted(files, key=os.path.getmtime, reverse=True)
    
    passages = []
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data['file_path'] = file_path # 파일 경로 추가
                passages.append(data)
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생 ({os.path.basename(file_path)}): {str(e)}")
    return passages

# 저장된 지문 목록 로드
saved_passages = load_permanently_saved_passages()

if saved_passages:
    # 드롭다운으로 표시
    # 옵션 생성 시 제목 없으면 파일명 표시
    passage_options = {p['file_path']: f"{p.get('title', os.path.basename(p['file_path']))}" for p in saved_passages}
    selected_file_path = st.selectbox(
        "불러올 저장된 지문 선택", 
        options=list(passage_options.keys()), 
        format_func=lambda path: passage_options.get(path, os.path.basename(path)),
        index=0 # 기본으로 가장 최근 파일 선택
    )
    
    # 선택된 파일 데이터 찾기
    selected_passage_data = next((p for p in saved_passages if p.get('file_path') == selected_file_path), None)

    if selected_passage_data:
        st.markdown(f"### {selected_passage_data.get('title', '제목 없음')}")
        st.markdown(selected_passage_data.get('passage', '내용 없음'))
        
        if selected_passage_data.get('question'):
            st.markdown(selected_passage_data['question'])
            
        # 파일 삭제 버튼 (영구 저장된 파일 대상)
        if st.button(f"'{selected_passage_data.get('title', '제목 없음')}' 영구 삭제", key=f"delete_{selected_passage_data['file_path']}"):
             try:
                 os.remove(selected_passage_data['file_path'])
                 st.success("선택한 지문이 영구적으로 삭제되었습니다.")
                 st.rerun() # 목록 갱신
             except Exception as e:
                 st.error(f"파일 삭제 중 오류: {e}")
                 
    else:
        st.warning("선택된 지문 데이터를 찾을 수 없습니다.")

else:
    st.info("아직 구현되지 않은 기능입니다.")