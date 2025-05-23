from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Team
from .serializers import TeamSerializer
from .permissions import IsAdmin
from django.db import transaction


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'remove_member', 'add_member']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Team.objects.all()
        return user.teams.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            team_members = instance.members.all()
            team_required_roles = [
                'teamLead', 'junior_backend', 'middle_backend', 'senior_backend',
                'junior_frontend', 'middle_frontend', 'senior_frontend', 'tester', 'devops'
            ]
            with transaction.atomic():
                for member in team_members:
                    if member.position in team_required_roles:
                        member.position = None
                        member.save()
                instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        team = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = team.members.get(id=user_id)
            team_required_roles = [
                'teamLead', 'junior_backend', 'middle_backend', 'senior_backend',
                'junior_frontend', 'middle_frontend', 'senior_frontend', 'tester', 'devops'
            ]
            if user.position in team_required_roles:
                user.position = None
                user.save()
            team.members.remove(user)
            return Response({"status": f"User {user_id} removed from team"}, status=status.HTTP_200_OK)
        except team.members.model.DoesNotExist:
            return Response({"error": "User not in team"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='add-member')
    def add_member(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team_name = serializer.validated_data.get('team_name')
        member = serializer.validated_data.get('member_id')
        position = serializer.validated_data.get('position')
        try:
            team = Team.objects.get(name=team_name)
            if member.teams.exists():
                return Response({"error": "Пользователь уже состоит в команде."}, status=status.HTTP_400_BAD_REQUEST)
            if member not in team.members.all():
                if position == 'teamLead' and team.members.filter(position='teamLead').exists():
                    return Response({"error": "Команда уже имеет teamLead."}, status=status.HTTP_400_BAD_REQUEST)
                team.members.add(member)
                member.position = position
                member.save()
                return Response({"status": f"User {member.id} added to team {team_name}"}, status=status.HTTP_200_OK)
            return Response({"error": "User already in team"}, status=status.HTTP_400_BAD_REQUEST)
        except Team.DoesNotExist:
            return Response({"error": f"Team {team_name} does not exist"}, status=status.HTTP_400_BAD_REQUEST)
