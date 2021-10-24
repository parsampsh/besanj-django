from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.views import require_token
from .models import *


@require_token
@require_POST
def create(request, user):
    title = request.POST.get('title')
    description = request.POST.get('description')

    if title is None:
        return JsonResponse({"error": "Field `title` is required"}, status=400)

    if len(title) > 255:
        return JsonResponse({"error": "Maximum length for field title is 255"}, status=400)

    if description is not None:
        if len(description) > 1000:
            return JsonResponse({"error": "Maximum length for field description is 1000"}, status=400)

    poll = Poll()
    poll.user = user
    poll.title = title
    poll.description = description
    poll.save()

    return JsonResponse({'created_poll_id': poll.id}, status=201)


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
