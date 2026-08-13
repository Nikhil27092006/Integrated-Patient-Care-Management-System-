"""
Email Service Module — IPCMS
Sends professional HTML emails via Gmail SMTP (or any SMTP provider).
Used to deliver doctor login credentials after admin creates a doctor account.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate, make_msgid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")))


def _get_smtp_config() -> dict:
    """Load SMTP config from environment variables."""
    return {
        "host":      os.getenv("SMTP_HOST", "smtp.gmail.com").strip(),
        "port":      int(os.getenv("SMTP_PORT", "587")),
        "user":      os.getenv("SMTP_USER", "").strip(),
        "password":  os.getenv("SMTP_PASSWORD", "").strip(),
        "from_name": os.getenv("SMTP_FROM_NAME", "IPCMS - Patient Care System").strip(),
    }


def _build_doctor_welcome_html(
    doctor_name: str,
    email: str,
    temp_password: str,
    specialty: str,
    experience: int,
    fee: float,
    bio: str,
    login_url: str,
    admin_name: str,
) -> str:
    """Build a premium HTML email body for doctor welcome/credential mail."""
    year = datetime.now().year
    bio_html = ""
    if bio:
        bio_snippet = bio[:100] + ("…" if len(bio) > 100 else "")
        bio_html = (
            '<div class="profile-row"><span class="profile-key">Bio</span>'
            f'<span class="profile-val" style="max-width:300px;text-align:right;font-size:12px;">'
            f"{bio_snippet}</span></div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Your Doctor Account — IPCMS</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', Arial, sans-serif; background: #f1f5f9; color: #1e293b; }}
    .wrapper {{ max-width: 620px; margin: 40px auto; background: #ffffff;
               border-radius: 20px; overflow: hidden;
               box-shadow: 0 20px 60px rgba(0,0,0,0.12); }}
    .header {{ background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 40%, #14b8a6 100%);
               padding: 44px 40px 36px; text-align: center; }}
    .header-icon {{ font-size: 48px; margin-bottom: 14px; display: block; }}
    .header h1 {{ color: #ffffff; font-size: 26px; font-weight: 700; letter-spacing: -0.5px; }}
    .header p {{ color: rgba(255,255,255,0.85); font-size: 14px; margin-top: 6px; }}
    .badge {{ display: inline-block; background: rgba(255,255,255,0.2);
              border: 1px solid rgba(255,255,255,0.35); border-radius: 20px;
              padding: 4px 14px; font-size: 12px; color: #ffffff; margin-top: 12px; }}
    .body {{ padding: 36px 40px; }}
    .greeting {{ font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 10px; }}
    .intro {{ font-size: 14px; color: #64748b; line-height: 1.7; margin-bottom: 28px; }}
    .section-title {{ font-size: 11px; font-weight: 700; color: #94a3b8;
                      text-transform: uppercase; letter-spacing: 1px; margin-bottom: 14px; }}
    .credentials-box {{ background: linear-gradient(135deg, #f8fafc, #f1f5f9);
                        border: 2px solid #e2e8f0; border-radius: 14px;
                        padding: 24px 28px; margin-bottom: 28px; }}
    .cred-row {{ display: flex; align-items: center; gap: 12px;
                 padding: 12px 0; border-bottom: 1px solid #e2e8f0; }}
    .cred-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
    .cred-icon {{ font-size: 20px; width: 32px; text-align: center; flex-shrink: 0; }}
    .cred-label {{ font-size: 12px; color: #94a3b8; font-weight: 500; margin-bottom: 2px; }}
    .cred-value {{ font-size: 15px; font-weight: 700; color: #0f172a; }}
    .cred-value.password {{ font-family: 'Courier New', monospace; background: #fef3c7;
                            color: #92400e; padding: 2px 8px; border-radius: 6px;
                            border: 1px solid #fde68a; letter-spacing: 1px; }}
    .profile-box {{ background: linear-gradient(135deg, rgba(14,165,233,0.05), rgba(20,184,166,0.05));
                    border: 1px solid rgba(14,165,233,0.2); border-radius: 14px;
                    padding: 20px 24px; margin-bottom: 28px; }}
    .profile-row {{ display: flex; justify-content: space-between; align-items: center;
                    padding: 8px 0; border-bottom: 1px solid rgba(14,165,233,0.1); }}
    .profile-row:last-child {{ border-bottom: none; }}
    .profile-key {{ font-size: 13px; color: #64748b; font-weight: 500; }}
    .profile-val {{ font-size: 13px; font-weight: 700; color: #0f172a; }}
    .cta-btn {{ display: block; text-align: center;
                background: linear-gradient(135deg, #0ea5e9, #0284c7);
                color: #ffffff !important; text-decoration: none;
                font-weight: 700; font-size: 15px; padding: 16px 32px;
                border-radius: 12px; margin: 0 auto 28px;
                letter-spacing: 0.3px;
                box-shadow: 0 6px 20px rgba(14,165,233,0.35); }}
    .warning-box {{ background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px;
                    padding: 16px 20px; margin-bottom: 28px; }}
    .warning-box p {{ font-size: 13px; color: #92400e; line-height: 1.6; }}
    .warning-box strong {{ color: #78350f; }}
    .steps {{ margin-bottom: 28px; }}
    .step {{ display: flex; align-items: flex-start; gap: 14px; margin-bottom: 16px; }}
    .step-num {{ background: linear-gradient(135deg, #0ea5e9, #14b8a6); color: #fff;
                 font-size: 12px; font-weight: 700; border-radius: 50%;
                 width: 26px; height: 26px; display: flex; align-items: center;
                 justify-content: center; flex-shrink: 0; margin-top: 1px; }}
    .step-text {{ font-size: 13.5px; color: #334155; line-height: 1.6; }}
    .step-text strong {{ color: #0f172a; }}
    .divider {{ border: none; border-top: 1px solid #f1f5f9; margin: 24px 0; }}
    .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0;
               padding: 24px 40px; text-align: center; }}
    .footer p {{ font-size: 12px; color: #94a3b8; line-height: 1.7; }}
    .footer strong {{ color: #64748b; }}
    .logo-text {{ font-size: 14px; font-weight: 700; color: #0ea5e9; margin-bottom: 6px; }}
  </style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <span class="header-icon">&#x1F3E5;</span>
    <h1>Welcome to IPCMS, Dr. {doctor_name}!</h1>
    <p>Your doctor account has been successfully created by the admin.</p>
    <span class="badge">&#x1F468;&#x200D;&#x2695;&#xFE0F; Doctor Account &middot; {specialty or 'General Medicine'}</span>
  </div>
  <div class="body">
    <div class="greeting">Hello, Dr. {doctor_name} &#x1F44B;</div>
    <p class="intro">
      <strong>{admin_name}</strong> has created your login account on the
      <strong>Integrated Patient Care Management System (IPCMS)</strong>.
      Below are your login credentials and profile details. Please keep this email safe
      and change your password after your first login.
    </p>
    <div class="section-title">&#x1F510; Your Login Credentials</div>
    <div class="credentials-box">
      <div class="cred-row">
        <span class="cred-icon">&#x1F4E7;</span>
        <div>
          <div class="cred-label">Email / Username</div>
          <div class="cred-value">{email}</div>
        </div>
      </div>
      <div class="cred-row">
        <span class="cred-icon">&#x1F511;</span>
        <div>
          <div class="cred-label">Temporary Password</div>
          <div class="cred-value password">{temp_password}</div>
        </div>
      </div>
      <div class="cred-row">
        <span class="cred-icon">&#x1F310;</span>
        <div>
          <div class="cred-label">Login Portal URL</div>
          <div class="cred-value" style="font-size:13px; color:#0ea5e9;">{login_url}</div>
        </div>
      </div>
    </div>
    <div class="section-title">&#x1FA7A; Your Doctor Profile</div>
    <div class="profile-box">
      <div class="profile-row">
        <span class="profile-key">Full Name</span>
        <span class="profile-val">Dr. {doctor_name}</span>
      </div>
      <div class="profile-row">
        <span class="profile-key">Specialty</span>
        <span class="profile-val">{specialty or 'General Medicine'}</span>
      </div>
      <div class="profile-row">
        <span class="profile-key">Experience</span>
        <span class="profile-val">{experience} year(s)</span>
      </div>
      <div class="profile-row">
        <span class="profile-key">Consultation Fee</span>
        <span class="profile-val">&#x20B9;{fee:.0f}</span>
      </div>
      {bio_html}
    </div>
    <a href="{login_url}" class="cta-btn">&#x1F510; Login to IPCMS Portal &rarr;</a>
    <div class="warning-box">
      <p>
        &#x26A0;&#xFE0F; <strong>Important Security Notice:</strong><br/>
        This is a <strong>temporary password</strong>. You are strongly advised to change it
        immediately after your first login. Do not share your credentials with anyone.
        If you did not expect this email, please contact your system administrator.
      </p>
    </div>
    <div class="section-title">&#x1F680; Getting Started</div>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <div class="step-text"><strong>Visit the login portal</strong> using the URL above and sign in with your email and temporary password.</div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-text"><strong>Update your password</strong> from your profile settings immediately after login.</div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-text"><strong>Complete your profile</strong> by adding your availability schedule and bio.</div>
      </div>
      <div class="step">
        <div class="step-num">4</div>
        <div class="step-text"><strong>Start accepting patients</strong> &mdash; review appointments and manage your schedule.</div>
      </div>
    </div>
    <hr class="divider"/>
    <p style="font-size:13px; color:#64748b; line-height:1.7;">
      If you have any questions or trouble logging in, please contact the admin:
      <strong style="color:#0ea5e9;">{admin_name}</strong> or your IT support team.
    </p>
  </div>
  <div class="footer">
    <div class="logo-text">&#x1F3E5; IPCMS</div>
    <p>
      <strong>Integrated Patient Care Management System</strong><br/>
      This email was sent automatically on behalf of <strong>{admin_name}</strong>.<br/>
      &copy; {year} IPCMS. All rights reserved. &middot; Do not reply to this email.
    </p>
  </div>
</div>
</body>
</html>"""


def send_doctor_credentials_email(
    doctor_email: str,
    doctor_name: str,
    temp_password: str,
    specialty: str = "General Medicine",
    experience: int = 0,
    fee: float = 0.0,
    bio: str = "",
    login_url: str = "http://localhost:8501",
    admin_name: str = "Admin",
) -> tuple:
    """
    Send login credentials email to a newly created doctor.

    Returns:
        (True, "success message") on success
        (False, "error description") on failure
    """
    cfg = _get_smtp_config()

    if not cfg["user"] or not cfg["password"]:
        return False, (
            "SMTP credentials not configured. "
            "Please set SMTP_USER and SMTP_PASSWORD in your .env file."
        )

    # Build MIME message with RFC compliant headers
    msg = MIMEMultipart("alternative")
    subject_str = f"Your Doctor Account Credentials - IPCMS | Dr. {doctor_name}"
    msg["Subject"] = Header(subject_str, "utf-8")
    msg["From"] = f"{cfg['from_name']} <{cfg['user']}>"
    msg["To"] = doctor_email
    msg["Reply-To"] = cfg["user"]
    msg["Date"] = formatdate(localtime=True)
    domain_part = cfg["user"].split("@")[-1] if "@" in cfg["user"] else "localhost"
    msg["Message-ID"] = make_msgid(domain=domain_part)

    # Plain-text fallback
    plain_text = (
        f"Welcome to IPCMS, Dr. {doctor_name}!\n\n"
        f"Your doctor account has been created by {admin_name}.\n\n"
        f"LOGIN CREDENTIALS\n"
        f"-----------------\n"
        f"Email:     {doctor_email}\n"
        f"Password:  {temp_password}\n"
        f"Portal:    {login_url}\n\n"
        f"PROFILE DETAILS\n"
        f"---------------\n"
        f"Name:       Dr. {doctor_name}\n"
        f"Specialty:  {specialty}\n"
        f"Experience: {experience} year(s)\n"
        f"Fee:        Rs.{fee:.0f}\n\n"
        f"IMPORTANT: Please change your password immediately after your first login.\n\n"
        f"If you have any questions, contact the system admin.\n\n"
        f"-- IPCMS Team"
    )

    html_body = _build_doctor_welcome_html(
        doctor_name=doctor_name,
        email=doctor_email,
        temp_password=temp_password,
        specialty=specialty,
        experience=experience,
        fee=fee,
        bio=bio,
        login_url=login_url,
        admin_name=admin_name,
    )

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["user"], doctor_email, msg.as_string())
        return True, f"Credentials email sent successfully to {doctor_email}"
    except smtplib.SMTPAuthenticationError:
        return False, (
            "SMTP Authentication failed. "
            "For Gmail, use an App Password (not your regular password). "
            "See: https://myaccount.google.com/apppasswords"
        )
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except OSError:
        return False, "Connection timed out. Check your SMTP_HOST and SMTP_PORT in .env."
    except Exception as e:
        return False, f"Email sending failed: {str(e)}"
