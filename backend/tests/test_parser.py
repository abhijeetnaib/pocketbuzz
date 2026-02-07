"""
Tests for POS Report Parser
"""
import pytest
from app.services.parser import (
    parse_pos_email,
    _clean_phone,
    _is_valid_record,
    _detect_source
)


class TestPhoneCleaning:
    """Test phone number cleaning and validation."""
    
    def test_valid_10_digit_phone(self):
        assert _clean_phone("9876543210") == "9876543210"
    
    def test_phone_with_country_code(self):
        assert _clean_phone("+919876543210") == "9876543210"
        assert _clean_phone("919876543210") == "9876543210"
    
    def test_phone_with_spaces(self):
        assert _clean_phone("98765 43210") == "9876543210"
        assert _clean_phone("987 654 3210") == "9876543210"
    
    def test_phone_with_dashes(self):
        assert _clean_phone("98765-43210") == "9876543210"
    
    def test_invalid_phone_too_short(self):
        assert _clean_phone("98765") == ""
    
    def test_invalid_phone_wrong_start(self):
        # Indian mobiles start with 6-9
        assert _clean_phone("1234567890") == ""
        assert _clean_phone("5234567890") == ""
    
    def test_valid_phone_starting_with_6789(self):
        assert _clean_phone("6123456789") == "6123456789"
        assert _clean_phone("7123456789") == "7123456789"
        assert _clean_phone("8123456789") == "8123456789"
        assert _clean_phone("9123456789") == "9123456789"


class TestRecordValidation:
    """Test record filtering logic."""
    
    def test_valid_dinein_record(self):
        record = {
            "phone": "9876543210",
            "source": "Dine-In",
            "name": "Test Customer"
        }
        assert _is_valid_record(record) is True
    
    def test_filter_zomato_orders(self):
        """Critical: Zomato orders must be filtered (masked numbers)."""
        record = {
            "phone": "9876543210",
            "source": "Zomato",
            "name": "Zomato Customer"
        }
        assert _is_valid_record(record) is False
    
    def test_filter_swiggy_orders(self):
        """Critical: Swiggy orders must be filtered (masked numbers)."""
        record = {
            "phone": "9876543210",
            "source": "Swiggy",
            "name": "Swiggy Customer"
        }
        assert _is_valid_record(record) is False
    
    def test_filter_ubereats_orders(self):
        record = {
            "phone": "9876543210",
            "source": "UberEats",
            "name": "UberEats Customer"
        }
        assert _is_valid_record(record) is False
    
    def test_filter_invalid_phone(self):
        record = {
            "phone": "12345",  # Too short
            "source": "Dine-In",
            "name": "Test"
        }
        assert _is_valid_record(record) is False
    
    def test_case_insensitive_source_filter(self):
        """Sources should be filtered regardless of case."""
        record = {
            "phone": "9876543210",
            "source": "ZOMATO",
            "name": "Test"
        }
        assert _is_valid_record(record) is False


class TestSourceDetection:
    """Test aggregator source detection from context."""
    
    def test_detect_zomato_in_context(self):
        text = "Order from Zomato - Customer 9876543210"
        source = _detect_source(text, "9876543210", "Dine-In")
        assert source == "Zomato"
    
    def test_detect_swiggy_in_context(self):
        text = "Swiggy order delivered to 9876543210"
        source = _detect_source(text, "9876543210", "Dine-In")
        assert source == "Swiggy"
    
    def test_default_source_when_no_aggregator(self):
        text = "Walk-in customer 9876543210 ordered butter chicken"
        source = _detect_source(text, "9876543210", "Dine-In")
        assert source == "Dine-In"


class TestEmailParsing:
    """Test email body parsing."""
    
    def test_parse_simple_email_body(self):
        email_body = """
        Daily Sales Report
        Date: 2026-02-07
        
        Customer: Rahul Sharma
        Phone: 9876543210
        Order: Butter Chicken, Naan
        Amount: Rs. 850
        
        Customer: Priya Singh
        Phone: 8765432109
        Order: Paneer Tikka
        Amount: Rs. 450
        """
        
        records = parse_pos_email(None, email_body, "Dine-In")
        
        # Should find 2 valid phone numbers
        assert len(records) >= 2
        
        # Verify phones are extracted correctly
        phones = [r["phone"] for r in records]
        assert "9876543210" in phones
        assert "8765432109" in phones
    
    def test_filter_aggregator_from_email(self):
        email_body = """
        Sales Report
        
        Dine-In Customer
        Phone: 9876543210
        
        Zomato Order
        Phone: 8765432109
        """
        
        records = parse_pos_email(None, email_body, "Dine-In")
        
        # Should only have 1 record (Zomato filtered)
        phones = [r["phone"] for r in records]
        assert "9876543210" in phones
        # Zomato order should be filtered
        assert "8765432109" not in phones
    
    def test_empty_email_returns_empty_list(self):
        records = parse_pos_email(None, "", "Dine-In")
        assert records == []
    
    def test_no_phones_returns_empty_list(self):
        email_body = "No phone numbers in this email body"
        records = parse_pos_email(None, email_body, "Dine-In")
        assert records == []


class TestPhoneFormatInOutput:
    """Test that output phone numbers are properly formatted."""
    
    def test_phone_in_output_is_10_digits(self):
        email_body = "Customer phone: +91-98765-43210"
        records = parse_pos_email(None, email_body, "Dine-In")
        
        if records:
            # All phones should be 10 digits (country code stripped)
            for record in records:
                assert len(record["phone"]) == 10
                assert record["phone"].isdigit()
