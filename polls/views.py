from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.views import require_token
from .models import *


@require_token
@require_POST
def create(request, user):
    """ Creates a new poll """
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
    """ Deletes a poll """
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
    """ Toggles selection of a choice """
    choice_id = request.POST.get('choice_id')
    try:
        choice = Choice.objects.get(pk=choice_id)
    except:
        return JsonResponse({'error': 'Choice not found'}, status=404)

    if not choice.poll.is_published:
        return JsonResponse({'error': 'You cannot vote to this choice'}, status=403)

    all_choices = choice.poll.choice_set.all()

    for ch in all_choices:
        if ch.id != choice.id:
            if ch.users.filter(pk=user.id).exists():
                ch.users.remove(user)

    if choice.users.filter(pk=user.id).exists():
        choice.users.remove(user)
    else:
        choice.users.add(user)

    return JsonResponse({'message': 'Your vote was saved successfully'})


def index(request):
    """ Shows list and details of the polls """
    # NOTES:
    # we need pagination
    # we need some filters: polls from a specific user, search, detail of one poll and...
    # for once item: choices list, vote percent and...
    return JsonResponse({})
