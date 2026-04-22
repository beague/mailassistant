from flask import Flask, jsonify, render_template
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def get_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_12474475031-6ar3ue8r2p985sorsh2lmnfr656meqbm.apps.googleusercontent.com.json',
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)


def get_header(headers, name):
    for h in headers:
        if h["name"] == name:
            return h["value"]
    return ""


@app.route("/")
def home():
    return render_template("index.html")


# 📩 GET EMAILS
@app.route("/emails")
def emails():
    service = get_service()

    results = service.users().messages().list(
        userId='me',
        maxResults=15
    ).execute()

    messages = results.get('messages', [])

    mails = []

    for msg in messages:
        data = service.users().messages().get(
            userId='me',
            id=msg['id']
        ).execute()

        headers = data["payload"]["headers"]

        mails.append({
            "id": msg["id"],
            "from": get_header(headers, "From"),
            "subject": get_header(headers, "Subject"),
            "date": get_header(headers, "Date"),
            "snippet": data["snippet"]
        })

    return jsonify(mails)


# 🗑 SUPPRESSION MAIL
@app.route("/delete/<mail_id>")
def delete_mail(mail_id):
    service = get_service()

    service.users().messages().trash(
        userId='me',
        id=mail_id
    ).execute()

    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)