from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from account.views import require_token, _handle_auth_token
from .models import *
from besanj_backend.pagination_policy import paginate
from besanj_backend.json_request_decorator import json_request


@json_request
@require_POST
@require_token
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

    for choice in choices:
        if len(choice) > 255:
            return JsonResponse({"error": "Maximum length for each choice is 255"}, status=400)

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

    return JsonResponse({'created_poll': poll.to_json()}, status=201)


@json_request
@require_POST
@require_token
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


@json_request
@require_POST
@require_token
def choose(request, user):
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

    return JsonResponse({'message': 'Your vote was saved successfully', 'updated_poll': choice.poll.to_json(user=user)})


def index(request):
    """ Shows list and details of the polls """
    auth_result, auth_user = _handle_auth_token(request)
    if not auth_result:
        auth_user = None
    if request.GET.get('user_id') is not None:
        try:
            user = User.objects.get(pk=request.GET.get('user_id'))
        except:
            return JsonResponse({'error': 'User not found'}, status=404)

        if auth_result and auth_user.id == user.id:
            polls = user.poll_set.order_by('-created_at')
        else:
            polls = user.poll_set.order_by('-created_at').filter(is_published=True)
    elif request.GET.get('single_poll_id') is not None:
        try:
            polls = [Poll.objects.get(pk=int(request.GET.get('single_poll_id')))]
        except:
            return JsonResponse({'error': 'Poll not found'}, status=404)

        if not polls[0].is_published:
            return JsonResponse({'error': 'Poll not found'}, status=404)
    else:
        polls = Poll.objects.order_by('-created_at').filter(is_published=True)

    if request.GET.get('search') is not None:
        searched_phrase = request.GET.get('search')
        polls = polls.filter(
            Q(title__contains=searched_phrase) | Q(description__contains=searched_phrase)
        )

    return paginate(polls, request, items_name='polls', item_json=lambda poll: poll.to_json(user=auth_user))


@require_token
def my_votes(request, user):
    """ Shows user's voted polls """
    choices = user.choice_set.order_by('-poll__created_at').all()

    return paginate(choices, request, items_name='polls', item_json=lambda choice: choice.poll.to_json(include_selected_choice_id=choice.id))
