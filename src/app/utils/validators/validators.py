import re
import uuid

from src.app.config.types import Department


class Validators:

    @staticmethod
    def is_name_valid(name: str) -> bool:
        """
        Validate if the given name is valid (2 < len < 16).
        :param name:
        :return:
        """
        return 2 < len(name) < 16

    @staticmethod
    def is_email_valid(email: str) -> bool:
        """
        Validate if the given email is a valid watchguard account.
        :param email:
        :return:
        """
        gmail_regex = r"^[a-zA-Z0-9._%+-]+@watchguard\.com$"
        return bool(re.match(gmail_regex, email))

    @staticmethod
    def is_password_valid(password: str) -> bool:
        """
        Validate if the given password meets the required criteria:
        - Length between 8 and 16 characters
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one special character
        """
        if not (8 <= len(password) <= 16):
            return False

        upper_case = False
        lower_case = False
        special_char = False

        # Define a set of special characters
        special_characters = set("!@#$%^&*()-_=+[]{}|;:',.<>?/")

        for char in password:
            if char.isupper():
                upper_case = True
            elif char.islower():
                lower_case = True
            elif char in special_characters:
                special_char = True

        return upper_case and lower_case and special_char

    @staticmethod
    def is_valid_UUID(id: str) -> bool:
        """
        Checks if the given string is a valid UUID.

        Args:
            id (str): The string to check.

        Returns:
            bool: True if the string is a valid UUID, False otherwise.
        """
        try:
            # Attempt to create a UUID object
            uuid_obj = uuid.UUID(id)
            # Check if the input string matches the generated UUID's string format
            return str(uuid_obj) == id
        except ValueError:
            # If a ValueError is raised, the string is not a valid UUID
            return False

    @staticmethod
    def is_department_valid(department) -> bool:
        """
        Checks if the provided department is valid
        """
        for dept in Department:
            if department == dept.value:
                return True

        return False
