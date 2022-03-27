import datetime
import string
import random
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import User, Profile, ResetPasswordRequest
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_POST
from besanj_backend.json_request_decorator import json_request


def _handle_auth_token(request):
    """ Gets a request object and checks auth token in the headers (or you can pass the token as string instead)
    If token stuff are ok and user is logged in, output is like this:
    (True, <User object>)
    Else:
    (False, <JsonResponse 401>)
    """
    if type(request) is str:
        token = request
    else:
        token = request.META.get('HTTP_TOKEN')

    if token is None:
        return False, JsonResponse({'error': "You are not authenticated"}, status=401)

    # search for user with this token
    user = User.objects.filter(profile__api_token=token).first()
    if user is None:
        return False, JsonResponse({'error': "Wrong token"}, status=401)
    return True, user


def require_token(func):
    """ A decorator for views they want to require auth using token
    You should set a second argument as User object
    The authenticated user using the token will be passed as that argument
    """
    def decorated_function(request):
        auth_result, user = _handle_auth_token(request)
        if not auth_result:
            return user

        return func(request, user)
    return decorated_function

@json_request
@require_POST
def register(request):
    """ Registers a new User """
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if None in (username, email, password):
        return JsonResponse({'error': "Please fill out all the fields"}, status=400)

    if len(username) > 255:
        return JsonResponse({'error': "Maximum length for field username is 255"}, status=400)

    if len(email) > 255:
        return JsonResponse({'error': "Maximum length for field email is 255"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': "This username already exists"}, status=409)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': "This email already exists"}, status=409)

    new_user = User(username=username, email=email, password=make_password(password))
    new_user.save()
    profile_obj = Profile()
    profile_obj.api_token = Profile.generate_unique_token()
    profile_obj.user = new_user
    profile_obj.save()

    return JsonResponse({
        "message": "You registered successfully!",
        "api_token": new_user.profile.api_token
    }, status=201)


@json_request
@require_POST
def get_token(request):
    """ Returns token of the user by checking username and password (same as login) """
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if password is None or username is None and email is None:
        return JsonResponse({'error': "Please fill out password and email(or username) fields"}, status=400)

    if email is not None:
        user = User.objects.filter(email=email).first()
    else:
        user = User.objects.filter(username=username).first()

    if user is None:
        return JsonResponse({'error': "Wrong information"}, status=401)

    if not check_password(password, user.password):
        return JsonResponse({'error': "Wrong information"}, status=401)

    return JsonResponse({"token": user.profile.api_token})


@require_token
def whoami(request, user):
    """ Returns the user information by the token """
    return JsonResponse({
        "user": user.profile.to_json()
    })


@json_request
@require_POST
@require_token
def reset_token(request, user):
    """ Resets the token of the user """
    user.profile.api_token = Profile.generate_unique_token()
    user.profile.save()

    return JsonResponse({"new_token": user.profile.api_token})


@json_request
@require_POST
def reset_password(request):
    """ Makes a request for user password to be reset """
    if request.POST.get('username') != None:
        user = User.objects.filter(username=request.POST.get('username')).first()
    elif request.POST.get('email') != None:
        user = User.objects.filter(email=request.POST.get('email')).first()
    else:
        return JsonResponse({'error': "Please send username or email"}, status=400)

    if user is None:
        return JsonResponse({'error': "User not found"}, status=404)

    old_req = ResetPasswordRequest.objects.filter(user=user)
    make_new_request = True
    if old_req.exists():
        old_req = old_req.first()
        if old_req.expires_at > datetime.datetime.now(datetime.timezone.utc):
            # request is already made, don't make new one
            make_new_request = False
            reset_pass_req = old_req
        else:
            # the old request is expired, delete it
            old_req.delete()

    if make_new_request:
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
        generated_code = ''.join(random.choice(string.ascii_letters*10) for _ in range(0, 100))
        reset_pass_req = ResetPasswordRequest.objects.create(user=user, expires_at=expires_at, code=generated_code)

    # send mail to the user
    send_mail(
        subject='Besanj - Reset Password',
        message='You requested to reset password of your account in Besanj. here is the link that you can reset your password using it: http://localhost/reset-password/' + reset_pass_req.code, # TODO : change the link in message to what it should be after making it in frontend
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[reset_pass_req.user.email]
    )

    return JsonResponse({'message': 'Password reset link has been sent to your email'})


@json_request
@require_POST
def reset_password_final(request):
    """ Final password reset """
    if request.POST.get('code'):
        code = request.POST.get('code')
        req = ResetPasswordRequest.objects.filter(code=code)

        if not req.exists():
            return JsonResponse({'error': "Invalid code"}, status=404)

        req = req.first()
        if req.expires_at < datetime.datetime.now(datetime.timezone.utc):
            return JsonResponse({'error': "The code is expired"}, status=403)
    else:
        return JsonResponse({'error': "Please send reset password code"}, status=400)

    if request.POST.get('new_password'):
        password = request.POST.get('new_password')

        user = req.user
        user.password = make_password(password)
        user.save()
        return JsonResponse({"message": "Password has been changed"}, status=200)
    else:
        return JsonResponse({"message": "The code is valid"}, status=200)

