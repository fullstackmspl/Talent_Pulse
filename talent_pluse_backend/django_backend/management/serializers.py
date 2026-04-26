from rest_framework import serializers
from .models import Lead, Ticket, Candidate, Reminder


# --------------------------------------------------
# Lead
# --------------------------------------------------
class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"


# --------------------------------------------------
# Ticket
# --------------------------------------------------
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


# --------------------------------------------------
# Candidate
# --------------------------------------------------
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = "__all__"


# --------------------------------------------------
# Reminder
# --------------------------------------------------
class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = "__all__"