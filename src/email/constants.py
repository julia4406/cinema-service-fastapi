ACTIVATION_EMAIL_SUBJECT = "Activation email"
ACTIVATION_EMAIL_BODY = (
    "Hello!\n\n"
    "Thank you for registering. To activate your account, "
    "please follow this link: {activation_url}\n\n"
    "The link is valid for 24 hours. If you did not register, please ignore this email."
)

RESET_PASSWORD_SUBJECT = "Password Reset Request"
RESET_PASSWORD_BODY = (
    "Hello!\n\n"
    "We received a request to reset your password. To proceed, "
    "please follow this link: {reset_url}\n\n"
    "The link is valid for 1 hour. If you did not request a password reset, please ignore this email."
)

PAYMENT_CONFIRMATION_SUBJECT = "Payment Confirmation"
PAYMENT_CONFIRMATION_BODY = "Hello!\n\nYour order #{order_id} has been successfully paid."

PAYMENT_CANCELLATION_SUBJECT = "Payment Cancellation"
PAYMENT_CANCELLATION_BODY = "Hello!\n\nYour order #{order_id} has been cancelled."
