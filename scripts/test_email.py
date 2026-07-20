import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.services.email_service import send_tenant_onboarding_email

if __name__ == "__main__":
    target_email = sys.argv[1] if len(sys.argv) > 1 else "akilafernando196@gmail.com"
    print(f"Testing LegalFlow AI Email Delivery to: {target_email}")
    print(f"SMTP Host: {settings.SMTP_HOST or 'Not Configured (Simulation Mode)'}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"SMTP User: {settings.SMTP_USER or 'Not Configured'}")
    
    success = send_tenant_onboarding_email(
        tenant_name="Test Commercial Tenant",
        tenant_email=target_email,
        temp_password="TenantPass_Test123!",
        company="Test Business Ltd"
    )
    
    if success:
        print("\n✅ Email process completed successfully!")
    else:
        print("\n❌ Email delivery failed. Please check SMTP settings in .env.")
