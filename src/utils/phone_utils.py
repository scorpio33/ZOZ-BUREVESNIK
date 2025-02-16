class PhoneUtils:
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        import re
        pattern = r'^\+7\d{10}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number to readable format"""
        if not PhoneUtils.validate_phone(phone):
            return phone
            
        # Format: +7 (XXX) XXX-XX-XX
        return f"+7 ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:]}"
