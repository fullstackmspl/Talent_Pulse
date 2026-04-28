import re
from datetime import timedelta
from django.utils import timezone

from core.db_service import (
    db_create_lead,
    db_get_lead,
    db_update_lead,
    db_get_all_leads,
    db_create_candidate,
    db_get_candidate,
    db_update_candidate,
    db_get_all_candidates,
    db_create_ticket,
    db_get_ticket,
    db_get_all_tickets,
    db_delete_ticket,
    db_create_reminder,
    db_get_all_reminders,
    db_search_by_name,
)

from core.n8n_service import (
    notify_new_lead,
    notify_candidate_update,
    notify_new_ticket,
    notify_reminder,
)


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def extract_email(text: str):
    # Matches email with special characters but MUST end in .com
    match = re.search(r"[\w\.\-\#\$\%\&\*\+\=\?\^\_\`\{\|\}\~\!]+@[\w\.-]+\.com", text, re.IGNORECASE)
    return match.group(0).lower() if match else None


def extract_name(text: str):
    # Remove noise words
    noise = ["create", "schedule", "update", "delete", "details", "show", "get", "for", "of", "candidate", "lead", "person", "new", "save", "add", "stage"]
    clean = text.lower()
    for word in noise:
        clean = re.sub(rf'\b{word}\b', '', clean)
    
    # Remove special chars and IDs
    clean = re.sub(r'[#\d]', '', clean)
    
    # Capitalize
    clean = clean.strip().title()
    return clean if clean else None


def extract_position(text: str):
    match = re.search(
        r"(?:for|as|role|position)\s+([A-Za-z0-9\+\# ]{2,40})",
        text,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else None


def extract_phone(text: str):
    # Extract all digits to check the 10-digit rule
    all_digits = "".join(re.findall(r"\d", text))
    # Return last 10 digits if more are provided (to handle +91 etc)
    if len(all_digits) >= 10:
        return all_digits[-10:]
    return None


def parse_date_string(text: str):
    # Simple regex for DD Month YYYY
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }
    lower = text.lower()
    
    # Match "25 April 2026" or "25-04-2026"
    match = re.search(r"(\d{1,2})[\s\-\/]([a-zA-Z]{3,10}|0?\d{1,2})[\s\-\/](\d{4})", text)
    if match:
        day, month, year = match.groups()
        day = day.zfill(2)
        if month.isdigit():
            month = month.zfill(2)
        else:
            month = months.get(month[:3].lower(), "01")
        return f"{year}-{month}-{day}"
    
    # Fallback: Just return today if it's "today" or "now"
    if "today" in lower:
        from datetime import date
        return str(date.today())
        
    return None


def extract_company(text: str):
    match = re.search(r"(?:at|from|company|work at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_due_date(text: str):
    now = timezone.now()
    lower = text.lower()

    if "tomorrow" in lower:
        return now + timedelta(days=1)

    if "next week" in lower:
        return now + timedelta(days=7)

    if "1 hour" in lower:
        return now + timedelta(hours=1)

    return now + timedelta(hours=2)


# ---------------------------------------------------
# Session Management
# ---------------------------------------------------
SESSIONS = {}


async def route_intent(intent: str, message: str, session_id: str = "default"):
    if not message:
        return {"message": "I didn't receive any text. How can I help you?"}
        
    lower = message.lower().strip()
    id_match = re.search(r"#?(\d+)", message)

    # 0. Question Heuristic: If it looks like a question about documents, bypass DB routing
    question_words = ["what", "who", "where", "when", "why", "how", "show me", "can you", "list", "does", "is", "are", "find", "tell"]
    if any(lower.startswith(q) for q in question_words) or lower.endswith("?"):
        # Bypass if it mentions "resume", "file", "document" or doesn't look like a clear data command
        if any(word in lower for word in ["resume", "file", "document", "in", "from"]):
            if not any(cmd in lower for cmd in ["save", "create", "delete", "remove", "update"]):
                return None # Falls back to RAG
    
    # 0. Heuristic Overrides for Direct Commands (Bypass model if obvious)
    if "delete" in lower or "remove" in lower or "erase" in lower:
        if "lead" in lower: intent = "delete_lead"
        elif "candidate" in lower: intent = "delete_candidate"
        elif "ticket" in lower: intent = "delete_ticket"
        elif id_match and intent not in ["delete_lead", "delete_candidate", "delete_ticket"]:
             # If just "delete #2", we'll use the wizard to be safe, or default to lead
             pass 

    # 0.5. Lead Report Heuristics
    if "conversion rate" in lower or "converted rate" in lower or "conversion %" in lower:
        intent = "lead_conversion_rate"
    elif "contacted lead" in lower:
        intent = "lead_report_contacted"
    elif "converted this month" in lower or "leads converted this month" in lower or ("converted" in lower and "month" in lower):
        intent = "lead_report_converted_month"
    elif "show converted" in lower or "converted lead" in lower:
        intent = "lead_report_converted"
    elif "show lost" in lower or "lost lead" in lower:
        intent = "lead_report_lost"
    elif "new lead" in lower and not any(x in lower for x in ["create", "add", "save", "make"]):
        intent = "lead_report_new"
    elif "all lead" in lower or "total lead" in lower or "show leads" == lower:
        intent = "lead_report_total"
    
    # 0.5.5 Candidate Report Heuristics
    if "candidate" in lower:
        if "hired" in lower: intent = "candidate_report_hired"
        elif "interview" in lower: intent = "candidate_report_interview"
        elif "screening" in lower: intent = "candidate_report_screening"
        elif "offered" in lower: intent = "candidate_report_offered"
        elif "rejected" in lower: intent = "candidate_report_rejected"
        elif "applied" in lower: intent = "candidate_report_applied"

    # 0.6. Heuristic Override for Resume Uploads/Analysis
    # Avoid triggering analyze_resume if the user is asking a question about a file.
    is_question = any(word in lower.split() for word in ["what", "who", "when", "where", "how", "why", "can", "is", "explain"])
    if not is_question and (re.search(r"\.(pdf|jpg|jpeg|png)", lower) or ("upload" in lower and "resume" in lower) or lower == "analyze old resume"):
        intent = "analyze_resume"


    # 1. Check for Global Exit/Cancel Keywords
    if lower in ["exit", "quit", "end", "cancel", "bye", "stop"]:
        if session_id in SESSIONS:
            del SESSIONS[session_id]
            return {"message": "Process cancelled. No problem! I'm here if you need anything else. 😊"}
        return {"message": "Goodbye! Have a great day. I'm ready for your next question whenever you are."}

    # 2. Check for active session
    session = SESSIONS.get(session_id)
    if session:
        # Handle Search Type Clarification (Lead vs Candidate)
        if session["type"] == "clarify_search_type":
            choice = message.lower()
            name = session["name"]
            if "lead" in choice:
                del SESSIONS[session_id]
                return await route_intent("lead_get", f"details for {name}", session_id)
            elif "candidate" in choice:
                del SESSIONS[session_id]
                return await route_intent("candidate_get", f"details for {name}", session_id)
            else:
                return {
                    "message": f"I found results for '{name}' in both Leads and Candidates. Which one should I open?",
                    "options": ["Lead", "Candidate"]
                }

        # Handle Delete Type Clarification
        if session["type"] == "clarify_delete_type":
            choice = message.lower()
            if "lead" in choice:
                session["type"] = "delete_lead_identify"
                return {"message": "Okay, please provide the ID (#), Email, or Name of the Lead you want to delete."}
            elif "candidate" in choice:
                session["type"] = "delete_candidate_identify"
                return {"message": "Okay, please provide the ID (#), Email, or Name of the Candidate you want to delete."}
            else:
                return {
                    "message": "What would you like to delete: a Lead or a Candidate?",
                    "options": ["Lead", "Candidate"]
                }

        # Handle Delete Identification
        if session["type"] in ["delete_lead_identify", "delete_candidate_identify"]:
            is_lead = "lead" in session["type"]
            del SESSIONS[session_id]
            return await route_intent("delete_lead" if is_lead else "delete_candidate", message, session_id)

        # Handle Resume Analysis Choice (Old vs New)
        if session["type"] == "clarify_resume_choice":
            choice = message.lower()
            if "old" in choice:
                import json
                try:
                    with open("uploaded_files.json", "r") as f:
                        all_files = json.load(f)
                    # Filter for PDFs/Images
                    resumes = [f["name"] for f in all_files if f["name"].lower().endswith((".pdf", ".jpg", ".jpeg", ".png"))]
                except:
                    resumes = []
                
                if not resumes:
                    del SESSIONS[session_id]
                    return {"message": "I couldn't find any resumes in your uploaded_files.json. Would you like to upload a new one?"}
                
                session["type"] = "clarify_old_resume_selection"
                return {
                    "message": "Which old resume should I analyze?",
                    "options": resumes[-6:] # Show last 6 uploads
                }
            elif "new" in choice or "upload" in choice:
                del SESSIONS[session_id]
                return {"message": "Please use the + icon to upload your resume. After it finishes uploading, just type the file name or click it to begin analysis!"}
            else:
                return {
                    "message": "Would you like to analyze an old resume from the system, or upload a new one?",
                    "options": ["Analyze Old Resume", "Upload New Resume"]
                }

        # Handle Old Resume Selection
        if session["type"] == "clarify_old_resume_selection":
            filename = message.strip()
            del SESSIONS[session_id]
            # Use a special tag to tell analyze_resume this is a DIRECT filename
            return await route_intent("analyze_resume", f"FILE_TARGET:{filename}", session_id)

        # Handle Clarification for Lookups (Multiple people with same name)
        if session["type"] in ["clarify_lead_get", "clarify_candidate_get"]:

            id_match = re.search(r"#?(\d+)", message)
            if id_match:
                target_id = int(id_match.group(1))
                is_lead = "lead" in session["type"]
                from core.db_service import db_get_lead, db_get_candidate
                target = await db_get_lead(target_id) if is_lead else await db_get_candidate(target_id)
                
                if target:
                    del SESSIONS[session_id]
                    if is_lead:
                        return {
                            "message": f"🔍 Lead Details:\nID: #{target['id']}\nName: {target['name']}\nEmail: {target['email']}\nStatus: {target['status']}\nPhone: {target.get('phone', 'N/A')}\nCompany: {target.get('company', 'N/A')}",
                            "data": target
                        }
                    else:
                        from core.db_service import db_get_candidate_history
                        history = await db_get_candidate_history(target['id'])
                        timeline = "\n".join([f"🕒 {h['changed_at'].strftime('%d %b')}: {h['status'].upper()} ({h['remarks'] or 'No remarks'})" for h in history])
                        return {
                            "message": f"🔍 Candidate Details:\nName: {target['name']}\nEmail: {target['email']}\nRole: {target['position_applied']}\n\n📍 Current Status: {target['status'].upper()}\n\n📜 Status History:\n{timeline if timeline else 'No history found.'}",
                            "data": target
                        }
                return {"message": f"I couldn't find ID #{target_id}. Please try again or provide a name."}
            else:
                # If they type a name instead of ID, restart search
                del SESSIONS[session_id]
                return await route_intent(intent, message, session_id)

        # Handle Clarification for Converted Leads
        if session["type"] == "clarify_converted_leads":
            choice = message.lower()
            from management.models import Lead
            from asgiref.sync import sync_to_async
            
            limit = 20 if "all" in choice else 10
            
            leads = await sync_to_async(lambda: list(Lead.objects.filter(status="converted").order_by("-updated_at")[:limit].values()))()
            del SESSIONS[session_id]
            
            if not leads: return {"message": "No converted leads found."}
            items = [f"#{l['id']} {l['name']} | Converted on: {l['updated_at'].strftime('%Y-%m-%d')}" for l in leads]
            return {"message": f"🏆 Here are the {'last 20' if limit == 20 else 'last 10'} converted leads:\n" + "\n".join(items)}

        # Handle Clarification for Converted Month
        if session["type"] == "clarify_converted_month":
            choice = message.lower()
            months = {
                "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
                "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sep": 9, "october": 10, "oct": 10,
                "november": 11, "nov": 11, "december": 12, "dec": 12
            }
            month_num = None
            for m_name, m_val in months.items():
                if m_name in choice:
                    month_num = m_val
                    break
            
            if not month_num:
                if "this" in choice or "current" in choice:
                    month_num = timezone.now().month
                else:
                    return {"message": "Please specify a valid month (e.g., 'April', 'Jan', or 'this month')."}

            from management.models import Lead
            from asgiref.sync import sync_to_async
            
            leads = await sync_to_async(lambda: list(Lead.objects.filter(status="converted", updated_at__month=month_num).order_by("-updated_at").values()))()
            del SESSIONS[session_id]
            
            months_names = {
                1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
                7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
            }
            m_name = months_names.get(month_num, f"Month {month_num}")
            
            if not leads: return {"message": f"No leads were converted in {m_name}."}
            items = [f"#{l['id']} {l['name']} | {l.get('company', 'N/A')} | {l['updated_at'].strftime('%d %b')}" for l in leads]
            return {"message": f"📅 Converted Leads ({m_name}):\n" + "\n".join(items)}

        # --------------------------------------------------
        # CREATE LEAD SESSION 
        # --------------------------------------------------
        if session["type"] == "create_lead":
            if not session.get("name"):
                session["name"] = extract_name(message) or message.strip()
            elif not session.get("email"):
                email = extract_email(message)
                if not email: return {"message": "Invalid email format. It must end with .com. Please try again."}
                session["email"] = email
            elif not session.get("phone"):
                phone = extract_phone(message)
                if not phone: return {"message": "Invalid phone! Please provide exactly 10 digits."}
                session["phone"] = phone
            elif not session.get("role"):
                session["role"] = extract_position(message) or message.strip()
            elif not session.get("status"):
                session["status"] = message.strip().lower()

            if session.get("name") and session.get("email") and session.get("phone") and session.get("role") and session.get("status"):
                try:
                    data = await db_create_lead({
                        "name": session["name"], "email": session["email"], "phone": session["phone"],
                        "company": session["role"], "status": session["status"], "notes": "Created via smart multi-turn."
                    })
                    from core.n8n_service import notify_new_lead
                    await notify_new_lead(data)
                    if session_id in SESSIONS: del SESSIONS[session_id]
                    return {"message": f"🎉 Success! Lead created for {data['name']}.\nDetails: {data['email']} | {data['phone']} | Status: {data['status']}\n\n📧 Email Notification Sent to Admin."}
                except Exception as e:
                    if session_id in SESSIONS: del SESSIONS[session_id]
                    return {"message": f"❌ Error: {str(e)}"}

            # Ask for next
            if not session.get("email"): return {"message": f"What is the email for {session['name']}?"}
            if not session.get("phone"): return {"message": f"What is the phone number for {session['name']}?"}
            if not session.get("role"): return {"message": f"What is the company/role for {session['name']}?"}
            if not session.get("status"):
                return {
                    "message": f"Lastly, what is the status for {session['name']}?",
                    "options": ["New", "Contacted", "Qualified", "Converted", "Lost"]
                }

        # --------------------------------------------------
        # CREATE CANDIDATE SESSION
        # --------------------------------------------------
        if session["type"] == "create_candidate":
            if not session.get("name"):
                session["name"] = extract_name(message) or message.strip()
            elif not session.get("email"):
                email = extract_email(message)
                if not email: return {"message": "Invalid email. Must end in .com."}
                session["email"] = email
            elif not session.get("role"):
                session["role"] = extract_position(message) or message.strip()
            elif not session.get("phone"):
                phone = extract_phone(message)
                if not phone: return {"message": "Invalid phone. Must be 10 digits."}
                session["phone"] = phone
            elif not session.get("status"):
                # Handle status selection
                val = message.strip().lower()
                valid_stages = ["applied", "screening", "interview", "offered", "hired", "rejected"]
                found = None
                for s in valid_stages:
                    if s in val: found = s; break
                if not found:
                    return {
                        "message": f"Please select a starting stage for {session['name']}:",
                        "options": ["Applied", "Screening", "Interview", "Offered", "Hired", "Rejected"]
                    }
                session["status"] = found
                
                # Special cases for creation
                if found == "interview":
                    return {"message": f"Candidate set to Interview stage. When is the interview scheduled for {session['name']}?"}
                if found == "hired":
                    return {"message": f"Congratulations! When is the official joining date for {session['name']}?"}

            elif session["status"] == "interview" and not session.get("interview_date"):
                session["interview_date"] = message.strip()
            elif session["status"] == "hired" and not session.get("joining_date"):
                session["joining_date"] = message.strip()

            # Check completion
            if session.get("name") and session.get("email") and session.get("role") and session.get("phone") and session.get("status"):
                # Final check for dates if needed
                if session["status"] == "interview" and not session.get("interview_date"):
                    return {"message": "Please provide the interview date to finish."}
                if session["status"] == "hired" and not session.get("joining_date"):
                    return {"message": "Please provide the joining date to finish."}
                
                try:
                    from core.db_service import db_create_candidate, db_update_candidate
                    data = await db_create_candidate({
                        "name": session["name"], "email": session["email"], "position_applied": session["role"],
                        "phone": session["phone"], "status": session["status"], "notes": "New candidate flow."
                    })
                    # Update dates if provided
                    if session.get("interview_date"): await db_update_candidate(data["id"], {"interview_date": session["interview_date"]})
                    if session.get("joining_date"): 
                        from core.db_service import db_create_employee
                        await db_update_candidate(data["id"], {"joining_date": session["joining_date"]})
                        await db_create_employee(data["id"], session["joining_date"])
                    
                    # Notify
                    from core.n8n_service import notify
                    await notify("CANDIDATE_CREATED", data, "candidate-created")
                    
                    if session_id in SESSIONS: del SESSIONS[session_id]
                    return {"message": f"👔 Great! Candidate {data['name']} has been added as '{session['status']}'. I've logged this to your history timeline."}
                except Exception as e:
                    if session_id in SESSIONS: del SESSIONS[session_id]
                    return {"message": f"❌ Error: {str(e)}"}

            # Ask for next
            if not session.get("email"): return {"message": f"What is the email for {session['name']}?"}
            if not session.get("role"): return {"message": f"What role is {session['name']} applying for?"}
            if not session.get("phone"): return {"message": f"What is the phone number for {session['name']}?"}
            if not session.get("status"):
                return {
                    "message": f"What is the current stage for {session['name']}?",
                    "options": ["Applied", "Screening", "Interview", "Offered", "Hired", "Rejected"]
                }

        # --------------------------------------------------
        # UPDATE SESSION (LEAD/CANDIDATE)
        # --------------------------------------------------
        if session["type"] == "update_lead" or session["type"] == "update_candidate":
            is_lead = "lead" in session["type"]
            
            # 1. IDENTIFY STAGE
            if not session.get("target_id"):
                id_match = re.search(r"#?(\d+)", message)
                email = extract_email(message)
                name = extract_name(message)
                target = None
                if id_match:
                    from core.db_service import db_get_lead, db_get_candidate
                    target = await db_get_lead(int(id_match.group(1))) if is_lead else await db_get_candidate(int(id_match.group(1)))
                elif email or name:
                    from core.db_service import db_search_by_name
                    search = await db_search_by_name(email or name)
                    pool = search["leads"] if is_lead else search["candidates"]
                    if len(pool) > 1: return {"message": f"Multiple matches found. Please provide ID (#)."}
                    target = pool[0] if pool else None

                if not target: return {"message": f"Couldn't find that { 'lead' if is_lead else 'candidate' }. Provide ID or Email."}
                session["target_id"] = target["id"]
                session["current_data"] = target
                # SAFETY: Return here so we don't use the ID message as the field value!
                return {
                    "message": f"Found {target['name']}. What would you like to update?",
                    "options": ["Name", "Email", "Phone", "Status", ("Company" if is_lead else "Role")]
                }
                
            # 2. FIELD SELECTION STAGE
            if not session.get("field"):
                # Check current message first (for menu clicks)
                current_msg = message.lower()
                detected_field = None
                for f in ["name", "email", "phone", "status", "company", "role"]:
                    if f in current_msg: 
                        detected_field = "position_applied" if f == "role" else f
                        break
                
                # If still nothing, check initial message (for shortcut commands)
                if not detected_field:
                    msg_low = session["initial_msg"].lower()
                    for f in ["name", "email", "phone", "status", "company", "role"]:
                        if f in msg_low: 
                            detected_field = "position_applied" if f == "role" else f
                            break
                
                if detected_field:
                    session["field"] = detected_field
                    # If the field was just selected from a menu click, ask for the value
                    if detected_field.lower() in message.lower():
                        if detected_field == "status":
                             opts = ["New", "Contacted", "Qualified", "Converted", "Lost"] if is_lead else ["Applied", "Screening", "Interview", "Offered", "Hired", "Rejected"]
                             return {
                                "message": f"Please select the new status for {session['current_data']['name']}:",
                                "options": opts
                             }
                        return {"message": f"What is the new {detected_field.replace('_', ' ')} for {session['current_data']['name']}?"}
                else:
                    opts = ["Name", "Email", "Phone", "Status", ("Company" if is_lead else "Role")]
                    return {
                        "message": f"Found {session['current_data']['name']}. What would you like to update?",
                        "options": opts
                    }

            # 3. SET VALUE STAGE
            if session["field"] == "status" and not is_lead:
                # FIRST: Check if we were waiting for a date (Interview/Joining)
                if session.get("temp_date_type"):
                    date_val = parse_date_string(message)
                    if not date_val:
                        # If the user is trying to do something else, let them out
                        if len(message.split()) > 4: # Likely a new command
                            del SESSIONS[session_id]
                            return await route_intent(intent, message, session_id)
                        return {"message": "I couldn't understand that date. Please use a format like '25 April 2026' or '2026-04-25'."}
                    
                    new_val = session.get("temp_status")
                    
                    try:
                        from core.db_service import db_update_candidate_status, db_create_employee, db_update_candidate
                        await db_update_candidate_status(session["target_id"], new_val, f"Moved to {new_val} on {date_val}")
                        
                        if session["temp_date_type"] == "interview":
                            await db_update_candidate(session["target_id"], {"interview_date": date_val})
                        elif session["temp_date_type"] == "joining":
                            await db_update_candidate(session["target_id"], {"joining_date": date_val})
                            await db_create_employee(session["target_id"], date_val)
                        
                        from core.n8n_service import notify
                        await notify("STATUS_UPDATED", {"id": session["target_id"], "status": new_val, "date": date_val}, "status-updated")
                        
                        del SESSIONS[session_id]
                        return {"message": f"✅ Success! {session['current_data']['name']} is now in {new_val.upper()} stage for {date_val}."}
                    except Exception as e:
                        return {"message": f"⚠️ Database Error: {str(e)}. Please try a different date format."}

                # SECOND: If no date pending, handle status selection
                val = message.strip().lower()
                valid_stages = ["applied", "screening", "interview", "offered", "hired", "rejected"]
                found = None
                for s in valid_stages:
                    if s in val: found = s; break
                
                if not found:
                    return {
                        "message": f"Please select a new status for {session['current_data']['name']}:",
                        "options": ["Applied", "Screening", "Interview", "Offered", "Hired", "Rejected"]
                    }
                
                # Handle stages that need dates
                if found == "interview":
                    session["temp_date_type"] = "interview"
                    session["temp_status"] = "interview"
                    return {"message": f"Moving to Interview stage. When is the interview scheduled?"}
                if found == "hired":
                    session["temp_date_type"] = "joining"
                    session["temp_status"] = "hired"
                    return {"message": f"Congratulations! What is the joining date?"}
                
                # Normal update for other stages
                from core.db_service import db_update_candidate_status
                await db_update_candidate_status(session["target_id"], found, f"Updated to {found}")
                
                from core.n8n_service import notify
                await notify("STATUS_UPDATED", {"id": session["target_id"], "status": found}, "status-updated")
                
                del SESSIONS[session_id]
                return {"message": f"✅ Status updated to {found.upper()}!"}

            # Generic Field Update
            val = message.strip()
            
            # Basic Validation to prevent IDs/invalid data being saved
            if session["field"] == "email" and ("@" not in val or "." not in val):
                return {"message": f"'{val}' doesn't look like a valid email. Please provide a full email address (e.g., name@gmail.com)."}
            if session["field"] == "phone":
                clean_phone = "".join(filter(str.isdigit, val))
                if len(clean_phone) < 10:
                    return {"message": f"'{val}' is not a valid 10-digit phone number. Please try again."}

            from core.db_service import db_update_lead, db_update_candidate
            if is_lead: await db_update_lead(session["target_id"], {session["field"]: val})
            else: await db_update_candidate(session["target_id"], {session["field"]: val})
            
            del SESSIONS[session_id]
            return {"message": f"✅ {session['field'].replace('_', ' ').capitalize()} updated successfully to: {val}"}

        if session["type"] == "clarify_lead_get":
            # User is providing ID or Email for a previous search
            id_match = re.search(r"#?(\d+)", message)
            email = extract_email(message)
            
            target = None
            if id_match:
                target = await db_get_lead(int(id_match.group(1)))
            elif email:
                # Search by email
                from management.models import Lead
                from asgiref.sync import sync_to_async
                target = await sync_to_async(lambda: Lead.objects.filter(email=email).values().first())()

            if target:
                del SESSIONS[session_id]
                return {
                    "message": f"🔍 Lead Found!\nID: #{target['id']}\nName: {target['name']}\nEmail: {target['email']}\nStatus: {target['status']}",
                    "data": target
                }
            return {"message": "Still couldn't find that lead. Please provide a valid ID (e.g. #11) or the exact Email."}

        # Catch-all for active sessions to prevent fallback
        return {"message": "I'm still processing your request. Could you please provide the detail I asked for?"}
    
    # 2. No active session, start new intent handling

    # -----------------------------------------
    # Greeting
    # -----------------------------------------
    if intent == "greeting":
        return {
            "message": "Hello! I can help with leads, candidates, tickets, reminders, and uploaded documents."
        }

    # -----------------------------------------
    # Lead Reports
    # -----------------------------------------
    if intent == "lead_report_total":
        from management.models import Lead
        from asgiref.sync import sync_to_async
        total = await sync_to_async(lambda: Lead.objects.count())()
        recent = await sync_to_async(lambda: list(Lead.objects.order_by("-id")[:12].values()))()
        
        if total == 0: return {"message": "The system currently has 0 leads."}
        
        items = [f"#{l['id']} {l['name']} | {l.get('company') or 'None'} | Status: {l['status'].upper()}" for l in recent]
        return {
            "message": f"📋 **Last {len(recent)} Leads**:\n" + "\n".join(items) + f"\n\n**(Total Database Leads: {total})**"
        }

    if intent == "lead_report_new":
        from management.models import Lead
        from asgiref.sync import sync_to_async
        today = timezone.now().date()
        leads = await sync_to_async(lambda: list(Lead.objects.filter(status="new", created_at__date=today).order_by("-created_at").values()))()
        if not leads:
             leads = await sync_to_async(lambda: list(Lead.objects.filter(status="new").order_by("-created_at")[:12].values()))()
             msg = "Last 12 New Leads"
        else:
             msg = f"Found {len(leads)} New Leads from Today"
             
        if not leads: return {"message": "No 'new' leads found in the system."}
        items = [f"#{l['id']} {l['name']} | {l.get('company') or 'None'} | Status: {l['status'].upper()}" for l in leads]
        return {
            "message": f"📋 **{msg}**:\n" + "\n".join(items)
        }

    if intent == "lead_report_contacted":
        from management.models import Lead
        from asgiref.sync import sync_to_async
        leads = await sync_to_async(lambda: list(Lead.objects.filter(status="contacted").order_by("-updated_at")[:12].values()))()
        if not leads: return {"message": "No 'contacted' leads found in the system."}
        
        items = [f"#{l['id']} {l['name']} | {l.get('company') or 'None'} | Status: CONTACTED" for l in leads]
        return {
            "message": f"📋 **Last {len(leads)} Contacted Leads**:\n" + "\n".join(items)
        }

    if intent == "lead_report_converted":
        SESSIONS[session_id] = {"type": "clarify_converted_leads", "initial_msg": message}
        return {
            "message": "Would you like to see ALL recent converted leads (up to 20), or just the LAST FEW (10)?",
            "options": ["All (20)", "Last Few (10)"]
        }

    if intent == "lead_report_converted_month":
        lower_msg = message.lower()
        months = ["january", "jan", "february", "feb", "march", "mar", "april", "apr", "may", "june", "jun", "july", "jul", "august", "aug", "september", "sep", "october", "oct", "november", "nov", "december", "dec", "this month"]
        if any(m in lower_msg for m in months):
            SESSIONS[session_id] = {"type": "clarify_converted_month"}
            return await route_intent(intent, message, session_id)
            
        SESSIONS[session_id] = {"type": "clarify_converted_month", "initial_msg": message}
        from datetime import datetime
        return {
            "message": "Which month would you like to check for converted leads?",
            "options": ["This month", "January", "February", "March", "April", "May", "June"]
        }

    if intent == "lead_report_lost":
        from management.models import Lead
        from asgiref.sync import sync_to_async
        leads = await sync_to_async(lambda: list(Lead.objects.filter(status="lost").order_by("-updated_at")[:10].values()))()
        if not leads: return {"message": "No lost leads found."}
        items = [f"#{l['id']} {l['name']} | {l.get('company', 'N/A')}" for l in leads]
        return {"message": f"🍂 Here are the last {len(leads)} lost leads:\n" + "\n".join(items)}

    if intent == "lead_conversion_rate":
        from management.models import Lead
        from asgiref.sync import sync_to_async
        
        total = await sync_to_async(lambda: Lead.objects.count())()
        converted = await sync_to_async(lambda: Lead.objects.filter(status="converted").count())()
        overall_rate = (converted / total * 100) if total > 0 else 0
        
        last_30_ids = await sync_to_async(lambda: list(Lead.objects.order_by("-id")[:30].values_list('id', flat=True)))()
        if last_30_ids:
            total_30 = len(last_30_ids)
            converted_30 = await sync_to_async(lambda: Lead.objects.filter(id__in=last_30_ids, status="converted").count())()
            rate_30 = (converted_30 / total_30 * 100)
        else:
            total_30 = 0
            rate_30 = 0
            
        return {
            "message": f"📊 **Lead Conversion Metrics**:\n\n📈 **Overall Conversion Rate**: {overall_rate:.1f}% ({converted} out of {total} leads)\n\n⚡ **Recently (Last 30 Days)**: {rate_30:.1f}%"
        }

    # -----------------------------------------
    # Create Lead
    # -----------------------------------------
    if intent == "create_lead":
        name = extract_name(message)
        email = extract_email(message)
        phone = extract_phone(message)
        role = extract_position(message)
        
        # Safety Check: Don't treat report keywords as names
        blacklist = ["contacted", "converted", "lost", "new", "report", "total", "rate", "%", "show", "list"]
        if name and any(k in name.lower() for k in blacklist) and not email and not phone:
            name = None

        session_data = {"type": "create_lead", "initial_msg": message}
        if name: session_data["name"] = name
        if email: session_data["email"] = email
        if phone: session_data["phone"] = phone
        if role: session_data["role"] = role

        if len(session_data) > 2: # We got some fields
            if session_data.get("name") and session_data.get("email") and session_data.get("phone") and session_data.get("role"):
                 # All found immediately (rare but possible)
                 try:
                    data = await db_create_lead({"name": name, "email": email, "phone": phone, "company": role, "status": "new"})
                    return {"message": f"✅ Lead {name} created with all details provided!"}
                 except: pass
            
            SESSIONS[session_id] = session_data
            # Figure out what's next
            if not session_data.get("name"): return {"message": "I'll help you create a lead. What is the name?"}
            if not session_data.get("email"): return {"message": f"Got it. What is the email for {name or 'them'}? (Must end in .com)"}
            if not session_data.get("phone"): return {"message": f"What is the 10-digit phone number?"}
            if not session_data.get("role"): return {"message": f"What is the role/company?"}
            return {"message": "What is the status of this lead?"}

        SESSIONS[session_id] = {"type": "create_lead", "initial_msg": message}
        return {"message": "Sure! Let's create a lead. What is the name?"}

    if intent == "update_lead":
        SESSIONS[session_id] = {"type": "update_lead", "initial_msg": message}
        return {"message": "Which lead do you want to update? Please provide ID, Email, or 10-digit Phone."}

    if intent == "update_candidate":
        SESSIONS[session_id] = {"type": "update_candidate", "initial_msg": message}
        return {"message": "Which candidate would you like to update? Please provide Name, ID (#), or Email."}

    if intent == "delete_lead":
        id_match = re.search(r"#?(\d+)", message)
        email = extract_email(message)
        phone = extract_phone(message)
        target_id = None
        
        from management.models import Lead
        from asgiref.sync import sync_to_async
        if id_match: target_id = int(id_match.group(1))
        elif email:
            target = await sync_to_async(lambda: Lead.objects.filter(email=email).first())()
            if target: target_id = target.id
        elif phone:
            target = await sync_to_async(lambda: Lead.objects.filter(phone__icontains=phone).first())()
            if target: target_id = target.id

        if not target_id:
            return {"message": "Lead not found. Please provide valid ID, Email, or Phone."}

        from core.db_service import db_delete_lead
        await db_delete_lead(target_id)
        return {"message": f"🗑️ Lead #{target_id} has been permanently deleted."}

    # -----------------------------------------
    # Create Candidate
    # -----------------------------------------
    if intent == "create_candidate" or intent == "candidate_create":
        name = extract_name(message)
        email = extract_email(message)
        role = extract_position(message)
        phone = extract_phone(message)

        if not name:
            SESSIONS[session_id] = {"type": "create_candidate", "initial_msg": message}
            return {"message": "Okay, let's add a candidate. What is their name?"}

        if not email:
            SESSIONS[session_id] = {"type": "create_candidate", "name": name, "initial_msg": message}
            return {"message": f"What is the email for {name}?"}

        if not role:
            SESSIONS[session_id] = {"type": "create_candidate", "name": name, "email": email, "initial_msg": message}
            return {"message": f"What role is {name} applying for?"}

        if not phone:
            SESSIONS[session_id] = {"type": "create_candidate", "name": name, "email": email, "role": role, "initial_msg": message}
            return {"message": f"What is the phone number for {name}?"}

        from core.db_service import db_create_candidate
        data = await db_create_candidate({
            "name": name,
            "email": email,
            "position_applied": role,
            "phone": phone,
            "status": "applied",
            "notes": message
        })

        await notify_candidate_update(data)

        return {
            "message": f"✅ Candidate {name} created for {role}.",
            "data": data
        }

    # -----------------------------------------
    # Create Ticket
    # -----------------------------------------
    if intent == "create_ticket":
        title = message.replace("create ticket", "").strip() or "New Support Request"
        data = await db_create_ticket({
            "title": title,
            "issue": message,
            "description": message,
            "status": "open",
            "priority": "medium"
        })
        await notify_new_ticket(data)
        return {
            "message": f"🎫 Ticket Created! '{data['title']}' is now in the system with ID #{data['id']}.",
            "data": data
        }

    # -----------------------------------------
    # Reminder
    # -----------------------------------------
    if intent == "create_reminder" or "remind" in lower:
        due = parse_due_date(message)

        data = await db_create_reminder({
            "title": message[:100],
            "description": message,
            "due_date": due,
            "is_done": False
        })

        await notify_reminder(data)

        return {
            "message": "Reminder created.",
            "data": data
        }

    # -----------------------------------------
    # Unified Search / Details
    # -----------------------------------------
    # Don't trigger search if it's already a delete action
    is_delete_action = intent in ["delete_lead", "delete_candidate", "delete_wizard"]
    if not is_delete_action and (intent == "search_person" or intent == "candidate_get" or intent == "lead_get" or (id_match and ("lead" in lower or "candidate" in lower or "ticket" in lower or "details" in lower))):
        # Force the intent if a specific ID is found with intent-related keywords
        if id_match:
            if "lead" in lower: intent = "lead_get"
            elif "candidate" in lower: intent = "candidate_get"
            elif "ticket" in lower: intent = "ticket_get"
            elif intent not in ["lead_get", "candidate_get", "ticket_get"]: intent = "lead_get" # Default to lead if ambiguous
            
        name = extract_name(message)
        id_match = re.search(r"#?(\d+)", message)
        email = extract_email(message)
        
        # If we have an ID or Email, skip the "Please provide a name" block
        if not name and not id_match and not email:
            return {"message": "Please provide a name, ID (#), or Email to look up."}
            
        search = {"leads": [], "candidates": []}
        if name:
            from core.db_service import db_search_by_name
            search = await db_search_by_name(name)
        
        has_leads = len(search["leads"]) > 0
        has_candidates = len(search["candidates"]) > 0
        
        # Scenario 1: Ambiguous (Found in BOTH)
        if has_leads and has_candidates and intent == "search_person":
            SESSIONS[session_id] = {"type": "clarify_search_type", "name": name}
            return {
                "message": f"I found '{name}' in both Leads and Candidates. Which one would you like to see details for?",
                "options": ["Lead", "Candidate"]
            }
            
        # Scenario 2: Only in Candidates
        if has_candidates and (intent == "candidate_get" or intent == "search_person"):
            # If multiple candidates, the candidate_get logic handles it below
            pass 
        
        # Scenario 3: Only in Leads
        if has_leads and (intent == "lead_get" or intent == "search_person"):
            # Redirect to lead_get logic
            if intent == "search_person": intent = "lead_get"

    if intent == "lead_get":
        id_match = re.search(r"#?(\d+)", message)
        email = extract_email(message)
        name = extract_name(message)
        
        target = None
        if id_match:
            from core.db_service import db_get_lead
            target = await db_get_lead(int(id_match.group(1)))
        elif email:
            from management.models import Lead
            from asgiref.sync import sync_to_async
            target = await sync_to_async(lambda: Lead.objects.filter(email=email).values().first())()
        elif name:
            search = await db_search_by_name(name)
            if len(search["leads"]) > 1:
                SESSIONS[session_id] = {"type": "clarify_lead_get", "name": name, "initial_msg": message}
                return {"message": f"I found {len(search['leads'])} leads named '{name}'. Please provide the ID (e.g. #11) or Email to specify."}
            target = search["leads"][0] if search["leads"] else None

        if not target:
            msg = "Lead not found."
            if name: msg += f" (Name: '{name}')"
            if email: msg += f" (Email: '{email}')"
            return {"message": msg}

        return {
            "message": f"🔍 Lead Details:\nID: #{target['id']}\nName: {target['name']}\nEmail: {target['email']}\nStatus: {target['status']}\nPhone: {target.get('phone', 'N/A')}\nCompany: {target.get('company', 'N/A')}",
            "data": target
        }

    if intent == "ticket_get":
        id_match = re.search(r"#?(\d+)", message)
        if not id_match:
            return {"message": "Please provide the ticket ID to show details (e.g., 'show ticket #4')."}
            
        target_id = int(id_match.group(1))
        from core.db_service import db_get_ticket
        target = await db_get_ticket(target_id)

        if not target:
            return {"message": f"Ticket #{target_id} not found."}

        return {
            "message": f"🎫 Ticket Details:\nID: #{target['id']}\nTitle: {target['title']}\nStatus: {target['status'].upper()}\nPriority: {target.get('priority', 'N/A').upper()}\n\n📝 Description:\n{target.get('description', 'No description provided.')}",
            "data": target
        }

    if intent == "lead_list":
        from core.db_service import db_get_all_leads
        data = await db_get_all_leads(limit=15)
        if not data:
            return {"message": "No leads found in the database."}
            
        items = [f"#{l['id']} {l['name']} | {l.get('company', 'N/A')} | Status: {l['status'].upper()}" for l in data]
        return {
            "message": f"📋 Last {len(data)} Leads:\n" + "\n".join(items),
            "data": data
        }

    if intent == "candidate_list":
        from core.db_service import db_get_all_candidates
        data = await db_get_all_candidates(limit=15)
        if not data:
            return {"message": "No candidates found."}
            
        items = [f"#{c['id']} {c['name']} | {c.get('position_applied', 'General')} | Status: {c.get('status', 'N/A').upper()}" for c in data]
        return {
            "message": f"📋 **Last {len(data)} Candidates**:\n" + "\n".join(items),
            "data": data
        }

    if intent.startswith("candidate_report_"):
        status_map = {
            "candidate_report_hired": "hired",
            "candidate_report_interview": "interview",
            "candidate_report_screening": "screening",
            "candidate_report_offered": "offered",
            "candidate_report_rejected": "rejected",
            "candidate_report_applied": "applied"
        }
        status_slug = status_map.get(intent)
        from management.models import Candidate
        from asgiref.sync import sync_to_async
        candidates = await sync_to_async(lambda: list(Candidate.objects.filter(status=status_slug).order_by("-updated_at")[:12].values()))()
        
        if not candidates:
            return {"message": f"No candidates found with status: **{status_slug.upper()}**."}
            
        items = [f"#{c['id']} {c['name']} | {c.get('position_applied') or 'N/A'} | Status: {c['status'].upper()}" for c in candidates]
        return {
            "message": f"📋 **{status_slug.upper()} Candidates** ({len(candidates)}):\n" + "\n".join(items)
        }

    # -----------------------------------------
    # Resume Analysis (NEW)
    # -----------------------------------------
    if intent == "analyze_resume":
        import os, json
        filename = None
        
        # Scenario A: Explicit target from session
        if "FILE_TARGET:" in message:
            filename = message.replace("FILE_TARGET:", "").strip()
        else:
            # Scenario B: Extract from natural language
            file_match = re.search(r"([\w\s\-\.\(\)]+\.(pdf|jpg|jpeg|png))", message, re.IGNORECASE)
            if file_match:
                filename = file_match.group(1).strip()
        
        if filename:
            # Verify file exists in uploaded_files.json
            try:
                with open("uploaded_files.json", "r") as f:
                    all_files = json.load(f)
                exists = any(f["name"].lower() == filename.lower() for f in all_files)
            except:
                exists = False
                
            if exists:
                # Try to find the physical file
                # Check multiple common locations where files might be sitting
                possible_paths = [
                    os.path.join("uploads", filename),
                    os.path.join("rag_data", filename),
                    os.path.join("django_backend", "uploads", filename), # Check Django uploads too
                    filename 
                ]
                
                file_path = None
                for p in possible_paths:
                    if os.path.exists(p):
                        file_path = p
                        break
                
                if not file_path:
                    # List directories for debugging if needed (Internal)
                    return {"message": f"I found '{filename}' in your database, but the physical file is missing from the server. Please re-upload this file to analyze it."}
                
                # Actual Extraction Flow
                from core.resume_service import extract_resume_data, format_resume_details
                from core.db_service import db_create_candidate
                from core.n8n_service import notify
                
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                
                extracted_data = await extract_resume_data(raw_bytes, filename)
                if not extracted_data:
                    return {"message": f"Gemini could not read details from '{filename}'. Is it a valid PDF?"}
                
                if isinstance(extracted_data, dict) and "error" in extracted_data:
                    return {"message": f"❌ Gemini Error: {extracted_data['error']}\n\nFile: {filename}"}
                
                notes = format_resume_details(extracted_data)
                
                exp_list = extracted_data.get("experience") or []
                pos_applied = exp_list[0].get("role") if exp_list and isinstance(exp_list, list) and len(exp_list) > 0 else "Parsed Applicant"

                candidate_data = {
                    "name": extracted_data.get("name") or "Extracted Candidate",
                    "email": extracted_data.get("email") or "no-email@talentpulse.local",
                    "phone": extracted_data.get("phone"),
                    "position_applied": pos_applied,
                    "status": "applied",
                    "notes": notes
                }

                
                new_candidate = await db_create_candidate(candidate_data)
                
                # Email notification
                email_payload = {
                    "candidate_id": new_candidate["id"],
                    "name": new_candidate["name"],
                    "details": notes
                }
                await notify("RESUME_ANALYZED", email_payload, "webhook/new-resume")
                
                return {
                    "message": f"✅ Analysis Complete for '{filename}'!\n\n**Candidate Created:** #{new_candidate['id']} {new_candidate['name']}\n\n**Key Details:**\n{notes[:600]}...",
                    "data": extracted_data
                }
            else:
                return {"message": f"I couldn't find a record for '{filename}' in my database. Would you like to upload it?", "options": ["Upload New Resume", "Analyze Old Resume"]}

        # If no filename mentioned, ask for choice
        SESSIONS[session_id] = {"type": "clarify_resume_choice"}
        return {
            "message": "I can help you analyze a resume. Would you like to pick an old one from the system, or upload a new one now?",
            "options": ["Analyze Old Resume", "Upload New Resume"]
        }

    if intent == "analyze_old_resume":
        import json
        try:
            with open("uploaded_files.json", "r") as f:
                all_files = json.load(f)
            # Filter for PDFs/Images
            resumes = [f["name"] for f in all_files if f["name"].lower().endswith((".pdf", ".jpg", ".jpeg", ".png"))]
        except:
            resumes = []
        
        if not resumes:
            return {"message": "I couldn't find any resumes in your uploaded documents. Would you like to upload a new one?"}
        
        SESSIONS[session_id] = {"type": "clarify_old_resume_selection"}
        return {
            "message": "Which old resume should I analyze?",
            "options": resumes[-6:] # Show last 6 uploads
        }

    if intent == "candidate_get":

        id_match = re.search(r"#?(\d+)", message)
        name = extract_name(message)
        
        target = None
        if id_match:
            from core.db_service import db_get_candidate
            target = await db_get_candidate(int(id_match.group(1)))
        elif name:
            from core.db_service import db_search_by_name
            search = await db_search_by_name(name)
            if len(search["candidates"]) > 1:
                SESSIONS[session_id] = {"type": "clarify_candidate_get", "name": name, "initial_msg": message}
                return {"message": f"I found {len(search['candidates'])} candidates named '{name}'. Provide ID (#) to specify."}
            target = search["candidates"][0] if search["candidates"] else None

        if not target: return {"message": "Candidate not found."}

        # Fetch History
        from core.db_service import db_get_candidate_history
        history = await db_get_candidate_history(target['id'])
        timeline = "\n".join([f"🕒 {h['changed_at'].strftime('%d %b')}: {h['status'].upper()} ({h['remarks'] or 'No remarks'})" for h in history])

        return {
            "message": f"🔍 Candidate Details:\nName: {target['name']}\nEmail: {target['email']}\nRole: {target['position_applied']}\n\n📍 Current Status: {target['status'].upper()}\n\n📜 Status History:\n{timeline if timeline else 'No history found.'}",
            "data": target
        }

    if intent == "ticket_list":
        data = await db_get_all_tickets(limit=10)
        if not data:
            return {"message": "No support tickets found."}
            
        items = [f"#{t['id']} {t['title']} | Priority: {t.get('priority', 'medium')} | Status: {t.get('status', 'open')}" for t in data]
        return {
            "message": f"📋 Last {len(data)} Tickets:\n" + "\n".join(items),
            "data": data
        }

    if intent == "reminder_list":
        data = await db_get_all_reminders(limit=10)
        if not data:
            return {"message": "No reminders found."}
            
        items = [f"#{r['id']} {r['title']} | Due: {r.get('due_date')} | Done: {r.get('is_done', False)}" for r in data]
        return {
            "message": f"📋 Last {len(data)} Reminders:\n" + "\n".join(items),
            "data": data
        }

    # -----------------------------------------
    # Update Lead
    # -----------------------------------------
    if intent == "update_candidate" or intent == "update_lead":
        is_lead = "lead" in intent
        name = extract_name(message)
        id_match = re.search(r"#?(\d+)", message)
        
        session_data = {"type": intent, "initial_msg": message}
        
        # Try to find the target immediately
        target = None
        if id_match:
            from core.db_service import db_get_lead, db_get_candidate
            target = await db_get_lead(int(id_match.group(1))) if is_lead else await db_get_candidate(int(id_match.group(1)))
        elif name:
            from core.db_service import db_search_by_name
            search = await db_search_by_name(name)
            pool = search["leads"] if is_lead else search["candidates"]
            if len(pool) == 1: target = pool[0]
            elif len(pool) > 1:
                SESSIONS[session_id] = session_data
                return {"message": f"I found multiple people named '{name}'. Please provide the ID (#) to specify."}

        if target:
            session_data["target_id"] = target["id"]
            session_data["current_data"] = target
            
            # Check if a field was mentioned (e.g., 'status' or 'stage')
            detected_field = None
            for f in ["name", "email", "phone", "status", "company", "role", "stage"]:
                if f in message.lower():
                    if f == "stage": detected_field = "status"
                    elif f == "role": detected_field = "position_applied"
                    else: detected_field = f
                    break
            
            if detected_field:
                session_data["field"] = detected_field
                SESSIONS[session_id] = session_data
                if detected_field == "status" and not is_lead:
                    return {
                        "message": f"Updating status for {target['name']}. Current: {target['status'].upper()}. Choose new:",
                        "options": ["Applied", "Screening", "Interview", "Offered", "Hired", "Rejected"]
                    }
                return {"message": f"Updating {detected_field} for {target['name']}. Current: {target.get(detected_field)}. New value?"}

        # If not found or no target yet, start identify session
        SESSIONS[session_id] = session_data
        return {"message": f"Which { 'lead' if is_lead else 'candidate' } would you like to update? (Provide Name or ID)"}
        if not field:
            return {"message": "What field do you want to update? (email, phone, status, or role)"}
            
        SESSIONS[session_id] = {"type": "update_candidate", "candidate_id": target_id, "field": field, "initial_msg": message}
        return {"message": f"Updating {field} for candidate #{target_id}. New value?"}

    # -----------------------------------------
    # Delete
    # -----------------------------------------
    if intent == "delete_wizard" or lower == "delete":
        SESSIONS[session_id] = {"type": "clarify_delete_type", "initial_msg": message}
        return {
            "message": "What would you like to delete: a Lead or a Candidate?",
            "options": ["Lead", "Candidate"]
        }

    if intent == "delete_lead":
        id_match = re.search(r"#?(\d+)", message)
        name = extract_name(message)
        email = extract_email(message)
        
        target_id = None
        if id_match:
            target_id = int(id_match.group(1))
        elif email:
            from management.models import Lead
            from asgiref.sync import sync_to_async
            target = await sync_to_async(lambda: Lead.objects.filter(email=email).first())()
            if target: target_id = target.id
        elif name:
            search = await db_search_by_name(name)
            if len(search["leads"]) > 1:
                SESSIONS[session_id] = {"type": "delete_lead_identify", "initial_msg": message}
                return {"message": f"I found multiple leads named '{name}'. Provide the ID to delete."}
            if search["leads"]: target_id = search["leads"][0]["id"]

        if not target_id:
            SESSIONS[session_id] = {"type": "delete_lead_identify", "initial_msg": message}
            return {"message": "Lead not found. Please provide a valid ID (#), Email, or Name to delete."}

        from core.db_service import db_delete_lead
        await db_delete_lead(target_id)
        return {"message": f"🗑️ Lead #{target_id} has been permanently deleted."}

    if intent == "delete_candidate":
        id_match = re.search(r"#?(\d+)", message)
        name = extract_name(message)
        email = extract_email(message)
        
        target_id = None
        if id_match:
            target_id = int(id_match.group(1))
        elif email:
            from management.models import Candidate
            from asgiref.sync import sync_to_async
            target = await sync_to_async(lambda: Candidate.objects.filter(email=email).first())()
            if target: target_id = target.id
        elif name:
            search = await db_search_by_name(name)
            if len(search["candidates"]) > 1:
                SESSIONS[session_id] = {"type": "delete_candidate_identify", "initial_msg": message}
                return {"message": f"Multiple candidates named '{name}' found. Provide ID to delete."}
            if search["candidates"]: target_id = search["candidates"][0]["id"]

        if not target_id:
            SESSIONS[session_id] = {"type": "delete_candidate_identify", "initial_msg": message}
            return {"message": "Candidate not found. Please provide a valid ID (#), Email, or Name to delete."}

        from core.db_service import db_delete_candidate
        await db_delete_candidate(target_id)
        return {"message": f"🗑️ Candidate #{target_id} has been permanently removed."}

    if intent == "delete_ticket":
        id_match = re.search(r"#?(\d+)", message)
        if not id_match:
            return {"message": "Please provide the ticket ID to delete (e.g., 'delete ticket #4')."}
        
        target_id = int(id_match.group(1))
        from core.db_service import db_delete_ticket
        deleted = await db_delete_ticket(target_id)
        
        if deleted:
            return {"message": f"🗑️ Ticket #{target_id} has been successfully deleted."}
        else:
            return {"message": f"❌ Ticket #{target_id} not found or already erased."}

    # -----------------------------------------
    # Fallback
    # -----------------------------------------
    return None