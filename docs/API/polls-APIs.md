# Polls APIs

### Create Poll: `/polls/create/` (POST)
This API creates a new post. needs authentication.

Arguments:
- `title`: title of the poll (max length 255, required)
- `description`: description of the poll (max length 1000, optional)
- `choices`: list of the choices of the poll. you should write choices line by line. each line is one choice. example: `first choice\nsecond choice` (required)

Responses:
- Returns `400` when some required fields are not sent or length of some fields are more than maximum
- Returns `201` when the poll is created successfully with `created_poll` in json responses (see structure of the json data in the next sections of this document)

### Delete Poll: `/polls/delete/` (POST)
This API deletes a poll and requires authentication.

Arguments:
- `poll_id`: id of the poll that you want to delete (required)

Responses:
- Returns `404` when the poll does not exists
- Returns `403` when you are trying to delete another user's poll
- Returns `200` when the poll is deleted successfully

### Choose: `/polls/choose/` (GET)
This API lets user to select a choice in a poll.
Requires authentication.

Arguments:
- `choice_id`: id of the choice that you want to choose

Responses:
- Returns `404` when the choice doesn't exist
- Returns `403` when the poll is not published yet
- Returns `200` when you voted successfully

Json response:

```json
{
	"message": "...",
	"updated_poll": {...poll object...}
}
```

The `updated_poll` contains information of the poll and it's choices after voting (percents and counts will be updated).
You can replace these information with those which were shown in the front end app after user voted.

### Index: `/polls/`
This API returns list of polls with some filters.
Does not require authentication but authentication makes more features for it.

Arguments:
- `single_poll_id`: when you wanna just get information of one single poll using it's id
- `user_id`: when you wanna get list of polls of one user (or yourself)
- `search`: when you wanna search the polls by a phrase
- `page`: determine current page in pagination

Responses:
- Returns `404` when `single_poll_id` or `user_id` doesn't exist
- Returns `200` when everything is ok

The response has pagination. here structure of it:

```json
{
  "all_count": "<count of all of the polls in result>",
  "pages_count": "<count of all of the pages in result>",
  "current_page": "<number of the current page>",
  "polls": [
    {...},
    {...},
    {...},
  ]
}
```

Structure of each item in `polls` key above:

```json
{
  "id": "id of the poll",
  "title": "title",
  "description": "description",
  "is_published": "is poll published(boolean, the unpublished polls will be showed to only owner of them)",
  "created_at": "datetime",
  "total_votes_count": "count of total votes to this poll",
  "user": {...},
  "choices": [
    {
      "id": 1,
      "title": "title",
      "sort": "a number for sorting choices",
      "votes_count": "count of the votes to this choice",
      "votes_percent": "percent of votes count between other choices"
    }
  ]
}
```

There can be a `selected_choice` key in poll json. But it happens only when a user is authenticated and calls this API.
Then for each poll, IF user has voted to it before, `selected_choice` key will be included which contains ID of selected choice on this poll by user.

### My Votes: `/polls/my_votes/`
This API shows user their votes polls.
Requires authentication.

Arguments:
- `page`: Page number for pagination

Responses:
- Returns `401` when you are not authenticated
- Returns `200` when everything is ok

Json response is same like index API, but including one more field in json of each poll.
It is `selected_choice` that contains id of selected choice by user in that poll.
