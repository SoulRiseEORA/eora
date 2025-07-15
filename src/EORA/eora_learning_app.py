
import streamlit as st
import requests

st.set_page_config(page_title="EORA 학습 인터페이스", layout="wide")

st.title("🧠 EORA 학습 앱")
st.markdown("첨부파일을 업로드하고, 질문을 입력하면 EORA가 GPT 기반 분석을 수행합니다.")

uploaded_file = st.file_uploader("📂 분석할 파일 업로드", type=["py", "txt"])
question = st.text_area("❓ 분석할 질문을 입력하세요", height=100)

if uploaded_file and question:
    if st.button("🧠 분석 실행"):
        with st.spinner("EORA가 파일을 읽고 분석 중입니다..."):
            files = {"file": uploaded_file.getvalue()}
            data = {"prompt": question}
            try:
                response = requests.post("http://127.0.0.1:8600/upload", files={"file": uploaded_file}, data=data)
                if response.ok:
                    result = response.json()
                    st.success(f"총 {result['청크수']}개의 청크가 처리되었습니다.")
                    for res in result["응답결과"]:
                        with st.expander(f"📄 청크 {res['청크']} 응답 보기"):
                            st.markdown(res["응답"])
                else:
                    st.error(f"서버 오류: {response.status_code}")
            except Exception as e:
                st.error(f"요청 실패: {e}")
