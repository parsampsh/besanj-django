from django.db import models
from django.contrib.auth.models import User
from polls.models import Poll


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    text = models.CharField(max_length=500)
    parent_comment = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_json(self, no_replies=False):
        output = {
            'id': self.id,
            'user': self.user.profile.to_json(),
            'is_published': self.is_published,
            'text': self.text,
            'created_at': self.created_at,
            'poll_id': self.poll.id
        }

        if self.parent_comment is not None:
            output['parent_comment_id'] = self.parent_comment.id

        if not no_replies:
            replies = Comment.objects.filter(is_published=True, parent_comment=self).order_by('created_at').all()
            output['replies'] = [item.to_json() for item in replies]

        return output
