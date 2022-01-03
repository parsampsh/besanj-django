""" Handles the pagination """

from django.core.paginator import Paginator
from django.http import JsonResponse


COMMENTS_HAVE_PAGINATION = False

def paginate(query, request, items_name='results', per_page=50, status_code=200, item_json=lambda item: item.to_json(), force_paginate_comments=False):
    """ Params:
    query: the query which you want paginate results of
    request: the request object
    items_name: name of the results key in json response (default is `results`. example `polls`)
    per_page: items per each page (default 50)
    status_code: response status code (default 200)
    item_json: this must be a lambda function. each item will be passed to it and the output must be json. the output json will be considered for the specific item in json response
    force_paginate_comments: this is a boolean and it is False by default. if you set this to True then this function paginates the comments and ignores the settings
    """
    if items_name == 'comments' and not COMMENTS_HAVE_PAGINATION and not force_paginate_comments:
        return JsonResponse({
            items_name: [item_json(item) for item in query.all()],
        }, status=status_code)

    paginator = Paginator(query, per_page)

    current_page_number = request.GET.get('page') if request.GET.get('page') is not None else 1
    try:
        current_page_number = int(current_page_number)
    except:
        current_page_number = 1
    current_page = paginator.get_page(current_page_number)

    current_page_items = [item_json(item) for item in current_page.object_list]

    return JsonResponse({
        items_name: current_page_items,
        'all_count': paginator.count,
        'pages_count': paginator.num_pages,
        'current_page': current_page_number,
    }, status=status_code)
