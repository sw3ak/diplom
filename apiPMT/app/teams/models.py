from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField('users.User', related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name