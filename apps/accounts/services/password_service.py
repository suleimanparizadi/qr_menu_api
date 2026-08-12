from django.contrib.auth import get_user_model

User = get_user_model()


class ChangePasswordService:
    """
    Change password for authenticated users.
    User must provide old password for security.
    """
    
    def __init__(self, user):

        self.user = user
    
    def change_password(self, old_password, new_password, confirm_password):

        """
        Change password after validating old password.
        """

        
        if not self.user.check_password(old_password):
            return False, "Current password is incorrect."
        
        if new_password != confirm_password:
            return False, "New passwords do not match."
        
        if old_password == new_password:
            return False, "New password must be different from current password."
        
        self.user.set_password(new_password)
        self.user.save(update_fields=['password'])
        
        return True, "Password changed successfully."