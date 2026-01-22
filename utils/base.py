from kavenegar import KavenegarAPI


def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('Your API KEY')
        params = {
            'sender': 'SENDER',
            'receptor': f"{phone_number}",
            'message': f"Your code: {code}"
        }
        api.sms_send(params)
    except:
        print('\nSomething went wrong...\n')


INVALID_NAMES = [
    'username', 'email', 'first_name', 'last_name', 'password', 'confirm_password',
    'register', 'login', 'logout', 'signup', 'signin', 'signout', 'auth', 'users',
    'delete', 'edit', 'change', 'remove',
]