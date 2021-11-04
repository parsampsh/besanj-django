from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from account.views import require_token, _handle_auth_token
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
    if request.GET.get('user_id') is not None:
        try:
            user = User.objects.get(pk=request.GET.get('user_id'))
        except:
            return JsonResponse({'error': 'User not found'}, status=404)

        auth_result, auth_user = _handle_auth_token(request)
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

    paginator = Paginator(polls, 50)

    current_page_number = request.GET.get('page') if request.GET.get('page') is not None else 1
    try:
        current_page_number = int(current_page_number)
    except:
        current_page_number = 1
    current_page = paginator.get_page(current_page_number)

    current_page_polls = [item.to_json() for item in current_page.object_list]

    return JsonResponse({
        'polls': current_page_polls,
        'all_count': paginator.count,
        'pages_count': paginator.num_pages,
        'current_page': current_page_number,
    })


@require_token
def my_votes(request, user):
    """ Shows user's voted polls """
    choices = user.choice_set.order_by('-poll__created_at').all()
    paginator = Paginator(choices, 50)
    current_page_number = request.GET.get('page') if request.GET.get('page') is not None else 1
    try:
        current_page_number = int(current_page_number)
    except:
        current_page_number = 1
    choices = paginator.get_page(current_page_number).object_list

    # load polls from choices
    polls = []
    for choice in choices:
        polls.append(choice.poll.to_json())
        polls[-1]['selected_choice'] = choice.id

    return JsonResponse({
        'polls': polls,
        'all_count': paginator.count,
        'pages_count': paginator.num_pages,
        'current_page': current_page_number,
    })
