from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.views import require_token


@require_POST
@require_token
def send(request):
    """ Send a new comment """
    pass


@require_token
@require_POST
def delete(request):
    """ User delete their comment """
    pass


def comments_by_user(request):
    """ List of comments by a spesific user """
    pass


def comments_on_poll(request):
    """ List of comments on a spesific poll """
    pass
