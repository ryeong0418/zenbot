import requests
import json
import msal
from datetime import datetime
from flask import Flask, request, redirect, url_for
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
from pprint import pprint
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter


class CallOutlookAIP:

     # .env 파일에서 환경 변수 로드

    def __init__(self):

        load_dotenv()
        self.GRAPH_API_ENDPOINT = os.getenv('GRAPH_API_ENDPOINT')
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        self.TENANT_ID = os.getenv('TENANT_ID')
        self.AUTHORITY = f"https://login.microsoftonline.com/{self.TENANT_ID}"
        self.REDIRECT_URI = os.getenv('REDIRECT_URI')
        self.SCOPE = ['User.Read', 'Mail.Read']
        self.CONNECTION_STRING = os.getenv('CONNECTION_STRING')
        self.CONTAINER_NAME = os.getenv('CONTAINER_NAME')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.app = Flask(__name__)
        self.add_routes()

    def add_routes(self):
        self.app.add_url_rule('/', 'home', lambda: 'Server is running!')
        self.app.add_url_rule('/login', 'login', self.login)
        self.app.add_url_rule('/getAToken','getAToken', self.get_a_token)

    def login(self):
        try:

            # Azure AD에 등록된 app에 접근
            # Azure AD에 인증 요청을 보내고 액세스 토큰을 받을 수 있음. 이 토큰을 사용하여 Azure 리소스에 접근할 수 있음.
            app = msal.ConfidentialClientApplication(
                self.CLIENT_ID,
                authority=self.AUTHORITY,
                client_credential=self.CLIENT_SECRET
            )

            # 인증 요청 URL 생성 -> 사용자가 인증을 완료하면 Azure AD는 사전에 정의된 REDIRECT_RIL(http://localhost:5000/getAToken)로 인증코드를 보내게 됩니다.
            auth_url = app.get_authorization_request_url(self.SCOPE, redirect_uri=self.REDIRECT_URI)

            # 브라우저에서 인증 URL 열기
            return redirect(auth_url)
        except Exception as e:
            return f"An error occurred during login: {str(e)}"


    def get_a_token(self):
        code = request.args.get('code')
        load_dotenv()
        total_text=''
        if code:
            try:
                app = msal.ConfidentialClientApplication(
                    self.CLIENT_ID,
                    authority=self.AUTHORITY,
                    client_credential=self.CLIENT_SECRET
                )
                # 권한부여 코드로 액세스 토큰 요청
                result = app.acquire_token_by_authorization_code(code, scopes=self.SCOPE, redirect_uri=self.REDIRECT_URI)

                if 'access_token' in result:
                    access_token = result['access_token']
                    messages = self.get_outlook_messages(access_token)

                    for val in messages['value']:
                        html_content = val['body']['content']
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text_content = soup.get_text()
                        total_text = total_text+text_content + '\n'

                    today_date = datetime.today()
                    filename = f"outlook_messages-{today_date}.txt"
                    upload_status = self.upload_to_blob(total_text, filename)

                    return f'Messages: {total_text} Upload_status:{upload_status}'
                else:
                    return f"Error obtaining access token: {result.get('error_description')}"
            except Exception as e:
                return f"An error occurred while obtaining the access token: {str(e)}"
        else:
            return 'No authorization code received.'

    def get_outlook_messages(self, access_token):
        try:
            endpoint = "https://graph.microsoft.com/v1.0/me/messages"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }

            response = requests.get(endpoint, headers=headers)

            if response.status_code == 200:
                messages = response.json()
                return messages
            else:
                return f"Error: {response.status_code}, {response.text}"
        except Exception as e:
            return f"An error occurred while retrieving messages: {str(e)}"


    def upload_to_blob(self, data, filename):

        blob_service_client=BlobServiceClient.from_connection_string(self.CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(self.CONTAINER_NAME)

        try:
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(data, blob_type="BlockBlob")
            return "Upload successful"
        except Exception as e:
            return f"An error occurred while uploading to Blob Storage: {str(e)}"

    def run(self, port=5000):
        self.app.run(port=port)


if __name__ == '__main__':
    server = CallOutlookAIP()
    server.run()
