from django.db import models


# --------------------------------------------------
# Lead
# --------------------------------------------------
class Lead(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("qualified", "Qualified"),
        ("converted", "Converted"),
        ("lost", "Lost"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="new"
    )

    source = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} ({self.status})"


# --------------------------------------------------
# Ticket
# --------------------------------------------------
class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    title = models.CharField(max_length=255)

    issue = models.TextField()

    description = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="open"
    )

    priority = models.CharField(
        max_length=50,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    assigned_to = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} ({self.status})"


# --------------------------------------------------
# Candidate
# --------------------------------------------------
class Candidate(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interview', 'Interview Scheduled'),
        ('offered', 'Offer Sent'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    position_applied = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='applied')
    interview_date = models.DateTimeField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

class CandidateStatusHistory(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='history_logs')
    status = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_at']

class Employee(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.SET_NULL, null=True, blank=True)
    employee_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=255)
    joining_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_code} - {self.name}"

# --------------------------------------------------
# Reminder
# --------------------------------------------------
class Reminder(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    is_done = models.BooleanField(default=False)
    related_to = models.CharField(max_length=50, blank=True, null=True)
    related_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# --------------------------------------------------
# Chat Persistence
# --------------------------------------------------
class ChatSession(models.Model):
    user_email = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default="New Conversation")
    active_source = models.CharField(max_length=255, blank=True, null=True) # Sticky Context
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user_email})"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20) # 'user' or 'ai'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
