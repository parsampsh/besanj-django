from django.http import JsonResponse
from .models import User, Profile
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_POST


def _handle_auth_token(request):
    """ Gets a request object and checks auth token in the headers
    If token stuff are ok and user is logged in, output is like this:
    (True, <User object>)
    Else:
    (False, <JsonResponse 401>)
    """
    token = request.META.get('HTTP_TOKEN')

    if token is None:
        return False, JsonResponse({'error': "You are not authenticated"}, 401)

    # search for user with this token
    try:
        user = User.objects.filter(profile__api_token=token).first()
        return True, user
    except:
        return False, JsonResponse({'error': "Wrong token"}, 401)

@require_POST
def register(request):
    """ Registers a new User """
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    if None in (username, email, password):
        return JsonResponse({'error': "Please fill out all the fields"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': "This username already exists"}, status=409)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': "This email already exists"}, status=409)

    new_user = User(username=username, email=email, password=make_password(password))
    new_user.save()
    profile_obj = Profile()
    profile_obj.api_token = Profile.generate_unique_token() # TODO : handle unique token
    profile_obj.user = new_user
    profile_obj.save()

    return JsonResponse({
        "message": "You registered successfully!",
        "api_token": new_user.profile.api_token
    }, status=201)


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


def whoami(request):
    """ Returns the user information by the token """
    return JsonResponse({"Hello": "whoami"})


def reset_token(request):
    """ Resets the token of the user """
    return JsonResponse({"Hello": "reset_token"})


def reset_password(request):
    """ Resets the user's password (same as forget password) """
    return JsonResponse({"Hello": "reset_password"})
