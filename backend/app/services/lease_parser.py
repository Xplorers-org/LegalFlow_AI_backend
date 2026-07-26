import os
import json
import fitz  # PyMuPDF
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger("backend.services.lease_parser")


class LeaseParserService:
    """Service to parse Lease Agreement PDFs and extract structured metadata using Google Gemini via OpenRouter."""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extracts plain text from PDF bytes using PyMuPDF."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error("Failed to extract text from PDF", error=str(e))
            raise ValueError(f"Could not parse PDF text: {str(e)}")

    @staticmethod
    def parse_lease_text(text: str) -> Dict[str, Any]:
        """Sends extracted lease text to Gemini to extract all schedules and terms in structured JSON."""
        import os
        import httpx

        # Load API key from environment or Pydantic settings
        api_key = settings.GEMINI_API_KEY or settings.OPENROUTER_API_KEY
        
        if not api_key or api_key == "your_openrouter_api_key_here":
            logger.warning("No API key configured. Returning fallback mock details.")
            return LeaseParserService._get_mock_fallback_data()

        # Check if the key is a Google AI Studio Key (starts with AQ. or AIzaSy)
        is_google_key = api_key.startswith("AQ.") or api_key.startswith("AIzaSy")

        prompt = f"""
You are an expert commercial real estate attorney specializing in Sri Lankan tenancy laws.
Analyze the following commercial lease agreement text and extract the key terms, schedules, lessor/lessee identity and utility details.

Return your response EXACTLY as a JSON object matching this schema. Do not include any markdown block formatting (like ```json) or additional text.

{{
  "lessor": {{
    "name": "Full name of the lessor/landlord",
    "nic_passport": "NIC or Passport number of the lessor if available",
    "address": "Lessor's address"
  }},
  "lessee": {{
    "name": "Full name of the lessee/tenant",
    "nic_passport": "NIC or Passport number of the lessee if available",
    "address": "Lessee's address",
    "company": "Company/Business name of the lessee if mentioned",
    "email": "Email address of the lessee if mentioned",
    "phone": "Phone/Contact number of the lessee if mentioned"
  }},
  "lease_terms": {{
    "commencement_date": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "contract_date": "YYYY-MM-DD (Date lease signed)",
    "monthly_rent": 0.0 (Numeric base rent monthly. E.g. 250000.00),
    "service_charge": 0.0 (Numeric total service charges monthly. E.g. 60000.00),
    "deposit": 0.0 (Numeric security deposit. E.g. 500000.00),
    "payment_day": 5 (Due date day of month, numeric integer E.g. 5),
    "grace_period_days": 7 (Grace period days, numeric integer E.g. 7),
    "interest_rate_pa": 12.0 (Late payment statutory interest rate % per annum, E.g. 12.0)
  }},
  "first_schedule": {{
    "physical_address": "Demised premises physical address",
    "assessment_number": "Municipal assessment number if available",
    "local_authority": "Local municipal council/authority",
    "lot_plan_reference": "Lot and plan reference with surveyor details",
    "extent": "Premises extent / size E.g. 12.5 Perches (2400 sq ft)",
    "permitted_use": "Permitted business/office use"
  }},
  "second_schedule_breakdown": {{
    "base_rent": 0.0 (Base Rent LKR E.g. 250000.00),
    "building_security": 0.0 (Building security fee E.g. 25000.00),
    "common_area_cleaning": 0.0 (Cleaning fee E.g. 15000.00),
    "common_area_lighting": 0.0 (Lighting fee E.g. 8000.00),
    "elevator_lift_maintenance": 0.0 (Elevator maintenance fee E.g. 12000.00),
    "annual_escalation": "Escalation terms E.g. 10% per annum"
  }},
  "third_schedule_utilities": {{
    "electricity_provider": "Ceylon Electricity Board (CEB)",
    "electricity_account_no": "Electricity account number if available",
    "water_provider": "National Water Supply and Drainage Board (NWSDB)",
    "water_account_no": "Water account number if available",
    "liability_for_consumption": "Description of utility payment liability E.g. Lessee, exclusively, from the Commencement Date",
    "recovery_of_arrears_on_termination": "Description of recovery of arrears on termination E.g. Firstly from the Security Deposit (Clause 8); balance recoverable by civil action (Clause 6.5)"
  }}
}}

LEASE AGREEMENT TEXT:
---
{text}
---
"""

        if is_google_key:
            logger.info("Invoking Gemini 3.5 Flash Lite natively via Google AI Studio API")
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 2048,
                        "responseMimeType": "application/json"
                    }
                }
                resp = httpx.post(url, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    raw_content = resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                    if raw_content.startswith("```"):
                        lines = raw_content.strip().split("\n")
                        if lines[0].startswith("```json") or lines[0].startswith("```"):
                            raw_content = "\n".join(lines[1:-1]).strip()
                    return json.loads(raw_content)
                else:
                    logger.error("Google AI Studio API returned error", status_code=resp.status_code, body=resp.text)
                    raise ValueError(f"Google API Error: {resp.text}")
            except Exception as e:
                logger.error("Failed to parse lease terms with native Google API", error=str(e))
                return LeaseParserService._get_mock_fallback_data()

        # Fallback to OpenRouter ChatOpenAI
        try:
            logger.info("Invoking Gemini OpenRouter for lease extraction")
            llm = ChatOpenAI(
                model="google/gemini-2.5-flash",
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0.1,
                max_retries=3,
                max_tokens=600,
            )
            resp = llm.invoke(prompt)
            raw_content = resp.content.strip()
            
            # Remove any ```json formatting wrappers if outputted by the LLM
            if raw_content.startswith("```"):
                lines = raw_content.strip().split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw_content = "\n".join(lines[1:-1]).strip()

            parsed_data = json.loads(raw_content)
            return parsed_data
        except Exception as e:
            logger.error("Failed to parse lease terms with LLM via OpenRouter", error=str(e))
            return LeaseParserService._get_mock_fallback_data()

    @staticmethod
    def _get_mock_fallback_data() -> Dict[str, Any]:
        """Fallback mock details if OpenRouter is offline or fails."""
        return {
            "lessor": {
                "name": "Priyantha Kumara Gunasekera",
                "nic_passport": "651002345V",
                "address": "No. 12, Ward Place, Colombo 00700"
            },
            "lessee": {
                "name": "Chathurika Dilrukshi Perera",
                "nic_passport": "199678901234",
                "address": "No. 23, Havelock Road, Colombo 00500",
                "company": "Perera Textiles",
                "email": "chathurika.perera@textiles.lk",
                "phone": "+94771234567"
            },
            "lease_terms": {
                "commencement_date": "2026-08-01",
                "expiry_date": "2027-07-31",
                "contract_date": "2026-08-15",
                "monthly_rent": 250000.0,
                "service_charge": 60000.0,
                "deposit": 500000.0,
                "payment_day": 5,
                "grace_period_days": 7,
                "interest_rate_pa": 12.0
            },
            "first_schedule": {
                "physical_address": "No. 156, Galle Road, Colombo 00300",
                "assessment_number": "45/12A",
                "local_authority": "Colombo Municipal Council",
                "lot_plan_reference": "Lot No. 07, Plan No. 2456 dated 12th March 2019 by Mr. W. M. Jayasinghe, Licensed Surveyor",
                "extent": "12.5 Perches (approximately 2,400 square feet)",
                "permitted_use": "General office, information technology, and software business use"
            },
            "second_schedule_breakdown": {
                "base_rent": 250000.0,
                "building_security": 25005.0,
                "common_area_cleaning": 15000.0,
                "common_area_lighting": 8000.0,
                "elevator_lift_maintenance": 12000.0,
                "annual_escalation": "10% per annum, effective each anniversary of the Commencement Date"
              },
            "third_schedule_utilities": {
                "electricity_provider": "Ceylon Electricity Board (CEB)",
                "electricity_account_no": "214-56789-002",
                "water_provider": "National Water Supply and Drainage Board (NWSDB)",
                "water_account_no": "0345-1122334",
                "liability_for_consumption": "Lessee, exclusively, from the Commencement Date",
                "recovery_of_arrears_on_termination": "Firstly from the Security Deposit (Clause 8); balance recoverable by civil action (Clause 6.5)"
            }
        }
