import unittest
import uuid

from src.app.config.types import Department
from src.app.utils.validators.validators import Validators


class TestValidators(unittest.TestCase):
    def test_is_name_valid(self):
        """
        Test name validation
        """
        # Valid names
        valid_names = [
            "John",
            "Sarah",
            "Alex",
            "Alexander"
        ]

        # Invalid names
        invalid_names = [
            "A",  # Too short
            "ThisNameIsTooLongToBeValid",  # Too long
            "",  # Empty string
            "  "  # Whitespace
        ]

        # Test valid names
        for name in valid_names:
            self.assertTrue(Validators.is_name_valid(name), f"Failed for valid name: {name}")

        # Test invalid names
        for name in invalid_names:
            self.assertFalse(Validators.is_name_valid(name), f"Failed for invalid name: {name}")

    def test_is_email_valid(self):
        """
        Test email validation
        """
        # Valid emails
        valid_emails = [
            "john.doe@watchguard.com",
            "jane_smith@watchguard.com",
            "user123@watchguard.com"
        ]

        # Invalid emails
        invalid_emails = [
            "john@gmail.com",  # Wrong domain
            "john@watchguard.co.uk",  # Incorrect domain
            "john@WATCHGUARD.COM",  # Case sensitivity check
            "john@",  # Incomplete email
            "@watchguard.com",  # No username
            "john.doe@watchguard",  # Missing top-level domain
            ""  # Empty string
        ]

        # Test valid emails
        for email in valid_emails:
            self.assertTrue(Validators.is_email_valid(email), f"Failed for valid email: {email}")

        # Test invalid emails
        for email in invalid_emails:
            self.assertFalse(Validators.is_email_valid(email), f"Failed for invalid email: {email}")

    def test_is_password_valid(self):
        """
        Test password validation
        """
        # Valid passwords
        valid_passwords = [
            "Pass@word1",
            "Secure!123",
            "Complex#456",
            "Valid_Pass2"
        ]

        # Invalid passwords
        invalid_passwords = [
            "short",  # Too short
            "ALLUPPERCASE",  # No lowercase
            "alllowercase",  # No uppercase
            "NoSpecialChar1",  # No special character
            "longpasswordwithnouppercaselowerspecial",  # Missing requirements
            "T!",  # Too short
            "TooLongPasswordWithNoSpecialCharOrNumbers" * 2,  # Too long
            "",  # Empty string
            "Pass word"  # No special character
        ]

        # Test valid passwords
        for password in valid_passwords:
            self.assertTrue(Validators.is_password_valid(password), f"Failed for valid password: {password}")

        # Test invalid passwords
        for password in invalid_passwords:
            self.assertFalse(Validators.is_password_valid(password), f"Failed for invalid password: {password}")

    def test_is_valid_UUID(self):
        """
        Test UUID validation
        """
        # Generate some valid UUIDs
        valid_uuids = [
            str(uuid.uuid4()),
            str(uuid.uuid4())
        ]

        # Invalid UUIDs
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "",
            "uuid.uuid4()",  # String representation of function call
            "ffffffff-ffff-ffff-ffff-fffffffffff"  # Invalid UUID format
        ]

        # Test valid UUIDs
        for uid in valid_uuids:
            self.assertTrue(Validators.is_valid_UUID(uid), f"Failed for valid UUID: {uid}")

        # Test invalid UUIDs
        for uid in invalid_uuids:
            self.assertFalse(Validators.is_valid_UUID(uid), f"Failed for invalid UUID: {uid}")

    def test_is_department_valid(self):
        """
        Test department validation
        """
        # Valid departments (using the enum values)
        valid_departments = [
            dept.value for dept in Department
        ]

        # Invalid departments
        invalid_departments = [
            "NON_EXISTING_DEPARTMENT",
            "",
            None,
            "random_string",
            123  # Non-string input
        ]

        # Test valid departments
        for dept in valid_departments:
            self.assertTrue(Validators.is_department_valid(dept), f"Failed for valid department: {dept}")

        # Test invalid departments
        for dept in invalid_departments:
            self.assertFalse(Validators.is_department_valid(dept), f"Failed for invalid department: {dept}")
