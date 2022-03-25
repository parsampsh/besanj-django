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

### Reset Password: `/account/reset-password/` (POST)
This API makes a reset password request and sends a link to the user's email.

Arguments (ONE of these two):
- `username`: Username of the user who wants to reset their password
- `email`: Email of the user who wants to reset their password

Responses:
- `400`: Arguments not sent
- `404`: User not found
- `200`: Email sent successfully

### Reset Password Final: `/account/reset-password-final/` (POST)
This API finally changes the password using the code that user has received in email using the previous API.

Arguments:
- `code`: The code that user has received
- `new_password`: The new password for user (optional)

You can use this API in 2 ways:
- Check that is the code true or not by sending only `code` argument (can be used before asking user to enter the new password)
- Change the password by sending both `code` and `new_password`

Responses:
- `400`: Arguments not sent
- `404`: Invalid code
- `403`: Reset password request is expired (will be expired after 2 hours)
- `200`: If you have sent both `code` and `new_password` this means password is changed successfully and if you only sent `code` this means the code is valid and not expired yet so you can use it to change the password
