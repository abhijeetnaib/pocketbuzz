"""
POS Report Parser
Extracts customer data from PDF reports and email bodies.
"""
import re
import io
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


@dataclass
class CustomerRecord:
    """Represents a single customer transaction."""
    phone: str
    name: Optional[str]
    items: Optional[str]
    bill_amount: Optional[float]
    source: str


def parse_pos_email(
    pdf_content: Optional[io.BytesIO],
    email_body: str,
    source: str = "Dine-In"
) -> List[Dict[str, Any]]:
    """
    Parse POS report from PDF attachment or email body.
    
    Args:
        pdf_content: PDF file as BytesIO, or None
        email_body: Email text/html body
        source: Default source label
        
    Returns:
        List of customer records ready for database insertion
    """
    records = []
    
    # Try PDF first
    if pdf_content and pdfplumber:
        records = _parse_pdf(pdf_content, source)
    
    # Fall back to email body parsing
    if not records and email_body:
        records = _parse_email_body(email_body, source)
    
    # Filter out invalid records
    valid_records = [r for r in records if _is_valid_record(r)]
    
    return valid_records


def _parse_pdf(pdf_content: io.BytesIO, source: str) -> List[Dict[str, Any]]:
    """Extract records from PDF using pdfplumber."""
    records = []
    
    try:
        with pdfplumber.open(pdf_content) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                records.extend(_extract_records_from_text(text, source))
                
                # Also try tables
                tables = page.extract_tables() or []
                for table in tables:
                    records.extend(_extract_records_from_table(table, source))
    except Exception as e:
        print(f"PDF parsing error: {e}")
    
    return records


def _parse_email_body(email_body: str, source: str) -> List[Dict[str, Any]]:
    """Extract records from email text."""
    return _extract_records_from_text(email_body, source)


def _extract_records_from_text(text: str, source: str) -> List[Dict[str, Any]]:
    """
    Extract customer records from plain text.
    Looks for patterns like phone numbers and associated data.
    """
    records = []
    
    # Pattern for Indian phone numbers (10 digits, may start with +91)
    phone_pattern = r'(?:\+91[-\s]?)?([6-9]\d{9})'
    
    # Find all phone numbers
    phones = re.findall(phone_pattern, text)
    
    for phone in phones:
        # Determine source from context
        record_source = _detect_source(text, phone, source)
        
        # Skip aggregator numbers
        if record_source in ["Zomato", "Swiggy", "UberEats"]:
            continue
        
        # Try to find name near phone number
        name = _extract_name_near_phone(text, phone)
        
        # Try to find bill amount
        amount = _extract_amount_near_phone(text, phone)
        
        records.append({
            "phone": phone,
            "name": name,
            "items": None,  # Would need more context
            "bill_amount": amount,
            "source": record_source
        })
    
    return records


def _extract_records_from_table(table: List[List], source: str) -> List[Dict[str, Any]]:
    """Extract records from a structured table."""
    records = []
    
    if not table or len(table) < 2:
        return records
    
    # Try to find header row and map columns
    headers = [str(h).lower() if h else "" for h in table[0]]
    
    phone_col = None
    name_col = None
    amount_col = None
    source_col = None
    
    for i, header in enumerate(headers):
        if any(x in header for x in ["phone", "mobile", "contact"]):
            phone_col = i
        elif any(x in header for x in ["name", "customer"]):
            name_col = i
        elif any(x in header for x in ["amount", "bill", "total"]):
            amount_col = i
        elif any(x in header for x in ["source", "type", "channel"]):
            source_col = i
    
    if phone_col is None:
        return records
    
    # Process data rows
    for row in table[1:]:
        if not row or len(row) <= phone_col:
            continue
        
        phone = _clean_phone(str(row[phone_col]) if row[phone_col] else "")
        if not phone:
            continue
        
        record_source = source
        if source_col and len(row) > source_col and row[source_col]:
            record_source = str(row[source_col])
        
        # Skip aggregator records
        if record_source.lower() in ["zomato", "swiggy", "ubereats"]:
            continue
        
        name = str(row[name_col]) if name_col and len(row) > name_col and row[name_col] else None
        amount = _parse_amount(row[amount_col]) if amount_col and len(row) > amount_col else None
        
        records.append({
            "phone": phone,
            "name": name,
            "items": None,
            "bill_amount": amount,
            "source": record_source
        })
    
    return records


def _detect_source(text: str, phone: str, default: str) -> str:
    """Detect if a record is from an aggregator based on context."""
    # Check for aggregator keywords near the phone number
    context_start = text.find(phone)
    if context_start == -1:
        return default
    
    context = text[max(0, context_start - 100):context_start + 100].lower()
    
    if "zomato" in context:
        return "Zomato"
    if "swiggy" in context:
        return "Swiggy"
    if "uber" in context or "ubereats" in context:
        return "UberEats"
    
    return default


def _extract_name_near_phone(text: str, phone: str) -> Optional[str]:
    """Try to extract a customer name near the phone number."""
    # Look for common patterns like "Name: John Doe" near phone
    patterns = [
        r'(?:name|customer)[:\s]+([A-Za-z\s]{2,30})',
        r'([A-Z][a-z]+ [A-Z][a-z]+)\s*[-:]\s*' + phone,
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def _extract_amount_near_phone(text: str, phone: str) -> Optional[float]:
    """Try to extract bill amount near the phone number."""
    context_start = text.find(phone)
    if context_start == -1:
        return None
    
    context = text[context_start:context_start + 200]
    
    # Look for rupee amounts
    amount_pattern = r'(?:Rs\.?|₹|INR)\s*([0-9,]+(?:\.[0-9]+)?)'
    match = re.search(amount_pattern, context)
    if match:
        return _parse_amount(match.group(1))
    
    return None


def _clean_phone(phone: str) -> str:
    """Clean and validate phone number."""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Remove country code if present
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    
    # Validate: must be 10 digits starting with 6-9
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    
    return ""


def _parse_amount(value: Any) -> Optional[float]:
    """Parse amount from various formats."""
    if value is None:
        return None
    
    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[₹Rs,\s]', '', str(value))
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _is_valid_record(record: Dict[str, Any]) -> bool:
    """
    Validate a record according to the filter logic.
    
    Critical logic:
    - Skip Zomato/Swiggy/UberEats (masked numbers are useless)
    - Phone must be 10 digits
    """
    source = record.get("source", "").lower()
    
    # Filter out aggregators
    if source in ["zomato", "swiggy", "ubereats"]:
        return False
    
    # Validate phone
    phone = record.get("phone", "")
    if len(phone) != 10 or not phone.isdigit():
        return False
    
    return True
