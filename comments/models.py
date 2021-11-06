from django.db import models
from django.contrib.auth.models import User
from polls.models import Poll


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    text = models.CharField(max_length=500)
    parent_comment = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
