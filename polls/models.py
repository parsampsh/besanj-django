from django.db import models
from django.contrib.auth.models import User


class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_votes_count(self):
        """ Returns count of total votes to this poll """
        return sum([item.votes_count() for item in self.choice_set.all()])

    def to_json(self, include_selected_choice_id=None, user=None):
        """ Returns the information of the poll in the json format """
        output = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_published': self.is_published,
            'created_at': str(self.created_at),
            'choices': [item.to_json() for item in self.choice_set.order_by('sort').all()],
            'total_votes_count': self.total_votes_count(),
            'user': self.user.profile.to_json(),
            'belongs_to_you': False
        }

        if include_selected_choice_id is not None:
            output['selected_choice'] = include_selected_choice_id
        elif user is not None:
            selected_choice = user.choice_set.filter(poll=self).first()
            if selected_choice != None:
                output['selected_choice'] = selected_choice.id

        if user is not None:
            if user == self.user:
                output['belongs_to_you'] = True

        return output


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)
    users = models.ManyToManyField(User)

    def votes_count(self):
        """ Returns count of the votes to this choice """
        return self.users.count()

    def votes_percent(self):
        total_votes = self.poll.total_votes_count()
        votes_to_this = self.votes_count()
        try:
            percent = (votes_to_this * 100) / total_votes
            return percent
        except:
            pass
        return 0

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'sort': self.sort,
            'votes_count': self.votes_count(),
            'votes_percent': self.votes_percent(),
        }
