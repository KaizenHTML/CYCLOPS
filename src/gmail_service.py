import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

class GmailService:
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
        self.default_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback").strip()
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.userinfo_uri = "https://www.googleapis.com/oauth2/v2/userinfo"
        self.gmail_base_uri = "https://gmail.googleapis.com/gmail/v1/users/me"

    def get_authorization_url(self, redirect_uri=None, state="cyclops_state"):
        target_redirect = redirect_uri or self.default_redirect_uri
        scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/gmail.readonly"
        ]
        scope_str = " ".join(scopes)
        params = {
            "client_id": self.client_id,
            "redirect_uri": target_redirect,
            "response_type": "code",
            "scope": scope_str,
            "access_type": "online",
            "prompt": "consent",
            "state": state
        }
        prepared_req = requests.Request("GET", self.auth_uri, params=params).prepare()
        return prepared_req.url

    def exchange_code_for_token(self, code, redirect_uri=None):
        target_redirect = redirect_uri or self.default_redirect_uri
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": target_redirect,
            "grant_type": "authorization_code"
        }
        res = requests.post(self.token_uri, data=data, timeout=12)
        print("GOOGLE TOKEN RESPONSE STATUS:", res.status_code)
        if res.status_code != 200:
            print("DETALLE ERROR GOOGLE TOKEN:", res.text)
            return None
        return res.json()

    def get_user_profile(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(self.userinfo_uri, headers=headers, timeout=10)
        print("GOOGLE PROFILE STATUS:", res.status_code)
        if res.status_code != 200:
            print("DETALLE ERROR GOOGLE PROFILE:", res.text)
            return None
        return res.json()

    def list_recent_messages(self, access_token, max_results=8):
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.gmail_base_uri}/messages"
        params = {"maxResults": max_results}
        res = requests.get(url, headers=headers, params=params, timeout=12)
        print("GOOGLE LIST MESSAGES STATUS:", res.status_code)
        if res.status_code != 200:
            print("DETALLE ERROR GOOGLE LIST:", res.text)
            return []
        data = res.json()
        messages = data.get("messages", [])
        print("TOTAL MENSAJES RECUPERADOS DE GMAIL:", len(messages))
        return messages

    def get_message_detail(self, access_token, message_id):
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.gmail_base_uri}/messages/{message_id}"
        params = {"format": "full"}
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code != 200:
            return None
        return res.json()

    def extract_email_payload(self, msg_json):
        headers_list = msg_json.get("payload", {}).get("headers", [])
        headers_map = {h.get("name", "").lower(): h.get("value", "") for h in headers_list}
        
        subject = headers_map.get("subject", "Sin asunto")
        sender = headers_map.get("from", "Desconocido")
        date_str = headers_map.get("date", "")
        snippet = msg_json.get("snippet", "")

        body_text = self._extract_body(msg_json.get("payload", {}))
        if not body_text:
            body_text = snippet

        return {
            "id": msg_json.get("id"),
            "subject": subject,
            "sender": sender,
            "date": date_str,
            "snippet": snippet,
            "body": body_text
        }

    def _extract_body(self, payload):
        if not payload:
            return ""

        body_data = payload.get("body", {}).get("data")
        if body_data:
            try:
                decoded_bytes = base64.urlsafe_b64decode(body_data.encode("ASCII"))
                return decoded_bytes.decode("utf-8", errors="replace")
            except Exception:
                pass

        parts = payload.get("parts", [])
        for part in parts:
            mime_type = part.get("mimeType", "")
            part_body_data = part.get("body", {}).get("data")
            if mime_type == "text/plain" and part_body_data:
                try:
                    decoded = base64.urlsafe_b64decode(part_body_data.encode("ASCII"))
                    return decoded.decode("utf-8", errors="replace")
                except Exception:
                    pass
            elif mime_type.startswith("multipart/") and "parts" in part:
                sub_body = self._extract_body(part)
                if sub_body:
                    return sub_body

        for part in parts:
            part_body_data = part.get("body", {}).get("data")
            if part_body_data:
                try:
                    decoded = base64.urlsafe_b64decode(part_body_data.encode("ASCII"))
                    return decoded.decode("utf-8", errors="replace")
                except Exception:
                    pass

        return ""
