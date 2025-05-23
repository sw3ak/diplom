from rest_framework import serializers
from .models import Team
from app.users.models import User


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    team_name = serializers.CharField(write_only=True, required=False)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    position = serializers.ChoiceField(
        choices=User.POSITION_CHOICES, write_only=True
    )

    class Meta:
        model = Team
        fields = ['id', 'name', 'members', 'team_name', 'member_id', 'position', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {'name': {'required': False}}

    def get_members(self, obj):
        users = obj.members.all()
        return [{
            'id': user.id,
            'username': user.username,
            'position': user.position,
            'created_at': user.created_at
        } for user in users]

    def validate(self, data):
        user = data.get('member_id')
        position = data.get('position')
        team_name = data.get('team_name')
        name = data.get('name')
        if user and user.is_superuser:
            raise serializers.ValidationError("Администратор не может быть добавлен в команду.")
        if self.context['request'].method == 'POST' and not team_name and not name:
            if position != 'teamLead':
                raise serializers.ValidationError("Команда может быть создана только с teamLead.")
            if not name:
                raise serializers.ValidationError("name is required for team creation.")
        if team_name:
            try:
                team = Team.objects.get(name=team_name)
                if position == 'teamLead' and team.members.filter(position='teamLead').exists():
                    raise serializers.ValidationError("Команда уже имеет teamLead.")
                if user.teams.exists():
                    raise serializers.ValidationError("Пользователь уже состоит в команде.")
            except Team.DoesNotExist:
                raise serializers.ValidationError(f"Team with name {team_name} does not exist.")
        return data

    def create(self, validated_data):
        member = validated_data.pop('member_id', None)
        position = validated_data.pop('position', None)
        validated_data.pop('team_name', None)
        instance = super().create(validated_data)
        if member and position:
            instance.members.add(member)
            member.position = position
            member.save()
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('member_id', None)
        validated_data.pop('position', None)
        team_name = validated_data.pop('team_name', None)
        if team_name and instance.name != team_name:
            raise serializers.ValidationError(f"Team name {team_name} does not match.")
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
