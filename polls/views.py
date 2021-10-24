from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.views import require_token
from .models import *


@require_token
@require_POST
def create(request, user):
    title = request.POST.get('title')
    description = request.POST.get('description')
    choices = request.POST.get('choices')

    if title is None:
        return JsonResponse({"error": "Field title is required"}, status=400)

    if choices is None:
        return JsonResponse({"error": "Field choices is required"}, status=400)

    choices = [item.strip() for item in choices.strip().splitlines() if item.strip() != '']

    if len(choices) == 0:
        return JsonResponse({"error": "Field choices is required"}, status=400)

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

    sort_counter = 0
    for choice in choices:
        poll.choice_set.create(title=choice, sort=sort_counter)
        sort_counter += 1

    return JsonResponse({'created_poll_id': poll.id}, status=201)


@require_token
@require_POST
def delete(request, user):
    poll_id = request.POST.get('poll_id')

    try:
        poll = Poll.objects.get(pk=poll_id)
    except:
        return JsonResponse({'error': 'Invalid poll_id'}, status=404)

    if poll.user.id != user.id:
        return JsonResponse({'error': 'You cannot delete this poll'}, status=403)

    poll.delete()

    return JsonResponse({'message': 'Poll was deleted'})


@require_token
@require_POST
def choice(request, user):
    return JsonResponse({})


def index(request):
    return JsonResponse({})
