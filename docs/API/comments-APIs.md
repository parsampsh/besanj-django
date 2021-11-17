# Comments APIs

### Send Comment: `/comments/send/`
This API is for sending comments. requires authentication.

Arguments:
- `poll_id`: Id of the poll which you want to send the comment on (required)
- `text`: Text of the comment (required, max length 500)
- `parent_comment_id`: Id of the poll which you want to send the comment as reply to (optional)

Responses:
- Returns `400` when there are problems with the sent arguments
- Returns `404` when the poll of parent comment does not exist
- Returns `201` when the comment is sent successfully with key `created_comment` in json response.

Structure of comment json:

```json
{
    "id": 1,
    "user": {...},
    "is_published": true,
    "text": "hi",
    "created_at": {...datetime...},
    "poll_id": 1
}
```

### Delete Comment: `/comments/delete/`
This API deletes a comment. requires authentication.

Arguments:
- `comment_id`: Id of the comment which you want to delete

Responses:
- Returns `404` when the given comment id does not exists
- Returns `403` when user tries to delete comment of other user
- Returns `200` when the comment is deleted successfully

### User Comments: `/comments/user_comments`
This API returns list of comments of a specific user.

Arguments:
- `user_id`: Id of the user which you want to get comments of
- `page`: Page number of pagination

Responses:
- Returns `404` when the given user id does not exists
- Returns `200` and the comments in json response

Structure of json response:

```json
{
    "comments": [{...}, {...}, {...}],
    "all_count": 10,
    "pages_count": 1,
    "current_page": 1
}
```

Note: if you send authentication token to this API, unpublished comments will be shown too.

### Poll Comments: `/comments/poll_comments/`
This API returns list of comment of a specific poll.

Arguments:
- `poll_id`: Id of the poll which you want to get comments of
- `page`: Page number of pagination

Responses:
- Returns `404` when the given poll id does not exists
- Returns `200` and the comments in json response
