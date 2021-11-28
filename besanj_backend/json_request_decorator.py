import json


def json_request(func):
    """
    You can use this decorator on your view when the incoming request has JSON data.
    This decorator deocdes json data and puts it in request.POST
    """
    def decorated_function(request):
        try:
            data = json.loads(request.raw_post_data)
            request.POST = data
        except:
            pass

        return func(request)
    return decorated_function
