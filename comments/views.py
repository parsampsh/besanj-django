from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.views import require_token
from .models import *


@require_POST
@require_token
def send(request, user):
    """ Send a new comment """
    poll_id = request.POST.get('poll_id')
    text = request.POST.get('text')
    parent_comment_id = request.POST.get('parent_comment_id')

    error_response = lambda err: JsonResponse({'error': err}, status=400)

    if poll_id is None:
        return error_response('field poll_id is required')

    if text is None:
        return error_response('field text is required')

    if len(text) > 500:
        return error_response('maximum length for field text is 500')

    try:
        poll = Poll.objects.get(pk=int(poll_id))

        if not poll.is_published:
            return JsonResponse({'error': 'poll does not exists'}, status=404)
    except:
        return JsonResponse({'error': 'poll does not exists'}, status=404)

    parent_comment = None
    if parent_comment_id is not None:
        try:
            parent_comment = Comment.objects.get(pk=int(parent_comment_id))

            if not parent_comment.is_published:
                return JsonResponse({'error': 'comment does not exists'}, status=404)
        except:
            return JsonResponse({'error': 'comment does not exists'}, status=404)

    comment = Comment.objects.create(user=user, poll=poll, text=text, parent_comment=parent_comment)

    return JsonResponse({'created_comment': comment.to_json()}, status=201)


@require_token
@require_POST
def delete(request, user):
    """ User delete their comment """
    comment_id = request.POST.get('comment_id')

    try:
        comment = Comment.objects.get(pk=int(comment_id))
    except:
        return JsonResponse({'error': 'comment not found'}, status=404)

    if comment.user.id is not user.id:
        return JsonResponse({'error': 'you do not have permission to delete this comment'}, status=403)

    comment.delete()

    return JsonResponse({'message': 'comment deleted'})


def comments_by_user(request):
    """ List of comments by a spesific user """
    pass


def comments_on_poll(request):
    """ List of comments on a spesific poll """
    pass
