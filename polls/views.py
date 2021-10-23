from django.http import JsonResponse
from account.views import require_token


@require_token
def create(request, user):
    return JsonResponse({})


@require_token
def choice(request, user):
    return JsonResponse({})


def index(request):
    return JsonResponse({})
