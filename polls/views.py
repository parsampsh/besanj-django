from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.views import require_token


@require_token
@require_POST
def create(request, user):
    return JsonResponse({})


@require_token
@require_POST
def update(request, user):
    return JsonResponse({})


@require_token
@require_POST
def delete(request, user):
    return JsonResponse({})


@require_token
@require_POST
def create_choice(request, user):
    return JsonResponse({})


@require_token
@require_POST
def update_choice(request, user):
    return JsonResponse({})


@require_token
@require_POST
def delete_choice(request, user):
    return JsonResponse({})


@require_token
@require_POST
def choice(request, user):
    return JsonResponse({})


def index(request):
    return JsonResponse({})
