from asgiref.sync import sync_to_async
from management.models import Lead, Ticket, Candidate, Reminder, CandidateStatusHistory, Employee


# ==================================================
# LEADS
# ==================================================
@sync_to_async
def db_get_all_leads(skip: int = 0, limit: int = 50):
    qs = Lead.objects.all().order_by("-id")[skip:skip + limit]
    return list(qs.values())


@sync_to_async
def db_get_leads_count():
    return Lead.objects.count()


@sync_to_async
def db_get_lead(lead_id: int):
    return Lead.objects.filter(id=lead_id).values().first()


@sync_to_async
def db_create_lead(data: dict):
    obj = Lead.objects.create(**data)
    return {
        "id": obj.id,
        "name": obj.name,
        "email": obj.email,
        "phone": obj.phone,
        "company": obj.company,
        "status": obj.status
    }


@sync_to_async
def db_update_lead(lead_id: int, data: dict):
    Lead.objects.filter(id=lead_id).update(**data)
    return Lead.objects.filter(id=lead_id).values().first()


@sync_to_async
def db_delete_lead(lead_id: int):
    deleted, _ = Lead.objects.filter(id=lead_id).delete()
    return deleted > 0


# ==================================================
# TICKETS
# ==================================================
@sync_to_async
def db_get_all_tickets(skip: int = 0, limit: int = 50):
    qs = Ticket.objects.all().order_by("-id")[skip:skip + limit]
    return list(qs.values())


@sync_to_async
def db_get_tickets_count():
    return Ticket.objects.count()


@sync_to_async
def db_get_ticket(ticket_id: int):
    return Ticket.objects.filter(id=ticket_id).values().first()


@sync_to_async
def db_create_ticket(data: dict):
    obj = Ticket.objects.create(**data)
    return {
        "id": obj.id,
        "title": obj.title,
        "status": obj.status
    }


@sync_to_async
def db_update_ticket(ticket_id: int, data: dict):
    Ticket.objects.filter(id=ticket_id).update(**data)
    return Ticket.objects.filter(id=ticket_id).values().first()


@sync_to_async
def db_delete_ticket(ticket_id: int):
    deleted, _ = Ticket.objects.filter(id=ticket_id).delete()
    return deleted > 0


# ==================================================
# CANDIDATES
# ==================================================
@sync_to_async
def db_get_all_candidates(skip: int = 0, limit: int = 50):
    qs = Candidate.objects.all().order_by("-id")[skip:skip + limit]
    return list(qs.values())


@sync_to_async
def db_get_candidates_count():
    return Candidate.objects.count()


@sync_to_async
def db_get_candidate(candidate_id: int):
    return Candidate.objects.filter(id=candidate_id).values().first()


@sync_to_async
def db_create_candidate(data: dict):
    # Ensure status is set
    status = data.get("status", "applied")
    obj = Candidate.objects.create(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        position_applied=data["position_applied"],
        status=status,
        notes=data.get("notes")
    )
    # Log initial status
    CandidateStatusHistory.objects.create(
        candidate=obj,
        status=status,
        remarks="Initial Application"
    )
    return {
        "id": obj.id,
        "name": obj.name,
        "email": obj.email,
        "status": obj.status,
        "position_applied": obj.position_applied
    }

@sync_to_async
def db_update_candidate_status(candidate_id: int, new_status: str, remarks: str = ""):
    candidate = Candidate.objects.get(id=candidate_id)
    old_status = candidate.status
    candidate.status = new_status
    candidate.save()
    
    # Log history
    CandidateStatusHistory.objects.create(
        candidate=candidate,
        status=new_status,
        remarks=remarks or f"Status changed from {old_status} to {new_status}"
    )
    from django.forms.models import model_to_dict
    return model_to_dict(candidate)

@sync_to_async
def db_create_employee(candidate_id: int, joining_date):
    candidate = Candidate.objects.get(id=candidate_id)
    import uuid
    emp_code = f"EMP-{str(uuid.uuid4())[:8].upper()}"
    
    employee = Employee.objects.create(
        candidate=candidate,
        employee_code=emp_code,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone or "",
        role=candidate.position_applied,
        joining_date=joining_date
    )
    from django.forms.models import model_to_dict
    return model_to_dict(employee)

@sync_to_async
def db_get_candidate_history(candidate_id: int):
    history = CandidateStatusHistory.objects.filter(candidate_id=candidate_id).order_by('-changed_at').values()
    return list(history)


@sync_to_async
def db_update_candidate(candidate_id: int, data: dict):
    Candidate.objects.filter(id=candidate_id).update(**data)
    return Candidate.objects.filter(id=candidate_id).values().first()


@sync_to_async
def db_delete_candidate(candidate_id: int):
    deleted, _ = Candidate.objects.filter(id=candidate_id).delete()
    return deleted > 0


# ==================================================
# REMINDERS
# ==================================================
@sync_to_async
def db_get_all_reminders(done=None, skip: int = 0, limit: int = 50):
    qs = Reminder.objects.all().order_by("-id")

    if done is not None:
        qs = qs.filter(is_done=done)

    qs = qs[skip:skip + limit]

    return list(qs.values())


@sync_to_async
def db_get_reminders_count(done=None):
    qs = Reminder.objects.all()

    if done is not None:
        qs = qs.filter(is_done=done)

    return qs.count()


@sync_to_async
def db_create_reminder(data: dict):
    obj = Reminder.objects.create(**data)

    return {
        "id": obj.id,
        "title": obj.title,
        "description": obj.description,
        "due_date": str(obj.due_date),
        "is_done": obj.is_done
    }


@sync_to_async
def db_update_reminder(reminder_id: int, data: dict):
    Reminder.objects.filter(id=reminder_id).update(**data)
    return Reminder.objects.filter(id=reminder_id).values().first()


@sync_to_async
def db_delete_reminder(reminder_id: int):
    deleted, _ = Reminder.objects.filter(id=reminder_id).delete()
    return deleted > 0


# ==================================================
# GLOBAL SEARCH
# ==================================================
@sync_to_async
def db_search_by_name(query: str):
    # Strip common noise from search query
    from django.db.models import Q
    noise = ["create", "update", "details", "for", "of", "candidate", "lead", "show", "get"]
    clean_q = query.lower()
    for w in noise: clean_q = clean_q.replace(w, "")
    clean_q = clean_q.strip()

    leads = list(
        Lead.objects.filter(Q(name__icontains=clean_q) | Q(email__icontains=clean_q)).values()
    )
    candidates = list(
        Candidate.objects.filter(Q(name__icontains=clean_q) | Q(email__icontains=clean_q)).values()
    )
    
    return {
        "leads": leads,
        "candidates": candidates,
        "total": len(leads) + len(candidates)
    }