# User Account APIs

### Register: `/account/register/` (POST)
This API can make a new user.

Arguments:
- `username`: An unique username (required, max length 255)
- `email`: An unique emails (required, max length 255)
- `password`: A password (required, unlimited length)

Responses:
- Returns `400` when there is something wrong with the arguments and a message in key `error` in the json response
- Returns `409` when the email or the username are already exists for another account
- Returns `201` when the user is registered successfully with user's api key in key `api_token` in json response

##### NOTE: the api_token is a random key with length 70. this key is for authentication. in other apis which need authentication, you should save this token at client and send it in other requests in a HTTP header named `Token`. Also, if you don't send token or send wrong token to any API which requires authentication, they will return 401 status code.

### Get Token: `/account/get-token/` (POST)
With this API, user can give her/his username/email and password and get her/his api token.

Arguments:
- `username`: An unique username (optional)
- `email`: An unique emails (optional)
- `password`: A password (required)

(you should send one of `username` and `password`)

Responses:
- Returns `400` when there is something wrong with the arguments with `error` in json
- Returns `401` when username/email or password are invalid with `error` in
- Returns `200` when everything is ok with `token` in the json response

### Who Am I: `/account/whoami` (GET)
This API returns user information to their self.
This API needs authentication using token.

Response (`200`):

```json
{
  "username": "user-name",
  "email": "email@example.com"
}
```

### Reset Token: `/account/reset-token` (POST)
This API resets the user's api token.
needs authentication with the previous token.

Response (`200`):

```json
{
  "new_token": "new-generated-token"
}
```
