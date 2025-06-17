import streamlit as st
import os
import streamlit_mermaid as stmd
import base64

col1, col2, col3 = st.columns([1,6,1])

with col2:
    st.markdown("""
    # KSAT Agent
    _Multi-Agent 기반 수능 국어 독서 영역 출제 자동화 시스템_

    ```
    제작자: 권준희
    소속: 연세대학교 교육학과
    버전: 0.7.4 (2025.06.17)
    - Fine-tuned 모델 업그레이드로 지문 품질 대폭 향상
    - 문항 구성 다양화, 오답 선지 고도화
    - 출제 절차 간소화 및 사용자 상호작용 강화
    ```""", unsafe_allow_html=True)

    st.info("KSAT Agent를 직접 사용해보고 싶다면, 좌측 상단의 '출제 AI 사용하기' 메뉴를 클릭하세요.", icon="💡")
    st.info("KSAT Agent가 출제한 예시 지문을 확인하고 싶다면, 좌측 상단의 '출제 결과물 예시' 메뉴를 클릭하세요.", icon="💡")

    st.markdown("""
    ---

    ## 1️⃣ 프로젝트 개요

    KSAT Agent는 수능 국어 독서 영역 출제를 자동화하는 Multi-Agent 시스템입니다. 대성학원, 메가스터디 등 대형 학원에서 3년간 국어 모의고사 출제자로 활동한 경험과 노하우를 AI 시스템에 구현했습니다. 교육 격차 해소를 목적으로, 기존 출제 프로세스의 시간과 비용을 99% 단축하면서도 수능 기출 수준의 품질을 유지합니다.
    """, unsafe_allow_html=True)

    with open("./docs/preview.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="KSAT Agent 최종 화면" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">KSAT Agent 최종 화면</figcaption>
        </div>
    ''')

    st.markdown("""
    ### 프로젝트 효과

    | 항목 (지문 당) | 기존  | KSAT Agent 사용 시 |
    |------|---------|--------------------|
    | **소요 시간** | 1 ~ 2 개월 | **10 분** |
    | **비용** | 100~200만 원 | **200~500 원** |
    | **의사소통** | 서면 피드백 반복 | 실시간 AI 대화 |

    - 기존 출제 프로세스 대비 비용과 출제 시간을 99% 단축
    - 외주 출제자에 의존하던 비효율적인 구조를 개선
    - 누구나 쉽게 고품질 모의고사 콘텐츠를 제작 가능
    - **강남대성수능연구소와 협업 논의 진행 중**

    ---
    """, unsafe_allow_html=True)

    st.markdown("""
    ## 2️⃣ 사용자 경험

    KSAT Agent는 6단계의 체계적인 워크플로우를 통해 수능 국어 독서 지문과 문항을 자동으로 생성합니다.

    ### 1. 주제 및 분야 입력

    사용자는 원하는 출제 분야나 구체적인 주제를 자연어로 입력합니다. Streamlit 기반의 대화형 웹 인터페이스에서 직관적으로 요청을 전달할 수 있습니다.
    """, unsafe_allow_html=True)

    with open("./docs/step_1.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="주제 및 분야 입력" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">주제 및 분야 입력</figcaption>
        </div>
    ''')

    st.markdown("""
    ### 2. 기출 DB 검색 & 주제 선정

    입력된 주제와 가장 유사한 기출 지문을 ChromaDB 벡터 임베딩을 활용해 빠르게 검색합니다. 이를 통해 출제 의도를 명확히 파악하고, 기존 기출의 맥락을 참고할 수 있습니다.
    """, unsafe_allow_html=True)

    with open("./docs/step_2.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="기출 DB 조회" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">기출 DB 조회</figcaption>
        </div>
    ''')

    st.markdown("""
    ### 3. 웹 기반 자료 리서치

    최신 정보나 특수 주제에 대해 웹 검색 도구를 활용해 추가 자료를 수집합니다. 이를 통해 최신 트렌드나 심화된 배경지식까지 반영할 수 있습니다.
    """, unsafe_allow_html=True)

    with open("./docs/step_3.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="자료 리서치" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">자료 리서치</figcaption>
        </div>
    ''')

    st.markdown("""
    ### 4. 개요 설계 및 지문 작성

    AI 에이전트가 입력된 주제와 참고 자료를 바탕으로 지문 개요를 설계하고, 파인튜닝된 모델을 통해 실제 수능 스타일의 독서 지문을 작성합니다. 이 과정은 Passage Editor가 전담합니다.
    """, unsafe_allow_html=True)

    with open("./docs/step_4.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="개요 및 지문 작성" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">개요 및 지문 작성</figcaption>
        </div>
    ''')

    st.markdown("""
    ### 5. 문제 출제 설계 및 준비

    작성된 지문을 바탕으로, Question Editor 에이전트가 기출 DB와 참고 자료를 추가로 탐색하여 문항 출제에 필요한 정보를 정리하고, 출제 방향을 설계합니다.
    """, unsafe_allow_html=True)

    with open("./docs/step_5.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="문제 출제 준비" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">문제 출제 준비</figcaption>
        </div>
    ''')

    st.markdown("""
    ### 6. 문항 및 해설 자동 생성

    최종적으로 AI가 수능 독서형 문항과 해설을 자동으로 생성하여, 사용자는 완성된 지문과 문제, 해설을 한 번에 받아볼 수 있습니다.
    """, unsafe_allow_html=True)

    with open("./docs/step_6.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="문제 및 해설 출력" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">문제 및 해설 출력</figcaption>
        </div>
    ''')

    st.markdown("""
    ---

    ## 3️⃣ 결과물 비교

    - 동일한 경제 현상을 다룬 지문을 요청한 결과, 일반적인 GPT에 비해 지문과 문제 모두 '수능스러움' 훨씬 잘 묻어났습니다.
    """, unsafe_allow_html=True)

    with st.expander("일반 AI가 작성한 수능 지문"):
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');
        .passage-font {
            border: 0.5px solid black;
            border-radius: 0px;
            padding: 5px !important;
            margin-bottom: 20px;
            font-family: 'Nanum Myeongjo', serif !important;
            font-size: 14px !important;
            line-height: 1.7;
            letter-spacing: -0.01em;
            font-weight: 500;
        }
        .passage-font p {
            text-indent: 1em; /* 각 문단의 첫 줄 들여쓰기 */
            margin-bottom: 0em;
        }
        .question-font {
            font-family: 'Nanum Myeongjo', serif !important;
            font-size: 14px !important;
            line-height: 1.7em;
            letter-spacing: -0.01em;
            font-weight: 500;
            margin-bottom: 1.5em;
        }
        .question-font table tr td table {
            font-family: '돋움', Dotum, sans-serif !important;
            font-size: 14px;
            line-height: 1.5em;
            font-weight: 500;
            letter-spacing: -0.02em;
        }
        </style>

        ### A. 일반 AI 결과물 (GPT 4.1)

        <div style="display: flex; gap: 24px; justify-content: center;">
        <div style="flex:1; max-width:450px;">
            <div class="passage-font">
            <p>한 국가의 경제에서 환율 변동은 수출과 수입, 그리고 경상수지에 다양한 영향을 미친다. 특히 'J커브 현상'은 환율이 상승(자국 통화의 가치가 하락)할 때 경상수지의 변화 양상이 단순하지 않음을 보여주는 이론이다.</p>
            <p>예를 들어, 국내 기업들이 주로 원화로 비용을 지불하고, 수출 대금을 달러로 받는 한국 경제를 생각해 보자. 원/달러 환율이 상승하면, 달러로 표시된 상품 가격이 원화로 환산될 때 높아진다. 즉, 같은 달러 금액의 수출을 하더라도 이를 원화로 환산하면 더 많은 돈을 벌게 된다. 반면, 해외에서 수입하는 상품을 구매할 때는 더 많은 원화를 지불해야 한다.</p>
            <p>하지만 J커브 현상이 의미하는 바는 단순히 환율이 오르면 경상수지가 바로 개선되지 않는다는 점이다. 예를 들어, 한국의 한 해 수출액이 1,000억 달러, 수입액이 900억 달러라고 가정하자. 원/달러 환율이 1,000원에서 1,200원으로 20% 상승했다고 하더라도, 대부분의 수출·수입 계약은 미리 정해진 가격과 물량에 따라 진행된다. 환율이 급등한 직후에는 수입 원화 비용이 즉시 늘어나지만, 수출 물량이나 수입 물량은 단기적으로 거의 변하지 않는다. 이로 인해 수입 대금이 증가하면서 오히려 경상수지가 일시적으로 악화될 수 있다.</p>
            <p>시간이 지나면서 변화가 발생한다. 수입 상품의 가격이 오르면 소비자와 기업들은 대체재를 찾거나 수입을 줄이기 시작한다. 반면, 해외 시장에서는 한국 상품의 가격 경쟁력이 높아지기 때문에 수출 주문이 늘어난다. 대략 몇 개월에서 1년 정도의 시간이 흐르면, 수입은 감소하고 수출은 증가하여 경상수지가 점차 개선된다. 이 과정에서 경상수지의 변화 추이를 그래프로 나타내면, 처음에는 하락하다가 이후에 상승 곡선을 그리며 알파벳 'J'와 비슷한 형태가 나타난다.</p>
            <p>즉, J커브 현상은 환율 상승 → 단기적 경상수지 악화 → 중장기적 경상수지 개선이라는 순차적 과정을 설명한다. 이러한 현상은 단기에는 가격 효과(환율 변동에 따른 금액 증가)가, 장기에는 수량 효과(무역량 변화에 따른 효과)가 더 크게 작용하기 때문이다.</p>
            <p>따라서 J커브 현상은 환율정책을 운용할 때 정책 효과가 나타나는 시점과 그 원인을 이해하는 데 중요한 시사점을 제공한다.</p>
            </div>
        </div>
        <div style="flex:1; max-width:450px;">
            <div class="question-font">
            <b>1. 다음 중 J커브 현상에 대한 설명으로 적절하지 <u>않은</u> 것은?</b><br>
            <table style="width:100%; font-size:14px;">
                <tr><td>ㄱ. 원/달러 환율이 상승할 경우, 경상수지는 즉시 개선된다.</td></tr>
                <tr><td>ㄴ. 단기적으로는 수입 대금이 증가해 경상수지가 악화될 수 있다.</td></tr>
                <tr><td>ㄷ. 시간이 지나면 수출은 증가하고 수입은 감소하여 경상수지가 개선될 수 있다.</td></tr>
                <tr><td>ㄹ. J커브라는 명칭은 경상수지의 변화 양상이 영문자 'J'와 유사하게 나타나기 때문이다.</td></tr>
            </table>
            ① ㄱ  <br>② ㄴ  <br>③ ㄷ  <br>④ ㄹ  <br>⑤ ㄴ, ㄷ <br><br><br>
            <b>2. 다음 &lt;보기&gt;는 J커브 현상과 관련된 상황을 서술한 것이다. 이에 대한 이해로 가장 적절한 것을 고르시오.</b><br>
            <table style="width:100%; font-size:14px;">
                <tr><td>
                한 나라의 환율이 단기간에 15% 상승하였다. 이로 인해 수입품 가격이 즉각 오르면서, 해당 국가의 경상수지는 한동안 악화되는 모습을 보였다. 그러나 8개월이 지난 후부터 수출이 점차 늘어나고 수입이 감소하여 경상수지가 개선되기 시작하였다.<br><br>
                경제학자 A는 이러한 현상이 국제무역 계약의 특성과 경제주체의 행동 변화가 시간이 지나면서 점진적으로 나타났기 때문이라고 설명하였다.
                </td></tr>
            </table>
            ① 경상수지의 단기 악화는 환율 상승으로 인한 수입 대금 증가와 무역량의 즉각적 변화 때문이다.  <br>
            ② J커브 현상에서는 환율이 상승한 직후부터 수출이 급격하게 증가한다.  <br>
            ③ 환율 상승 직후, 대부분의 무역 계약은 이미 정해진 가격과 물량에 따라 이루어진다.  <br>
            ④ 경제주체의 행동 변화는 환율 상승 직후 즉시 나타나 경상수지가 바로 개선된다.  <br>
            ⑤ 장기적으로도 경상수지는 환율 변동과 관계없이 변하지 않는다.
            </div>
        </div>
        </div>""", unsafe_allow_html=True)
    
    with st.expander("KSAT Agent가 작성한 수능 지문"):
        st.markdown("""
        ### B. KSAT Agent 결과물

        <div style="display: flex; gap: 24px; justify-content: center;">
        <div style="flex:1; max-width:450px;">
            <div class="passage-font">
            <p>수출이 수입보다 많은 상태를 무역수지가 흑자라고 하고, 수입이 수출보다 많은 상태를 무역수지가 적자라고 한다. 환율은 자국 화폐와 외국 화폐의 교환 비율을 의미하는데, 일반적으로 환율이 상승하면 수출이 증가하고 수입이 감소하여 무역수지가 개선된다고 알려져 있다. 그런데 단기적으로는 무역수지가 오히려 악화되었다가 일정 기간이 지난 후에야 개선되는 현상이 나타나기도 한다. 이러한 현상을 J커브 효과라고 하는데, 그 이유는 무역수지의 변화 추이를 그래프로 나타내면 알파벳 J와 같은 모양이 되기 때문이다.</p>
            <p>그렇다면 J커브 효과는 왜 나타나는 것일까? 환율 변동에 따른 무역수지의 변화는 가격 효과와 물량 효과로 설명할 수 있다. 가격 효과란 환율 변동으로 인해 수출입 상품의 가격이 변동하여 무역수지가 변화하는 효과이고, 물량 효과란 가격 변동에 따라 수출입 상품의 물량이 변동하여 무역수지가 변화하는 효과이다. 환율이 상승하면 외국에서 보면 수출 상품의 가격은 이전보다 낮아지므로 수출은 증가하고, 수입 상품의 가격은 이전보다 높아지므로 수입은 감소하여 무역수지가 개선되는 것이 일반적인 경우이다.</p>
            <p>그런데 수출입 물량은 단기적으로는 변동하지 않는 경우가 많다. 이미 체결된 수출입 계약에 따라 일정 기간은 그 계약에서 정해진 물량이 거래되고, 그 이후에도 가격 변동에 따라 물량이 조정되는 데에는 시차가 존재하기 때문이다. 따라서 단기에는 가격 효과만 나타나게 된다. 환율이 상승하여 자국 화폐의 가치가 하락하면 동일한 양의 수입 상품을 수입하기 위해 지불해야 하는 자국 화폐의 액수는 증가한다. 즉, 수입 물량은 변하지 않지만 수입에 지출되는 자국 화폐의 액수는 증가한다. 한편, 수출 상품의 경우에는 자국 화폐로 지불되는 액수는 변하지 않는다. 이로 인해 단기에는 무역수지가 악화되는 현상이 나타나게 된다. 그러나 일정 기간이 지나고 나면 수출은 증가하고 수입은 감소하는 물량 효과가 나타나기 시작하여 무역수지가 개선되는 방향으로 전환된다.</p>
            <p>이러한 J커브 효과는 수출과 수입의 가격 탄력성이 중요한 역할을 한다. 가격 탄력성이란 상품의 가격이 변동할 때 그 가격 변동에 따라 수요나 공급이 민감하게 반응하는 정도를 말한다. 수출과 수입의 가격 탄력성이 크다면 환율 상승으로 인한 가격 변동에 따라 수출은 증가하고 수입은 감소하여 장기적으로는 무역수지가 개선되는 효과가 나타나게 된다.</p>
            </div>
        </div>
        <div style="flex:1; max-width:450px;">
            <div class="question-font">
            <b>1. ㉠ '가격 효과'와 ㉡ '물량 효과'에 대한 이해로 적절하지 <u>않은</u> 것은?</b><br>
            <div style="margin-left: 1em; margin-top: 7px;">
                <div style="text-indent: -1.5em; padding-left: 1.5em;">① 환율 상승 초기에는 ㉠이 주로 작용하여, 수입품에 대한 자국 화폐 지불액이 늘어나 무역수지가 악화될 수 있다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">② ㉡은 수출입 물량이 가격 변동에 반응하여 조정되는 것으로, 일반적으로 ㉠보다 시간적 지연을 두고 나타난다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">③ ㉠과 ㉡은 환율 변동이 무역수지에 미치는 영향을 설명하는 개념으로, J커브 효과의 발생 원인을 이해하는 데 기여한다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">④ 환율 상승 시 ㉠은 수출 상품의 외화 표시 가격을 하락시키고, ㉡은 수입 상품의 물량 감소를 유발하여 무역수지를 개선시킨다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">⑤ ㉠만 고려할 경우 환율 상승은 즉각적인 무역수지 개선을 가져오지만, ㉡의 지연된 발현으로 인해 J커브 현상이 나타난다.</div>
            </div>
            <br>
            <div class="question-font">
                <b>2. 다음 &lt;보기&gt;는 환율 상승 이후 시간에 따른 무역수지 변화를 나타낸 그래프이다. 윗글을 바탕으로 &lt;보기&gt;를 이해한 내용으로 적절하지 <u>않은</u> 것은? [3점]</b><br>
                <table style="width:100%; font-size:14px;">
                <tr>
                    <td style="text-align: center; font-weight: bold; background-color: #f8f8f8; padding: 5px; font-size:10px;">&lt;보기&gt;</td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-size:14px;">
                    그래프는 T<sub>0</sub> 시점에서 환율이 상승한 이후 시간 경과에 따른 무역수지의 변화를 보여준다. 가로축은 시간, 세로축은 무역수지를 나타내며, 세로축의 0은 무역수지 균형 상태를 의미한다. T<sub>1</sub>은 무역수지가 최저점에 도달하는 시점, T<sub>2</sub>는 무역수지가 다시 균형 상태로 회복되는 시점, T<sub>3</sub> 이후는 무역수지가 개선되어 흑자 상태를 유지하는 시점이다.
                    <svg width="400" height="250" viewBox="0 0 400 250" style="width:60%; min-width:240px; max-width:60%; height:auto; display:block; margin-left:auto; margin-right:auto;">
                        <line x1="50" y1="200" x2="380" y2="200" style="stroke:black;stroke-width:1" />
                        <line x1="50" y1="50" x2="50" y2="200" style="stroke:black;stroke-width:1" />
                        <text x="40" y="45" style="font-size:10px; text-anchor:end;">흑자</text>
                        <text x="40" y="128" style="font-size:10px; text-anchor:end;">0</text>
                        <text x="40" y="205" style="font-size:10px; text-anchor:end;">적자</text>
                        <text x="50" y="215" style="font-size:10px; text-anchor:middle;">T₀</text>
                        <text x="130" y="215" style="font-size:10px; text-anchor:middle;">T₁</text>
                        <text x="230" y="215" style="font-size:10px; text-anchor:middle;">T₂</text>
                        <text x="330" y="215" style="font-size:10px; text-anchor:middle;">T₃</text>
                        <text x="370" y="215" style="font-size:10px; text-anchor:middle;">시간</text>
                        <text x="15" y="128" style="font-size:10px; writing-mode:tb; text-anchor:middle;">무역수지</text>
                        <line x1="50" y1="125" x2="380" y2="125" style="stroke:gray;stroke-width:0.5;stroke-dasharray:4;" />
                        <path d="M 50 125 Q 90 180, 130 190 T 230 125 Q 280 90, 330 80 L 370 75" style="stroke:blue;stroke-width:2;fill:none;" />
                        <circle cx="50" cy="125" r="2" style="fill:blue;" />
                        <circle cx="130" cy="190" r="2" style="fill:blue;" />
                        <circle cx="230" cy="125" r="2" style="fill:blue;" />
                        <circle cx="330" cy="80" r="2" style="fill:blue;" />
                        <text x="130" y="100" style="font-size:12px; text-anchor:middle;">A 구간 (T₀-T₁)</text>
                        <text x="200" y="150" style="font-size:12px; text-anchor:middle;">B 구간 (T₁-T₂)</text>
                        <text x="300" y="60" style="font-size:12x; text-anchor:middle;">C 구간 (T₂-T₃ 이후)</text>
                    </svg>
                    </td>
                </tr>
                </table>
                <div style="margin-left: 1em; margin-top: 7px; font-size:14px;">
                <div style="text-indent: -1.5em; padding-left: 1.5em;">① A 구간(T<sub>0</sub>~T<sub>1</sub>)에서는 환율 상승에도 불구하고 수출입 물량의 단기적 경직성으로 인해 가격 효과가 두드러져, 자국 화폐 기준 수입액이 증가하면서 무역수지가 악화된다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">② A 구간(T<sub>0</sub>~T<sub>1</sub>)이 형성되는 것은 기존 수출입 계약 물량이 일정 기간 유지되고, 생산 및 소비 패턴 변경에 시간이 소요되어 물량 조정이 지연되기 때문이다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">③ B 구간(T<sub>1</sub>~T<sub>2</sub>)에서는 가격 변동에 따른 물량 효과가 점차 나타나기 시작하여 수출 물량이 늘고 수입 물량이 줄면서 무역수지가 개선되기 시작한다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">④ 만약 T<sub>0</sub> 시점에서 수출입 상품의 가격 탄력성이 현재 그래프가 가정하는 것보다 더 크다면, T<sub>1</sub> 시점의 무역수지 적자 폭은 더 깊어지고 T<sub>2</sub> 시점은 더 늦춰질 것이다.</div>
                <div style="text-indent: -1.5em; padding-left: 1.5em;">⑤ C 구간(T<sub>2</sub>~T<sub>3</sub> 이후)에서는 물량 효과가 가격 효과를 압도하여 무역수지가 지속적으로 개선되거나 흑자 상태를 유지하며, 이는 수출입 가격 탄력성이 클수록 더 뚜렷하게 나타난다.</div>
                </div>
            </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info(":bulb: 좌측 상단의 '출제 결과물 예시' 메뉴를 통해 더 많은 예시를 확인할 수 있습니다.")

    st.markdown("""
    ---

    ## 4️⃣ 파인튜닝
    """, unsafe_allow_html=True)

    st.markdown("""
    ### A. 파인튜닝 필요성

    기본 GPT 모델은 친절하고 쉽게 설명하도록 학습되어 수능 지문 특유의 압축적 정보 밀도를 구현할 수 없었습니다. 수능 독서 지문은 제한된 공간 안에 학술적이고 촘촘한 정보를 담아야 하는 독특한 문체적 특성을 가지고 있습니다.

    ### B. 파인튜닝 과정

    1. **기출 데이터 수집**: 100개 평가원 기출 문항을 기반 데이터로 수집
    2. **Data Augmentation 적용**: LLM을 활용한 데이터 증강 기법으로 1000여개 데이터셋 구축
    3. **OpenAI 플랫폼 파인튜닝**: Fine-tuning API를 통해 GPT-4.1 기반 전용 모델 학습
    4. **최적 파라미터 탐색**: 수십 번의 실험을 통해 최적의 하이퍼파라미터 발견

    ### C. 파인튜닝 결과
    """, unsafe_allow_html=True)

    with open("./docs/fine-tune.png", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    st.html(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{data}" alt="Fine-tuning 성능 향상 결과" style="width: 100%;">
            <figcaption style="font-size: 0.9em; color: grey; margin-top: 10px;">Fine-tuning 성능 향상 결과</figcaption>
        </div>
    ''')

    st.markdown("""
    | Loss Type | 초기 (0 step) | 106 step | 213 step | 총 감소값 |
    |-----------|---------------|----------|----------|-----------|
    | Training Loss | 1.6 | 0.9 | 0.5 | -1.1 |
    | Validation Loss (Full Val) | 1.6 | 1.0 | 0.65 | -0.95 |

    **Loss 감소율**: Training Loss 68.8% 감소, Validation Loss 59.4% 감소
    """, unsafe_allow_html=True)

    st.markdown("""
    - **문체 개선**: 친절한 설명형 → 압축적 학술형 문체로 전환
    - **정보 밀도 극대화**: 동일한 분량 내 2-3배 많은 개념과 정보 포함
    - **수능 특화**: 기출 문제와 유사한 논리 구조와 용어 사용 패턴 습득
    - **과적합 방지**: 데이터 증강으로 충분한 데이터 확보, 3 epoch까지 train/val loss 지속 감소
    - **전문가 평가**: 문체, 개념 밀도, 논리성, 용어 정확성 모든 영역에서 대폭 향상

    ### D. 파인튜닝 전후 비교 예시

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');
    .passage-font {
        border: 0.5px solid black;
        border-radius: 0px;
        padding: 10px;
        margin-bottom: 20px;
        font-family: 'Nanum Myeongjo', serif !important;
        font-size: 14px;
        line-height: 1.7;
        letter-spacing: -0.01em;
        font-weight: 500;
    }
    .passage-font p {
        text-indent: 1em;
        margin-bottom: 0em;
    }
    </style>

    동일한 시스템 프롬프트에 대한 출력 차이 비교

    <div style="display: flex; gap: 24px; justify-content: center;">
    <div style="flex:1; max-width:450px;">
        <h4>파인튜닝 이전</h4>
        <blockquote>직관적이고 친절한 풀이형 설명, 동일한 분량에서 정보 밀도가 낮음</blockquote>
        <div class="passage-font">
        <p>우리는 일상생활 속에서 물건을 '가지고 있다'는 사실만으로 그 물건의 주인이라고 생각하기 쉽다. 그러나, 법적으로 '점유'와 '소유'는 구별된다. 점유란 물건에 대한 사실상의 지배 상태를 의미하며, 실제로 물건을 관리·통제하고 있는 상황을 말한다. 반면, 소유는 물건을 자유롭게 사용, 수익, 처분할 수 있는 권리를 의미한다. 예를 들어, 임차인은 임대차 계약을 통해 집을 점유하지만, 그 집의 소유자는 임대인이다. 이처럼 점유자와 소유자는 반드시 일치하지 않는다.</p>
        <p>우리 민법은 오랜 기간 타인의 부동산을 점유한 자에게 일정한 조건을 갖추면 소유권을 취득할 수 있도록 점유취득시효 제도를 두고 있다. 이는 부동산 관계를 명확히 하여 법적 안정성을 도모하기 위한 것이다. 점유취득시효가 성립하려면 다음과 같은 요건이 필요하다. 첫째, 20년 동안 계속하여 점유해야 한다. 둘째, 소유자가 될 의사로, 즉 스스로의 권리로 점유(자주점유)해야 하며, 점유자는 자주점유한 것으로 추정된다. 셋째, 점유는 폭력이나 강박 등 없이 평온하게 이루어져야 하고, 넷째, 점유 사실이 외부에 드러나 은밀하지 않은, 공연한 점유이어야 한다.</p>
        </div>
    </div>
    <div style="flex:1; max-width:450px;">
        <h4>파인튜닝 이후</h4>
        <blockquote>학술적, 압축적인 수능형 설명, 동일한 분량에서 정보 밀도가 높음</blockquote>
        <div class="passage-font">
        <p>우리 민법은 점유취득시효 제도를 두고 있다. 점유란 물건에 대한 사실상의 지배 상태를 의미하고, 소유란 물건을 사용․수익․처분할 수 있는 권리를 가진 상태를 의미한다. 따라서 점유자와 소유자는 항상 일치하지 않는다. 예를 들어 임차인은 임차물에 대한 점유자이지만, 임차물의 소유자는 아니다. 점유취득시효는 타인의 부동산을 소유의 의사로 평온․공연하게 20년간 점유한 자에게 그 부동산의 소유권을 취득할 수 있도록 하는 제도이다.</p>
        <p>점유취득시효가 인정되려면 시효 기간의 점유가 자주점유이어야 한다. 자주점유란 소유의 의사로 하는 점유를 말하는데, 점유자가 스스로 소유자를 자처하는 것만으로는 부족하고 점유 취득의 원인으로 볼 때 소유자와 동일하게 지배․처리하려는 의사를 가지고 있어야 한다. 점유자는 자주점유로 추정되므로 타인이 빌려준 물건을 점유한 경우와 같이 점유 취득의 원인으로 볼 때 소유의 의사가 없다고 인정되는 특별한 사정이 있는 경우에만 점유자의 자주점유가 부정된다. 또한 점유취득시효가 인정되려면 시효 기간의 점유가 폭력이나 강박에 의한 것이 아니어야 하고 은밀한 것이어서는 안 된다.</p>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ---

    ## 5️⃣ FastAPI + LangGraph 구현
    """, unsafe_allow_html=True)

    st.markdown("""
    ### A. 전체 아키텍처
    """, unsafe_allow_html=True)

    stmd.st_mermaid("""
    graph TD
    USER["👤 User"]

    subgraph FRONTEND_LAYER ["Presentation Layer (Frontend)"]
        direction LR
        STREAMLIT_UI["🖥️ Streamlit UI"]
    end

    subgraph DOCKER_CONTAINER ["Docker Container (Backend)"]
        direction LR
        subgraph FASTAPI_SERVER ["FastAPI Server"]
            direction TB
            API_GW["API Gateway (REST/SSE)"]
            LANGGRAPH_ENGINE["LangGraph Engine"]
        end
        
        subgraph AGENTS ["AI Agents"]
            direction TB
            SUPERVISOR["🤖 Supervisor"]
            PASSAGE_EDITOR["✍️ Passage Editor"]
            QUESTION_EDITOR["❓ Question Editor"]
        end

        subgraph BACKEND_TOOLS ["Backend Tools"]
            direction TB
            DB_RAG["📚 DB RAG"]
            WEB_SEARCH["🌐 Web Search"]
            HANDOFF["🤝 Handoff"]
        end
    end

    subgraph DATA_LAYER ["Data Layer"]
        direction LR
        CHROMA_DB["📊 ChromaDB (Vector Store)"]
        SQLITE_DB["💾 SQLite (Session State Checkpoints)"]
    end

    %% Connections
    USER --> STREAMLIT_UI
    STREAMLIT_UI -- "HTTP/SSE" --> API_GW
    
    API_GW --> LANGGRAPH_ENGINE
    
    LANGGRAPH_ENGINE -- "Workflow Orchestration" --> SUPERVISOR
    SUPERVISOR -- "Tool Invocation" --> BACKEND_TOOLS
    
    DB_RAG -- "Data Retrieval" --> CHROMA_DB
    LANGGRAPH_ENGINE -- "State Persistence" --> SQLITE_DB
    
    %% Styling
    classDef frontend fill:#D6EAF8,stroke:#333;
    classDef backend fill:##D5F5E3,stroke:#333;
    classDef data fill:#D5F5E3,stroke:#333;

    class USER,STREAMLIT_UI frontend;
    class DOCKER_CONTAINER,FASTAPI_SERVER,API_GW,LANGGRAPH_ENGINE,AGENTS,SUPERVISOR,PASSAGE_EDITOR,QUESTION_EDITOR,BACKEND_TOOLS,DB_RAG,WEB_SEARCH,HANDOFF backend;
    class CHROMA_DB,SQLITE_DB data;
    """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    - GCP 서버 내 Docker 컨테이너에서 FastAPI와 LangGraph 엔진이 함께 동작
    - 세션별 체크포인터 DB, ChromaDB로 데이터/상태 관리
    - 사용자는 웹 UI로 요청 입력, 실시간 결과 확인

    ### B. 워크플로우

    - 사용자가 Streamlit UI에 주제/요청 입력
    - FastAPI 서버가 입력을 LangGraph 엔진에 전달
    - LangGraph가 에이전트/도구를 순차 호출
    - 처리 결과를 실시간으로 프론트엔드에 스트리밍
    - 입력 즉시 결과 확인, 전체 데이터 비동기 처리
    """, unsafe_allow_html=True)

    stmd.st_mermaid("""
    sequenceDiagram
        participant User as "👤 사용자"
        participant Frontend as "🖥️ Streamlit UI"
        participant Backend as "⚙️ FastAPI 서버"
        participant Engine as "🧠 LangGraph 엔진"
        
        User->>Frontend: 주제/요청 입력
        Frontend->>Backend: POST /chat/stream (세션 ID, 프롬프트)
        Backend->>Engine: graph.astream_events(inputs) 호출
        
        loop 실시간 이벤트 스트림
            Engine-->>Backend: Agent/Tool 실행 이벤트 청크
            Backend-->>Frontend: SSE 이벤트 (AI 메시지, 상태 변경 등)
            Frontend-->>User: UI에 실시간 결과 표시
        end
    """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    ### C. FastAPI 서버 구현

    - 각 사용자 세션별로 LangGraph 인스턴스 관리
    - 세션별 체크포인터 DB로 대화 이력/상태 저장
    - SSE 방식으로 LangGraph 실행 결과 실시간 전달
    - 여러 사용자가 동시에 접속해도 세션 독립 동작

    **1. 실시간 채팅 스트리밍 엔드포인트**
    - 사용자의 입력을 LangGraph 엔진에 전달, 결과를 스트리밍 반환
    """, unsafe_allow_html=True)

    st.code("""
    @app.post("/chat/stream")
    async def stream_chat(req: ChatRequest):
        async def generate():
            session_data = await get_session_graph(req.session_id)
            graph = session_data["graph"]
            inputs = {"messages": [HumanMessage(content=req.prompt)]}
            cfg = {"configurable": {"thread_id": req.session_id}, "recursion_limit": 100}
            async for chunk in graph.astream(inputs, config=cfg, stream_mode="messages"):
                yield f"data: {json.dumps(chunk)}\\n\\n"
        return StreamingResponse(generate(), media_type="text/plain")
    """, language='python')

    st.markdown("""
    **2. 세션 대화 이력 조회 엔드포인트**
    - 특정 세션의 대화 이력 조회
    """, unsafe_allow_html=True)

    st.code("""
    @app.get("/sessions/{session_id}/history")
    async def get_session_history(session_id: str):
        session_data = await get_session_graph(session_id)
        # 체크포인트에서 이력 조회 로직
        return {"history": history}
    """, language='python')

    st.markdown("""
    **3. 세션 삭제 및 정리 엔드포인트**
    - 세션 삭제 및 리소스 정리
    """, unsafe_allow_html=True)

    st.code("""
    @app.delete("/sessions/{session_id}")
    async def delete_session(session_id: str):
        if session_id in session_graphs:
            await session_graphs[session_id]["memory"].close()
            del session_graphs[session_id]
        return {"status": "deleted"}
    """, language='python')

    st.markdown("""
    ### D. LangGraph 에이전트 구조

    - Supervisor, Passage Editor, Question Editor 등 역할별 에이전트로 구성
    - Supervisor가 전체 흐름 제어, 각 에이전트는 독립적으로 작업 수행
    - Tool Node를 통해 외부 DB/웹 검색 등 리소스 활용
    """, unsafe_allow_html=True)

    stmd.st_mermaid("""
    graph TD
        START(["🚀 시작"]) --> AGENTS
        
        subgraph AGENTS["🎯 에이전트 그룹"]
            SUPERVISOR["Supervisor Agent"]
            PASSAGE["Passage Editor"]
            QUESTION["Question Editor"]
        end
        
        AGENTS --> TOOLS["🛠️ Tool Node"]
        
        TOOLS --> WEB["🌐 Web Search"]
        TOOLS --> DB["📊 ChromaDB"]
    """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    **에이전트 간 Handoff**:
    - Command.PARENT: 부모 그래프로 제어권 이동
    - Send: 특정 에이전트에게 데이터와 함께 작업 전달
    - State 업데이트: 현재 활성 에이전트 추적 및 메시지 이력 관리
    - 비동기 처리: 각 에이전트는 독립적으로 실행, 완료 시 결과 반환
    """, unsafe_allow_html=True)

    st.code("""
    @tool
    async def call_passage_editor(
        summary: Optional[str],
        request: Optional[str],
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        pre_passage = state.get("passage", "")
        tool_message = ToolMessage(content="passage_editor 에이전트를 호출합니다.", tool_call_id=tool_call_id)
        return Command(
            graph=Command.PARENT,
            goto=Send("passage_editor", {"summary": summary, "request": request, "passage": pre_passage}),
            update={"messages": state["messages"] + [tool_message], "current_agent": "passage_editor"}
        )
    """, language='python')

    st.markdown("""
    ### E. State 구조

    - State/reducer 구조는 불필요한 정보로 인한 컨텍스트 흐림, 토큰 소모 최적화를 위해 설계
    - 에이전트 간 공통 상태 객체(MultiAgentState) 공유
    - 각 에이전트는 필요한 정보만 참조/갱신, 전체 워크플로우 일관성 유지
    - 구조 확장 용이, 새로운 에이전트/기능 추가에 유연
    """, unsafe_allow_html=True)

    st.code("""
    # 공통 스키마
    class MultiAgentState(AgentState):
        messages: Annotated[List[BaseMessage], merge_messages]  # 커스텀 리듀서
        current_agent: str | None = None      # 현재 활성 에이전트 추적
        summary: str = ""                     # 주제 요약
        passage: str = ""                     # 생성된 지문
        question: str = ""                    # 생성된 문항
        request: str = ""                     # 사용자 요청사항

    # Question Editor 전용 상태
    class QuestionEditorState(MultiAgentState):
        messages: Annotated[List[BaseMessage], add_messages]  # 기본 리듀서 사용
        passage: str      # 필수: 문항 출제 대상 지문
        request: str      # 선택: 세부 요청사항
        question: str     # 기존 문항 (수정 시)
    """, language='python')

    st.markdown("""
    **MultiAgentState 필드별 에이전트 참조 관계**:

    | field | Supervisor | Passage Editor | Question Editor | 설명 |
    |------------|:-------------:|:------------------:|:------------------:|------|
    | **messages** | 👀 참조 | - | - | 전체 대화 내역 |
    | **summary** | ✍️ **생성** | 👀 참조 | - | 개요 |
    | **passage** | 👀 참조 | ✍️ **생성** | 👀 **참조** | 지문 |
    | **question** | 👀 참조 | - | ✍️ **생성** | 문항 |
    | **request** | ✍️ **생성** | 👀 참조 | 👀 참조 | 사용자 요청사항 |

    ### F. RAG DB(ChromaDB 임베딩 전략)

    - LangGraph 에이전트가 외부 지식/기출 데이터 참조 시 사용
    - 문제 출제, 지문 생성 등에서 유사도 검색·맥락 보강·참고자료 제공에 활용
    - 검색 정확도 향상을 위해 쿼리+메타데이터(연도, 분야 등) 필터 조합 지원
    - 불필요한 정보 노출 최소화, 필요한 맥락만 효율적으로 제공
    - OpenAI 임베딩 모델로 기출 지문 벡터화, 벡터 유사도 기반 검색
    - 대용량 데이터에서도 빠르고 정확한 의미 기반 검색 가능
    """, unsafe_allow_html=True)

    stmd.st_mermaid("""
    graph LR
        A["🎯 Agent"] --> B["🛠️ Tool Node"]
        B --> C["🔍 임베딩 & 벡터 검색"]
        C --> D["📋 지문 + 메타데이터"]
        D --> A
    """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    ---

    ## 6️⃣ 배포
    """, unsafe_allow_html=True)

    st.markdown("""
    ### A. Docker 기반 컨테이너화

    **Docker 구성 요소**:

    | 구성 요소 | 설명 | 목적 |
    |-----------|------|------|
    | **Base Image** | Python 3.11-slim | 경량화된 Python 런타임 환경 |
    | **System Packages** | build-essential, sqlite3, supervisor | 컴파일 도구, DB, 프로세스 관리 |
    | **Python Dependencies** | requirements.txt 기반 설치 | FastAPI, LangGraph 등 필수 패키지 |
    | **Directory Structure** | DB/checkpointer, DB/kice | 데이터베이스 및 체크포인트 저장소 |
    | **Process Manager** | Supervisor | 멀티 프로세스 관리 및 자동 재시작 |
    | **Port Exposure** | 8000번 포트 | FastAPI 서버 외부 접근 |
    """, unsafe_allow_html=True)

    st.markdown("""
    ### B. GCP 클라우드 배포
    """, unsafe_allow_html=True)

    stmd.st_mermaid("""
    graph TB
        subgraph GCP["☁️ Google Cloud Platform"]
            CE["🖥️ Compute Engine<br/>e2-standard-2"]
            FW["🔥 Firewall Rules<br/>HTTP/HTTPS"]
            PD["💾 Disk<br/>Checkpointer, 기출 DB 데이터 보존"]
        end
        
        subgraph DOCKER["🐳 Docker Environment"]
            DC["📋 Docker Compose"]
            APP["🚀 FastAPI App"]
            DB["📊 ChromaDB"]
            SUP["⚙️ Supervisor"]
        end
        
        CE --> DOCKER
        FW --> CE
        PD --> DB
    """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    **GCP 인프라 구성**:

    | 리소스 | 스펙 | 용도 |
    |--------|------|------|
    | **Compute Engine** | e2-standard-2 (2vCPU/8GB RAM) | 메인 애플리케이션 서버 |
    | **Operating System** | Ubuntu 22.04 LTS | 안정적인 Linux 환경 |
    | **Network** | HTTP(80)/HTTPS(443) 방화벽 | 웹 트래픽 허용 |
    | **Storage** | 영구 디스크 20GB | 데이터베이스 및 로그 보존 |
    | **Monitoring** | Supervisor + Docker logs | 프로세스 상태 및 로그 관리 |

    ### C. Github Actions CI/CD
    """, unsafe_allow_html=True)

    stmd.st_mermaid("""
    graph LR
        A["👨‍💻 개발자<br/>main 브랜치 푸시"] --> B["🔄 Github Actions<br/>빌드 & 체크아웃"]
        B --> C["🔐 GCP 서버<br/>코드 동기화"]
        C --> D["🐳 Docker 재빌드<br/>배포 완료"]
    """, pan=False, zoom=False, show_controls=False)

    st.markdown("""
    **CI/CD 파이프라인 단계**:

    | 단계 | 작업 내용 | 소요 시간 |
    |------|-----------|-----------|
    | **1. Trigger** | main 브랜치 push 감지 | 즉시 |
    | **2. Checkout** | 최신 소스 코드 가져오기 | ~30초 |
    | **3. SSH Connect** | GCP 서버 원격 접속 | ~10초 |
    | **4. Code Update** | git pull로 코드 동기화 | ~20초 |
    | **5. Container Rebuild** | docker-compose 재빌드 | ~2-3분 |
    | **6. Health Check** | 서비스 정상 동작 확인 | ~30초 |
    """, unsafe_allow_html=True)
