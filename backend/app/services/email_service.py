import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger("backend.services.email")


def send_tenant_onboarding_email(
    tenant_name: str,
    tenant_email: str,
    temp_password: str,
    company: str | None = None,
    login_url: str = "http://localhost:5173/login"
) -> bool:
    """
    Sends an automated welcome email to a newly created tenant containing their temporary login credentials.
    """
    subject = f"Welcome to LegalFlow AI - Your Tenant Portal Login Access"
    company_display = f" ({company})" if company else ""

    # HTML Email Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .header {{ background-color: #0f172a; color: #ffffff; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
            .content {{ padding: 30px; color: #334155; line-height: 1.6; }}
            .cred-box {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 8px; padding: 20px; margin: 25px 0; }}
            .cred-item {{ margin-bottom: 10px; font-size: 15px; }}
            .cred-item:last-child {{ margin-bottom: 0; }}
            .label {{ font-weight: 600; color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
            .value {{ font-family: 'Courier New', Courier, monospace; font-size: 16px; font-weight: bold; color: #1e293b; background: #e2e8f0; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-top: 4px; }}
            .btn {{ display: inline-block; background-color: #2563eb; color: #ffffff !important; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 15px; text-align: center; }}
            .footer {{ background-color: #f1f5f9; text-align: center; padding: 15px; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>LegalFlow AI</h1>
                <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 14px;">Commercial Tenancy Portal</p>
            </div>
            <div class="content">
                <p>Dear <strong>{tenant_name}</strong>{company_display},</p>
                <p>Your commercial landlord has created your account on <strong>LegalFlow AI</strong>. You can now log into your dedicated tenant portal to view your lease agreement, track rent invoices, and settle payments securely online.</p>
                
                <div class="cred-box">
                    <div class="cred-item">
                        <div class="label">Portal Login URL</div>
                        <div style="font-size: 15px; font-weight: 500; margin-top: 4px;"><a href="{login_url}" style="color: #2563eb;">{login_url}</a></div>
                    </div>
                    <div class="cred-item" style="margin-top: 15px;">
                        <div class="label">Your Login Email</div>
                        <div class="value">{tenant_email}</div>
                    </div>
                    <div class="cred-item" style="margin-top: 15px;">
                        <div class="label">Temporary Password</div>
                        <div class="value">{temp_password}</div>
                    </div>
                </div>

                <p>For security, please log in using your temporary password and update your password under account settings after your first sign in.</p>

                <div style="text-align: center; margin-top: 25px;">
                    <a href="{login_url}" class="btn">Log In to Tenant Portal &rarr;</a>
                </div>
            </div>
            <div class="footer">
                &copy; 2026 LegalFlow AI Commercial Tenancy Platform. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    plaintext_content = f"""
    LegalFlow AI - Tenant Portal Access
    
    Dear {tenant_name}{company_display},
    
    Your commercial landlord has created your account on LegalFlow AI.
    
    Login URL: {login_url}
    Email: {tenant_email}
    Temporary Password: {temp_password}
    
    Please log in and update your password.
    """

    # Dispatch via SMTP if configured
    if settings.SMTP_HOST:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg["To"] = tenant_email

            msg.attach(MIMEText(plaintext_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                if settings.SMTP_PORT == 587:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, [tenant_email], msg.as_string())

            logger.info("Successfully dispatched tenant onboarding email via SMTP", recipient=tenant_email)
            return True
        except Exception as e:
            logger.error("Failed to send tenant onboarding email via SMTP", recipient=tenant_email, error=str(e))
            return False
    else:
        # Development / Simulation Log
        logger.info(
            "SMTP_HOST not set. Simulated sending tenant onboarding email to log",
            recipient=tenant_email,
            login_url=login_url,
            temp_password=temp_password,
        )
        print("\n" + "=" * 60)
        print(f"📧 [AUTOMATED EMAIL SENT TO TENANT: {tenant_email}]")
        print(f"Subject: {subject}")
        print(f"Login URL: {login_url}")
        print(f"Temporary Password: {temp_password}")
        print("=" * 60 + "\n")
        return True
