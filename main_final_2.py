import streamlit as st
from datetime import datetime
import requests
import json
import base64
import smtplib
import markdown
import openai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap
from dotenv import load_dotenv
import os
from pyairtable import Api

load_dotenv()  # .env 파일에서 환경 변수를 불러옵니다.
openai.api_key = os.getenv('OPENAI_API_KEY')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BETTERMODE_CLIENT_ID = "2ae5ac5e-480a1a1fcdfb"
BETTERMODE_CLIENT_SECRET = "f3d2027f8dd54b3a9df31e8ca029c98a"

# 페이지 제목 설정
st.title('AI Talk 자동 생성 프로그램🚀')
st.write('간단한 연사 정보, 강의 내용을 입력하면 자동으로 AI Talk 상세 페이지와 포스터가 생성됩니다. 🎨')
st.markdown("---")

# 세션 상태 변수 초기화
if 'generated_page' not in st.session_state:
    st.session_state['generated_page'] = ''
if 'titles' not in st.session_state:
    st.session_state['titles'] = []
if 'subtitles' not in st.session_state:
    st.session_state['subtitles'] = []

# 강의 정보 입력 폼
topic = st.text_input("강의 주제", value="⚡️직접 경험한 클로드 3 지금 당장 사용해본 성공사례 ")

# 한 줄에 날짜와 시간 입력 받기
col1, col2, col3 = st.columns(3)
with col1:
    date = st.date_input("강의 날짜")
with col2:
    start_time = st.time_input("시작 시간", datetime.strptime("18:00", "%H:%M").time())
with col3:
    end_time = st.time_input("종료 시간", datetime.strptime("20:00", "%H:%M").time())

speaker_name = st.text_input("연사 이름", value="클승우")
speaker_bio = st.text_area("연사 소개", value="""2010년부터 아이폰 앱개발을 시작해서 현재는 AI를 활용한 업무자동화를 연구하고 있습니다.
AI로 업무자동화하기 (GPTers), 클클 Claude Clan (GPTers) 채팅방을 운영하고 있습니다.
챗GPT 출시 후 일반인 대상 AI활용, 리터러시 교육을 1년동안 진행하고 있습니다.""")

outline = st.text_area("강의 내용 및 목차", value="""* 클로드 특강(3/21) 회고
    - Opus 무료 사용법, 클로드 5달러 무료제공?, 실시간 채팅을 통해 얻은 통찰
* 클로드 3 커뮤니티 인사이트 공유
    - 클로드 3로 LLM 앱 만들기, 부동산 분석, 확장프로그램 만들기, 소설쓰기 등 
* 클로드 3의 강점을 활용한 새로운 시도와 발견
    - 1분만에 웹크롤러 만들기, 논문 분석하기, 숨겨진 주제(특강에서 소개 예정)""")

# 강의 소개 페이지 생성 함수
def generate_lecture_page():
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}"
        },
        data=json.dumps({
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "당신은 최고의 에듀테크 회사의 직원입니다. 다음은 강의 상세 페이지 생성을 위한 요청입니다.마크다운 형식을 사용해주세요."},
                {"role": "user", "content": f"""
                다음 예시를 참고하여 입력된 강의 정보를 바탕으로 새로운 강의 상세 페이지를 작성해 주세요. 최대한 친절하고 자세하게 작성해주세요. 

                [강의 상세 페이지 포맷]
                1. 인트로 300자 이상 작성

                2. 강의 날짜를 MM월 DD일, HH:MM - HH:MM PM(AM) 형식으로 수정

                3. 예시
                   📅 강의 날짜: 04월 12일, 06:00 PM - 08:00 PM
                 
                   📚 장소: 온라인 (줌) 강의 링크
                 
                   📝 참가 신청: 참가신청 링크 (작성하시면 링크를 보내드립니다.)

                4. 아웃트로 300자 이상 작성

                [입력된 강의 정보]
                ✏️ 강의 주제: {topic}
                📅 강의 날짜: {date.strftime('%Y년 %m월 %d일')}, {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
                👨🏻‍🏫 연사 이름: {speaker_name}
                👨🏻‍💼 연사 소개: {speaker_bio}
                💬 강의 내용 및 목차: {outline}
                
                📚 장소 : 온라인 (줌) 신청시 온라인 줌 링크를 보내드립니다.
                📝 참가신청 : https://ai.gpters.org/aitalk_rsvp (작성하시면 링크를 보내드립니다.)

                [예시]
                ✏️ 프롬프트 엔지니어링 마스터클래스 : ChatGPT 활용의 기술

                🎓 ChatGPT의 모든 것, 최고의 전문가에게 배우는 프롬프트 엔지니어링 노하우!

                ChatGPT를 단순한 채팅 이상으로 활용하고 싶으신가요? 프롬프트 엔지니어링 기술을 익혀 ChatGPT를 업무에 적극 활용할 수 있습니다. 이 강의에서는 프롬프트 엔지니어링의 기본 개념부터 ChatGPT 활용을 위한 고급 팁까지 모두 다룹니다. ChatGPT 사용의 달인이 되어보세요!

                📅 일시 : 6월 10일 토요일 2:00 - 5:00 PM 

                📚 장소 : 온라인 (Zoom) https://ai.gpters.org/pe_masterclass
                
                📝 참가신청 : https://ai.gpters.org/pe_rsvp  (작성하시면 참여 링크를 보내드립니다.)
                
                
                ### 👨‍🏫 강사 소개 : 김프롬프트 
                - OpenAI의 초기 멤버로 ChatGPT 개발에 참여
                - 현재는 기업들의 ChatGPT 도입 및 활용을 돕는 컨설턴트로 활동 중
                - 프롬프트 엔지니어링 분야의 선구자로 잘 알려짐
                
                
                ### ✏️ 커리큘럼 
                1부 : 프롬프트 엔지니어링 기초
                - 프롬프트 엔지니어링이란?

                - ChatGPT의 동작 원리 이해하기

                - 효과적인 프롬프트 작성법
                
                2부 : 프롬프트 엔지니어링 활용
                - 업무 자동화를 위한 프롬프트 설계

                - 창의적 아이디어 도출을 위한 프롬프트

                - 글쓰기에 활용할 수 있는 프롬프트
                
                3부 : 프롬프트 엔지니어링 고급 기술  
                - 롤플레잉을 활용한 고급 프롬프트

                - 연속적인 대화를 위한 프롬프트 설계

                - 의도하지 않은 결과 피하기
                
                4부 : 질의응답
                
                ChatGPT를 제대로 활용하고 싶다면 이번 기회를 놓치지 마세요. 프롬프트 엔지니어링 마스터클래스에서 여러분을 뵙겠습니다!
                """}
            ],
            "max_tokens": 2048,
            "temperature": 0.7,
        })
    )
    # API 응답 확인
    if response.status_code == 200:
        response_json = response.json()
        # 생성된 강의 소개 페이지 내용을 session_state에 저장
        st.session_state['generated_page'] = response_json['choices'][0]['message']['content']


        # 제목과 부제목 추천 요청 보내기
        title_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai.api_key}" 
            },
            data=json.dumps({
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "당신은 SEO에 최적화된 매력적인 제목과 부제목을 생성하는 데 능숙한 AI입니다."},
                {"role": "user", "content": f"""
                다음 강의 정보를 바탕으로 매력적이고 SEO에 최적화된 제목과 부제목을 각각 5개씩 제안해주세요. 제목은 최대 30자, 부목은 최대 40자 내 작성해주세요.

                [강의 정보]
                ✏️ 강의 주제: {topic}
                👨🏻‍💼 연사 소개: {speaker_bio}
                💬 강의 내용 및 목차: {outline}
                """}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        })
        )

        # 성공적인 API 응답 처리
        if title_response.status_code == 200:
            title_response_json = title_response.json()
            last_message_content = title_response_json['choices'][0]['message']['content']

            # 응답 내용을 제목과 부제목으로 분리
            split_content = last_message_content.strip().split('\n\n')
            
            if len(split_content) >= 2:
                # 제목과 부제목이 모두 있는 경우
                st.session_state['titles'] = split_content[0].split('\n')[:5]
                st.session_state['subtitles'] = split_content[1].split('\n')[:5]
            elif len(split_content) == 1:
                # 제목만 있는 경우, 부제목을 빈 리스트로 설정
                st.session_state['titles'] = split_content[0].split('\n')[:5]
                st.session_state['subtitles'] = []
        else:
            st.error(f"API 요청 실패: {title_response.status_code} - {title_response.text}")

# 강의 소개 페이지 생성 버튼
if st.button("강의 소개 페이지 생성"):
    with st.spinner("강의 소개 페이지 생성 중... 이 작업은 2~3분 정도 소요됩니다. 조금만 기다려주세요 💪"):
        generate_lecture_page()
    
    if 'generated_page' in st.session_state:
        st.session_state['displayed_page'] = st.session_state['generated_page']

if 'displayed_page' in st.session_state:
    st.markdown("---")
    st.markdown("### 생성된 강의 소개 페이지")
    st.markdown(st.session_state['displayed_page'])

st.markdown("---")
st.subheader("제목과 부제목 선택📝")
st.write('제목과 부제목을 선택하거나, 직접 입력하실 수 있어요')

# 제목 선택
title_options = st.session_state['titles'] + ['직접 입력']
title_index = st.selectbox("제목 선택", options=range(len(title_options)), format_func=lambda x: title_options[x] if x < len(title_options) else '')

if title_index == len(title_options) - 1:
    custom_title = st.text_input("제목 직접 입력")

# 제목 확정 버튼 처리
if st.button("제목 확정"):
    if title_index == len(title_options) - 1:
        selected_title = custom_title  # 사용자가 직접 입력한 제목
    else:
        selected_title = st.session_state['titles'][title_index]  # 목록에서 선택한 제목
    
    # 앞의 숫자와 따옴표 삭제
    if selected_title.startswith(('1.', '2.', '3.', '4.', '5.')):
        selected_title = selected_title[2:].strip()
    
    # 맨 앞과 맨 뒤의 따옴표 삭제
    selected_title = selected_title.strip('"')
    
    st.session_state['selected_title'] = selected_title

# 부제목 선택
subtitle_options = st.session_state['subtitles'] + ['직접 입력']
subtitle_index = st.selectbox("부제목 선택", options=range(len(subtitle_options)), format_func=lambda x: subtitle_options[x] if x < len(subtitle_options) else '')

if subtitle_index == len(subtitle_options) - 1:
    custom_subtitle = st.text_input("부제목 직접 입력")

# 부제목 확정 버튼 처리
if st.button("부제목 확정"):
    if subtitle_index == len(subtitle_options) - 1:
        selected_subtitle = custom_subtitle  # 사용자가 직접 입력한 부제목
    else:
        selected_subtitle = st.session_state['subtitles'][subtitle_index]  # 목록에서 선택한 부제목
    
    # 앞의 숫자와 따옴표 삭제
    if selected_subtitle.startswith(('1.', '2.', '3.', '4.', '5.')):
        selected_subtitle = selected_subtitle[2:].strip()
    
    # 맨 앞과 맨 뒤의 따옴표 삭제
    selected_subtitle = selected_subtitle.strip('"')
    
    st.session_state['selected_subtitle'] = selected_subtitle
    
    st.session_state['selected_subtitle'] = selected_subtitle

# 확정된 제목과 부제목을 표시
if 'selected_title' in st.session_state:
    st.write(f"확정된 제목: {st.session_state.get('selected_title', '')}")
if 'selected_subtitle' in st.session_state:
    st.write(f"확정된 부제목: {st.session_state.get('selected_subtitle', '')}")

# 전화번호 입력 섹션
if 'selected_title' in st.session_state and 'selected_subtitle' in st.session_state:
    st.markdown("---")
    st.subheader("연락처 정보📱")
    st.write("게시글 작성자이신 스터디장님의 전화번호를 입력해주세요")
    phone_number = st.text_input("전화번호 (예: 01012345678)")
    
    if phone_number:
        st.session_state['phone_number'] = phone_number
        st.write(f"입력된 전화번호: {phone_number}")
        
        # Airtable API 설정
        api = Api(AIRTABLE_API_KEY)
        base_id = "appq8xK4PLp7D7aCg"
        table_id = "tblAV1fM6DdHEMfWR"
        
        try:
            # 전화번호로 사용자 검색
            records = api.table(base_id, table_id).all(formula=f"FIND('{phone_number}', {{전화번호}}) > 0")
            
            if records:
                st.success("✅ 등록된 사용자를 찾았습니다!")
                for record in records:
                    user_name = record['fields'].get('이름', '정보 없음')
                    bettermode_user_id = record['fields'].get('bettermode 유저 id', '')
                    st.write(f"이름: {user_name}")
                    
                    if bettermode_user_id:
                        # Bettermode에 게시글 생성 버튼
                        if st.button("Bettermode에 게시글 생성"):
                            try:
                                # GraphQL mutation 쿼리 정의
                                mutation = """
                                mutation CreateNewPost($input: CreatePostInput!, $spaceId: ID!) {
                                    createPost(input: $input, spaceId: $spaceId) {
                                        id
                                    }
                                }
                                """

                                # 마크다운을 HTML로 변환하고 스타일 적용
                                content_md = st.session_state.get('generated_page', '')
                                
                                def format_curriculum(text):
                                    # 각 줄을 처리
                                    lines = text.split('\n')
                                    formatted_lines = []
                                    current_section = None
                                    
                                    for line in lines:
                                        line = line.strip()
                                        if not line:
                                            continue
                                            
                                        # 부분 제목 (예: "1부: 테스트 기초")
                                        if "부:" in line or "부 :" in line:
                                            if current_section is not None:
                                                formatted_lines.append("</ul></p>")
                                            formatted_lines.append(f"<p>{line}</p>")
                                            formatted_lines.append("<ul>")
                                            current_section = line
                                        # 항목 (예: "- 테스트의 중요성...")
                                        elif line.startswith('-') or line.startswith('*'):
                                            item = line[1:].strip()
                                            formatted_lines.append(f"<li>{item}</li>")
                                    
                                    if current_section is not None:
                                        formatted_lines.append("</ul></p>")
                                    
                                    return '\n'.join(formatted_lines)

                                # 커리큘럼 부분을 찾아서 HTML로 변환
                                parts = content_md.split("### ✏️ 커리큘럼")
                                if len(parts) > 1:
                                    # 커리큘럼 이전 부분
                                    before_curriculum = parts[0]
                                    
                                    # 커리큘럼 부분과 그 이후 부분 분리
                                    remaining = parts[1].split("\n\n", 1)
                                    curriculum = remaining[0]
                                    after_curriculum = remaining[1] if len(remaining) > 1 else ""
                                    
                                    # 커리큘럼 부분만 HTML로 변환
                                    formatted_curriculum = format_curriculum(curriculum)
                                    
                                    # 전체 내용 다시 조합
                                    content_md = f"{before_curriculum}### ✏️ 커리큘럼\n\n{formatted_curriculum}\n\n{after_curriculum}"
                                
                                content_html = markdown.markdown(content_md, extensions=['extra'])
                                
                                # HTML 템플릿 적용 (스타일 추가)
                                styled_html = f"""
                                <div class="flex flex-wrap gap-4 items-center">
                                    <div class="basis-full min-w-0 break-words">
                                        <h1 class="font-medium text-heading-xs text-content">{st.session_state.get('selected_title', '')}</h1>
                                    </div>
                                    <div class="empty:hidden break-words min-w-0 basis-full">
                                        <article class="prose">
                                            <style>
                                                ul {{ list-style-type: disc !important; margin-left: 1.5em; margin-bottom: 1em; }}
                                                ul ul {{ list-style-type: circle !important; margin-left: 1.5em; margin-bottom: 0.5em; }}
                                                li {{ margin-bottom: 0.5em; display: list-item !important; }}
                                                li::before {{ content: none !important; }}
                                                .prose ul > li::before {{ content: none !important; }}
                                                .prose ul > li {{ padding-left: 0 !important; }}
                                            </style>
                                            {content_html}
                                        </article>
                                    </div>
                                    <div class="flex space-s-2 text-content-subdued items-center empty:hidden basis-full">
                                        <div class="flex items-center h-7 space-s-3 flex-1">
                                            <div class="flex-grow min-w-0">
                                                <div class="flex items-center max-w-full">
                                                    <div class="text-content-subdued shrink-0 whitespace-nowrap text-sm">
                                                        {date.strftime('%Y-%m-%d')} {start_time.strftime('%H:%M')}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """

                                # 변수 데이터 준비
                                variables = {
                                    "spaceId": "DpzZo3dmHTGH",
                                    "input": {
                                        "postTypeId": "NR49kR6XEqUbEEr",
                                        "mappingFields": [
                                            {
                                                "key": "title",
                                                "type": "text",
                                                "value": json.dumps(st.session_state.get('selected_title', ''))
                                            },
                                            {
                                                "key": "subtitle",
                                                "type": "text",
                                                "value": json.dumps(st.session_state.get('selected_subtitle', ''))
                                            },
                                            {
                                                "key": "content",
                                                "type": "html",
                                                "value": json.dumps(styled_html)
                                            },
                                            {
                                                "key": "date_time",
                                                "type": "date",
                                                "value": json.dumps(f"{date.strftime('%Y-%m-%d')}T{start_time.strftime('%H:%M')}:00Z")
                                            }
                                        ],
                                        "publish": True,
                                        "ownerId": bettermode_user_id
                                    }
                                }

                                # 디버깅을 위해 변환된 HTML 출력
                                st.write("변환된 HTML:")
                                st.code(styled_html)

                                # 디버깅을 위해 mutation과 변수 출력
                                st.write("Mutation 쿼리:")
                                st.code(mutation)
                                st.write("Variables:")
                                st.code(json.dumps(variables, indent=2))

                                # GraphQL API 호출
                                response = requests.post(
                                    "https://portal.gpters.org/api/bettermode/graphql",
                                    headers={
                                        "X-Bettermode-Client-Id": BETTERMODE_CLIENT_ID,
                                        "X-Bettermode-Client-Secret": BETTERMODE_CLIENT_SECRET,
                                        "Content-Type": "application/json"
                                    },
                                    json={
                                        "query": mutation,
                                        "variables": variables
                                    }
                                )

                                # 디버깅을 위해 응답 출력
                                st.write("API 응답:")
                                st.write(response.json())

                                if response.status_code == 200:
                                    result = response.json()
                                    if "errors" in result:
                                        st.error(f"게시글 생성 실패: {result['errors']}")
                                    else:
                                        post_id = result['data']['createPost']['id']
                                        st.success("✅ Bettermode에 게시글이 성공적으로 생성되었습니다!")
                                        st.markdown(f"[게시글 확인하기](https://www.gpters.org/events/post/{post_id})")
                                        
                                        # 이메일 발송
                                        try:
                                            # 현재 시간으로 transactionId 생성
                                            transaction_id = datetime.now().strftime('%y%m%d%H%M%S')
                                            
                                            # 이메일 발송 요청
                                            email_response = requests.post(
                                                "https://portal.gpters.org/api/internal/emails",
                                                headers={
                                                    "x-admin-token": "Kh4IgiwYUpfqFrl+/exW9aYeHFkvyEZKzO7xqV0SJ7I=",
                                                    "Content-Type": "application/json"
                                                },
                                                json={
                                                    "content": f"{user_name}님이 AI토크 게시글을 생성하셨습니다.",
                                                    "preview": "",
                                                    "bcc": ["dahye@gpters.org"],
                                                    "title": "AI토크 게시글 생성",
                                                    "transactionId": transaction_id,
                                                    "emailId": "AI토크 게시글 생성"
                                                }
                                            )
                                            
                                            if email_response.status_code == 200:
                                                st.success("✉️ 관리자에게 이메일이 발송되었습니다.")
                                            else:
                                                st.warning("⚠️ 이메일 발송에 실패했습니다.")
                                                
                                        except Exception as e:
                                            st.error(f"이메일 발송 중 오류 발생: {str(e)}")
                                else:
                                    st.error(f"게시글 생성 실패: {response.status_code} - {response.text}")
                            except Exception as e:
                                st.error(f"게시글 생성 중 오류 발생: {str(e)}")
                    else:
                        st.warning("⚠️ Bettermode 사용자 ID가 없습니다. 관리자에게 문의해주세요.")
            else:
                st.warning("⚠️ 입력하신 전화번호로 등록된 사용자를 찾을 수 없습니다.")
        
        except Exception as e:
            st.error("Airtable 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
            st.error(f"오류 내용: {str(e)}")
