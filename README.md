
## 📬 ZENBOT

### Outlook 메일 데이터를 자연어로 검색할 수 있는 RAG 기반 챗봇
OAuth 인증을 통해 사용자의 메일을 수집하고, Azure Data Lake → LangChain 임베딩 → Azure AI Search → Streamlit UI를 통해 최종적으로 메일 검색이 가능한 챗봇을 구현하였습니다.


## 🛠 기술 스택
| 영역          | 기술                                          |
|-------------|---------------------------------------------|
| 인증          | OAuth2, Microsoft Graph API, Flask          |
| 저장          | Azure Data Lake Storage Gen2                |
| 전처리         | Databricks, PySpark                         |
| 임베딩 및 벡터 검색 | 	OpenAI text-embedding-3-large, LangChain, 	Azure AI Search |
| 챗봇 UI       | 	Streamlit                       |

## ✅ 주요 기능

🔐 Outlook OAuth 인증: 사용자의 로그인 정보를 위임받아 메일 접근

📨 메일 수집 및 전처리: HTML/서명 제거 후 .txt로 정제하여 저장

🧠 LangChain RAG 파이프라인 구축: 문서 분할 → 임베딩 → 벡터 검색

💬 Streamlit 챗봇: 자연어로 메일 검색 가능, 질문에 유사 메일 내용 응답

## 🏗️ Architecture
![zenbot_architecture](/assets/zenbot_architecture.png)

## 데모 시나리오 예시
![zenbot](/assets/zenbot.jpg)