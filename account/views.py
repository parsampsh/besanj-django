from django.http import JsonResponse
from .models import User, Profile
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST


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
    profile_obj.api_token = get_random_string(70)
    profile_obj.user = new_user
    profile_obj.save()

    return JsonResponse({
        "message": "You registered successfully!",
        "api_token": new_user.profile.api_token
    }, status=201)


def get_token(request):
    """ Returns token of the user by checking username and password (same as login) """
    return JsonResponse({"Hello": "get_token"})


def whoami(request):
    """ Returns the user information by the token """
    return JsonResponse({"Hello": "whoami"})


def reset_token(request):
    """ Resets the token of the user """
    return JsonResponse({"Hello": "reset_token"})


def reset_password(request):
    """ Resets the user's password (same as forget password) """
    return JsonResponse({"Hello": "reset_password"})
