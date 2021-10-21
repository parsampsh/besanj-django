from django.http import JsonResponse


def register(request):
    """ Registers a new User """
    return JsonResponse({"Hello": "register"})


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
