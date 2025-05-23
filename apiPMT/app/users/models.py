from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


class User(AbstractUser):
    POSITION_CHOICES = (
        ('junior_backend', 'Junior Backend'),
        ('middle_backend', 'Middle Backend'),
        ('senior_backend', 'Senior Backend'),
        ('junior_frontend', 'Junior Frontend'),
        ('middle_frontend', 'Middle Frontend'),
        ('senior_frontend', 'Senior Frontend'),
        ('teamLead', 'Team Lead'),
        ('techDir', 'Technical Director'),
        ('admin', 'Administrator'),
        ('tester', 'Tester'),
        ('project_manager', 'Project Manager'),
        ('client_manager', 'Client Manager'),
        ('devops', 'DevOps'),
    )

    position = models.CharField(max_length=20, choices=POSITION_CHOICES, null=True, blank=True)
    projects = models.ManyToManyField('projects.Project', blank=True)
    tasks = models.ManyToManyField('tasks.Task', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    def clean(self):
        if self.pk:
            if self.is_superuser:
                if self.teams.exists():
                    raise ValidationError("Администратор не может быть в команде.")
                if self.position != 'admin':
                    raise ValidationError("Суперпользователь должен иметь роль 'admin'.")

            single_team_roles = [
                'teamLead', 'junior_backend', 'middle_backend', 'senior_backend',
                'junior_frontend', 'middle_frontend', 'senior_frontend', 'tester', 'devops'
            ]
            if self.position in single_team_roles:
                if not self.teams.exists():
                    raise ValidationError(f"Роль {self.position} требует участия ровно в одной команде.")
                if self.teams.count() > 1:
                    raise ValidationError(f"Роль {self.position} позволяет быть только в одной команде.")

            team_required_roles = [
                'teamLead', 'junior_backend', 'middle_backend', 'senior_backend',
                'junior_frontend', 'middle_frontend', 'senior_frontend'
            ]
            if self.position in team_required_roles and not self.teams.exists():
                raise ValidationError(f"Роль {self.position} может быть назначена только при наличии команды.")

    def save(self, *args, **kwargs):
        if self.is_superuser and self.position is None:
            self.position = 'admin'
        try:
            self.full_clean()
            super().save(*args, **kwargs)
        except ValidationError as e:
            raise DRFValidationError(e.message_dict)
