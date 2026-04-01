import os
import sys
import resend

def send_newsletter(html_content: str, issue_number: int, issue_date: str):
    resend.api_key = os.environ["RESEND_API_KEY"]

    recipient_email = os.environ["RECIPIENT_EMAIL"]
    from_email = os.environ.get("FROM_EMAIL", "East / West Review <newsletter@yourdomain.com>")

    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [recipient_email],
        "subject": f"East / West Review — {issue_date}",
        "html": html_content,
    }

    email = resend.Emails.send(params)
    print(f"Email sent successfully. ID: {email['id']}")
    return email

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_newsletter.py <html_file> <issue_number> <issue_date>")
        sys.exit(1)

    html_file = sys.argv[1]
    issue_number = sys.argv[2]
    issue_date = sys.argv[3]

    with open(html_file, "r") as f:
        html_content = f.read()

    print(f"Sending Vol. {issue_number} ({issue_date}) to {os.environ.get('RECIPIENT_EMAIL', '[not set]')}...")
    send_newsletter(html_content, issue_number, issue_date)
