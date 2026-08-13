from django.contrib.auth import get_user_model
from utils.service_result import ServiceResult


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
            return ServiceResult.fail(
                message="Current password is incorrect.",
                code="INVALID_OLD_PASSWORD"        
            )
        
        if new_password != confirm_password:
            return ServiceResult.fail(
                message= "New passwords do not match.",
                code="PASSWORD_MISMATCH"
            )
            
        
        if old_password == new_password:
            return ServiceResult.fail(
                message="New password must be different from current password.",
                code="PASSWORD_SAME_AS_OLD"
            )
 
        self.user.set_password(new_password)
        self.user.save(update_fields=['password'])

        return ServiceResult.success(
            message="Password changed successfully."
        )
        