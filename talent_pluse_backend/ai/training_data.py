# TalentPulse Expanded Training Dataset
# This file contains the sample data for training the intent classification model.

EXPANDED_SAMPLES = [
    # ── 8. TYPO ROBUSTNESS (451–500) ──────────────────────────
    ("show all lead", "lead_list"), ("list lead", "lead_list"), ("get lead", "lead_list"), ("lsit leed", "lead_list"),
    ("details for 15", "lead_get"), ("show lead #15", "lead_get"), ("get info for 15", "lead_get"),
    ("Ashu details", "lead_get"), ("show Ashu", "lead_get"),
    ("show tikt", "ticket_list"), ("list tckets", "ticket_list"), ("get tkt", "ticket_list"), ("lsit tckts", "ticket_list"),
    ("show candit", "candidate_list"), ("list cnadidates", "candidate_list"), ("get canddtes", "candidate_list"), ("lsit candts", "candidate_list"),
    ("remnd me", "create_reminder"), ("creae lead", "create_lead"), ("registar lead", "create_lead"), ("crt led", "create_lead"),
    ("updaet email", "update_lead"), ("chng status", "update_lead"), ("upd phon", "update_lead"),
    ("deleete lead", "delete_lead"), ("remov led", "delete_lead"), ("del lead", "delete_lead"),
    ("deleete candit", "delete_candidate"), ("remov cand", "delete_candidate"), ("del candi", "delete_candidate"),
]

EXPANDED_SAMPLES += [
    # ── 1. GREETINGS & IDENTITY (0–20) ────────────────────────
    ("hi", "greeting"), ("hello", "greeting"), ("hey", "greeting"), ("yo", "greeting"),
    ("who are you", "identity"), ("what are you", "identity"), ("your name", "identity"),
    ("what can you do", "capabilities"), ("help me", "capabilities"), ("features", "capabilities"),
    ("bye", "farewell"), ("goodbye", "farewell"), ("see you", "farewell"),

    # ── 2. LEADS (CRUD & ANALYTICS) (151–200) ──────────────────
    ("show all leads", "lead_list"), ("list leads", "lead_list"), ("get leads", "lead_list"),
    ("create a new lead with name Rahul", "create_lead"), ("add lead Rahul", "create_lead"), ("crt lead Anita", "create_lead"),
    ("save contact Amit", "create_lead"), ("new lead for sales", "create_lead"), ("regstr lead Priya", "create_lead"),
    ("register lead Rahul at Google", "create_lead"), ("add lead Amit email amit@gmail.com", "create_lead"),
    ("get lead details for ID 101", "lead_get"), ("show lead 45", "lead_get"), ("gt led #10", "lead_get"), ("detals for Anita", "lead_get"),
    ("update lead name to Amit Sharma", "update_lead"), ("change lead 10 status", "update_lead"), ("update company for Anita from lead", "update_lead"), ("upd led #5", "update_lead"),
    ("delete lead with ID 45", "delete_lead"), ("remove lead 99", "delete_lead"), ("remove Anita from lead", "delete_lead"), ("del led 12", "delete_lead"),
    ("show leads created today", "lead_list"), ("filter leads by active", "lead_list"), ("lsit all laeds", "lead_list"),
    ("analyze lead sources", "system_analytics"), ("lead conversion probability", "system_analytics"),

    # ── 3. CANDIDATES (CRUD & MATCHING) (201–240) ──────────────
    ("show all candidates", "candidate_list"), ("list applicants", "candidate_list"),
    # Candidate Retrieval & Details
    ("who is Rahul", "search_person"),
    ("find Rahul profile", "search_person"),
    ("details of Rahul", "candidate_get"),
    ("info on candidate Rahul", "candidate_get"),
    ("lookup Rahul", "search_person"),
    ("show me Rahul", "candidate_get"),
    ("rahul details", "candidate_get"),
    ("get candidate Rahul", "candidate_get"),
    ("detals for Rahul", "candidate_get"), # typo
    ("find rahulll", "search_person"), # typo
    ("shw profile of rahul", "candidate_get"), # shorthand
    
    # Lead Retrieval
    ("info for lead Rahul", "lead_get"),
    ("lead rahul details", "lead_get"),
    ("who is lead Rahul", "lead_get"),
    ("get lead details for Rahul", "lead_get"),
    ("find lead Rahul", "lead_get"),
    ("shw lead rahul", "lead_get"), # shorthand
    
    # Status/Stage Updates
    ("change status to interview", "update_candidate"),
    ("update stage for Rahul", "update_candidate"),
    ("set Rahul to screening", "update_candidate"),
    ("move candidate 4 to hired", "update_candidate"),
    ("updte rahul status", "update_candidate"), # typo
    ("chng stage for rahul", "update_candidate"), # shorthand
    ("put rahul in offered stage", "update_candidate"),
    ("mark rahul as rejected", "update_candidate"),
    ("rahul is now hired", "update_candidate"),
    ("change rahul to screening", "update_candidate"),
    ("switch status for rahul", "update_candidate"),
    
    # Creation
    ("add new candidate Rahul", "candidate_create"),
    ("register Rahul as applicant", "candidate_create"),
    ("new candidate Rahul", "candidate_create"),
    ("create a candidate", "candidate_create"),
    ("add rahul to candidates", "candidate_create"),
    ("crte candidate rahul", "candidate_create"), # typo
    ("new applicant rahul", "candidate_create"),
    
    # Deletion
    ("remove candidate Rahul", "delete_candidate"),
    ("delete candidate #4", "delete_candidate"),
    ("remove lead 12", "delete_lead"),
    ("erase rahul from system", "delete_candidate"),
    ("discard this lead", "delete_lead"),
    ("del candidate rahul", "delete_candidate"), # shorthand
    
    # Scheduling
    ("schedule interview for Rahul", "update_candidate"),
    ("schdule intervew for rahul", "update_candidate"), # typos
    ("book interview rahul", "update_candidate"),
    ("set interview date", "update_candidate"),
    
    # Resume Analysis & Extraction (NEW)
    ("Analyze Resume", "analyze_resume"),
    ("analyze my resume", "analyze_resume"),
    ("extract info from resume", "analyze_resume"),
    ("get info from pratham r.pdf (1).pdf", "analyze_resume"),
    ("extract info from pratham r.pdf", "analyze_resume"),
    ("analyze old resume", "analyze_old_resume"),
    ("process new resume", "analyze_new_resume"),
    ("upload and analyze resume", "analyze_new_resume"),
    ("details from file pratham.pdf", "analyze_resume"),
    ("who is in this resume pratham.pdf", "analyze_resume"),
    ("info from my uploads", "analyze_old_resume"),

    ("filter candidates by Python", "candidate_list"), ("top candidates for AI", "candidate_list"),
    ("match candidate to job description", "candidate_match"), ("score candidate Rahul", "candidate_match"),

    # ── 4. REMINDERS & TICKETS (241–310) ──────────────────────
    ("show all reminders", "reminder_list"), ("list my reminders", "reminder_list"),
    ("create reminder for tomorrow", "create_reminder"), ("remind me at 5pm", "create_reminder"),
    ("delete reminder 3", "delete_reminder"), ("remove task 10", "delete_reminder"),
    ("update reminder task", "update_reminder"), ("mark reminder as done", "update_reminder"),
    ("show all tickets", "ticket_list"), ("list support requests", "ticket_list"),
    ("create new ticket", "create_ticket"), ("login not working", "create_ticket"),
    ("app is crashing", "create_ticket"), ("report a bug", "create_ticket"),
    ("delete ticket 55", "delete_ticket"), ("close ticket 12", "update_ticket"),
    ("update ticket status", "update_ticket"), ("assign ticket to me", "update_ticket"),

    # ── 5. DOCUMENTS & FILES (RAG) (1–150 & 311–350) ───────────
    ("read this file and explain it", "rag_doc_insight"), ("explain this document", "rag_doc_insight"),
    ("summarize this document", "rag_summarize"), ("summarize in 5 bullet points", "rag_summarize"),
    ("create executive summary", "rag_summarize"), ("summarize for me", "rag_summarize"),
    ("extract all emails from this text", "rag_extract"), ("extract phone numbers", "rag_extract"),
    ("extract dates and events", "rag_extract"), ("extract names", "rag_extract"),
    ("analyze strengths and weaknesses", "rag_analyze"), ("provide pros and cons", "rag_analyze"),
    ("identify patterns in this file", "rag_analyze"), ("SWOT analysis of this pdf", "rag_analyze"),
    ("rewrite this in better English", "rag_edit"), ("fix grammar here", "rag_edit"),
    ("make this more formal", "rag_edit"), ("shorten this text", "rag_edit"),
    ("upload a file", "file_management"), ("list all files", "file_management"),
    ("delete a file", "file_management"), ("rename document", "file_management"),

    # ── 6. SYSTEM & AUTOMATION (136–150 & 401–450) ─────────────
    ("create workflow from this", "automation_workflow"), ("generate step-by-step guide", "automation_workflow"),
    ("generate task list", "automation_workflow"), ("API logic for this", "automation_workflow"),
    ("generate dashboard insights", "system_analytics"), ("show performance trends", "system_analytics"),
    ("revenue forecast", "system_analytics"), ("KPI report", "system_analytics"),
    ("detect anomalies", "system_analytics"), ("optimize operations", "system_analytics"),

    # ── 7. FALLBACK & CHAT (351–400) ──────────────────────────
    ("answer this question", "general_chat"), ("explain this text", "general_chat"),
    ("generate text for me", "general_chat"), ("write a message", "general_chat"),
    ("okay", "fallback"), ("hmm", "fallback"), ("not sure", "fallback"), ("random", "fallback"),
]

# Add more variety for the "Create Rahul" style
EXPANDED_SAMPLES += [
    (f"create {role} name {name}", f"create_{role}")
    for role in ["candidate", "lead"]
    for name in ["Rahul", "Amit", "Priya", "Sonia", "John"]
]

EXPANDED_SAMPLES += [
    (f"add {role} {name} with age {age}", f"create_{role}")
    for role in ["candidate", "lead"]
    for name in ["Rahul", "Amit"]
    for age in ["22", "25", "30"]
]
EXPANDED_SAMPLES += [
    ("change status for rahul", "update_candidate"),
    ("update candidate status rahul", "update_candidate"),
    ("move rahul to interview stage", "update_candidate"),
    ("change candidate 4 stage", "update_candidate"),
    ("update status for candidate mehak", "update_candidate"),
    ("show details for rahul", "candidate_get"),
    ("get info about candidate rahul", "candidate_get"),
    ("candidate profile rahul", "candidate_get"),
    ("show rahul history", "candidate_get"),
    ("view rahul details", "candidate_get"),
    ("details for rahul", "candidate_get"),
    ("who is rahul", "candidate_get"),
    ("show details for create rahul", "candidate_get"), # Handle existing noise names
    ("update status for create rahul", "update_candidate"),
]
