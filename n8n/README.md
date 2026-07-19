# LegalFlow AI — Local n8n Setup & Workflow Configuration Guide

This guide explains how to set up, launch, and configure **n8n** locally for LegalFlow AI workflow automations (payment reminders, overdue lease monitoring, notice PDF dispatch, and payment gateway webhook handling).

---

## 1. Local Setup Options

### Option A: Via Docker Compose (Recommended)

n8n is included in the main `docker-compose.yml` service specification:

```yaml
n8n:
  image: docker.n8n.io/n8nio/n8n
  container_name: legalflow-n8n
  restart: always
  ports:
    - "5678:5678"
  environment:
    - N8N_BASIC_AUTH_ACTIVE=true
    - N8N_BASIC_AUTH_USER=admin
    - N8N_BASIC_AUTH_PASSWORD=admin
    - N8N_ENCRYPTION_KEY=n8n_encryption_secret_key_2026
  volumes:
    - n8n_data:/home/node/.n8n
```

Launch all services:
```bash
docker-compose up -d n8n
```

Once running, access the n8n Web Console at:
**`http://localhost:5678`**

Login Credentials:
- **Username**: `admin`
- **Password**: `admin`

---

### Option B: Standalone Local Setup via npm

If you prefer to run n8n directly on your Mac without Docker:

1. Install Node.js (v18 or v20).
2. Install n8n globally:
   ```bash
   npm install n8n -g
   ```
3. Start n8n:
   ```bash
   n8n start
   ```

---

## 2. Configured Workflow Architectures

LegalFlow AI utilizes three core n8n automation workflows:

### Workflow 1: Daily Overdue Rent Monitoring (`n8n/workflows/overdue_checker.json`)
- **Trigger**: Cron Trigger (Daily at 08:00 AM)
- **Action**: Sends HTTP POST request to Backend `/api/v1/payments/check-overdue`
- **Effect**: Updates payment statuses, compiles financial facts, and initializes compliance cases for overdue accounts.

### Workflow 2: Payment Reminder Dispatch (`n8n/workflows/reminder_dispatcher.json`)
- **Trigger**: Webhook from Backend when a payment is 3 days overdue
- **Action**: Renders HTML Payment Reminder email template
- **Destination**: Sends email to Tenant with embedded PayHere payment checkout link.

### Workflow 3: Notice to Quit PDF & Landlord Alert (`n8n/workflows/notice_workflow.json`)
- **Trigger**: Webhook when Landlord approves Notice to Quit in Dashboard (`/api/v1/documents/{id}/approve`)
- **Action**: Converts Notice markdown into PDF format & notifies Landlord via Email/WhatsApp.

---

## 3. Importing Workflows into n8n

1. Open `http://localhost:5678` in your browser.
2. Click **Workflows** -> **Import from File**.
3. Select any `.json` file from `n8n/workflows/`.
4. Update the HTTP Request node URLs to point to `http://backend:8000` (or `http://localhost:8005` if running outside Docker).
5. Click **Activate Workflow**.
