from django.core.mail import send_mail

def send_activation_code(email, activation_code):
    activation_url = f'http://localhost:8000/v1/api/account/activate/{activation_code}'
    message = f"""
        Спасибо за регистрацию..
        Пожалуйста, активируйте свою учетную запись.
        Activation link: {activation_url}
    """
    send_mail(
    'Активируйте свой аккаунт',
    message,
    'test@test.com',
    [email, ],
    fail_silently=False
    )

