from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from database import (
    get_db,
    User,
    EmailRun,
    EmailRunStatus,
    EmailItem,
    EmailItemStatus,
)
from services.gmail_service import fetch_emails
from services.llm_service import classify_emails_batch, format_classifications_for_display
from services.gmail_label_service import apply_labels_batch
import time
from datetime import datetime

router = APIRouter(prefix="/api", tags=["clean"])


class CleanRequest(BaseModel):
    email: str = Field(..., description="User's email address")
    count: int = Field(..., description="Number of emails to clean (1-100)")

    @validator('count')
    def validate_count(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Count must be between 1 and 100')
        return v

    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('Valid email address is required')
        return v


@router.post("/clean")
async def start_clean(
    request: CleanRequest,
    db: Session = Depends(get_db)
):
    """
    Start the email cleaning process for a user.
    Validates the user exists and the count is between 1-100.
    """
    start = time.perf_counter()
    # NOTE: keep type hints Python 3.9-compatible
    run = None  # type: ignore[assignment]
    # Get user from database
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate count
    if request.count < 1 or request.count > 100:
        raise HTTPException(
            status_code=400, 
            detail="Email count must be between 1 and 100"
        )
    # Create an EmailRun record (NEW -> PROCESSING -> COMPLETED/FAILED)
    run = EmailRun(user_id=user.id, requested_count=request.count, status=EmailRunStatus.NEW)
    db.add(run)
    db.commit()
    db.refresh(run)

    run.status = EmailRunStatus.PROCESSING
    db.commit()

    validate_request_time = time.perf_counter() 
    # Fetch emails from Gmail
    try:
        print(f"\n{'='*80}")
        print(f"STEP 3: Fetching emails from Gmail")
        print(f"{'='*80}\n")
        result = fetch_emails(user, request.count, db)
        
        emails = result.get('emails', [])
        
        if not emails:
            run.status = EmailRunStatus.COMPLETED
            run.finished_at = datetime.utcnow()
            db.commit()
            return {
                "run_id": run.id,
                "message": "No emails found",
                "email": request.email,
                "requested_count": request.count,
                "actual_count": 0,
                "emails": [],
                "classifications": [],
                "status": "no_emails"
            }
        fetched_emails_time = time.perf_counter()

        # ------------------------------------------------------------------
        # Ingestion: create EmailItem rows (global-per-user uniqueness)
        # - Skip if the gmail_message_id already exists in DB (including FAILED).
        # ------------------------------------------------------------------
        existing_items = (
            db.query(EmailItem)
            .filter(EmailItem.user_id == user.id)
            .all()
        )
        existing_by_gmail_id = {item.gmail_message_id: item for item in existing_items}

        emails_to_process = []
        items_to_process = []

        for email in emails:
            gmail_id = email.get("id")
            if not gmail_id:
                continue

            if gmail_id in existing_by_gmail_id:
                # Already tracked for this user → skip (includes FAILED per your preference)
                continue

            item = EmailItem(
                user_id=user.id,
                run_id=run.id,
                gmail_message_id=gmail_id,
                status=EmailItemStatus.NEW,
                attempt_count=0,
                last_error=None,
            )
            db.add(item)
            items_to_process.append(item)
            emails_to_process.append(email)

        db.commit()

        # Helper: build rollup stats for *all fetched emails* (new + existing)
        def build_rollup_for_fetched_emails():
            fetched_ids = [e.get("id") for e in emails if e.get("id")]
            if not fetched_ids:
                return [], {"summary": {}, "classifications": []}, {"success_count": 0, "failed_count": 0, "total": 0, "results": []}

            items = (
                db.query(EmailItem)
                .filter(
                    EmailItem.user_id == user.id,
                    EmailItem.gmail_message_id.in_(fetched_ids),
                )
                .all()
            )

            classifications_from_db = []
            for item in items:
                classifications_from_db.append({
                    "email_id": item.gmail_message_id,
                    "category": item.category or "UNKNOWN",
                    "confidence": item.confidence if item.confidence is not None else 0.0,
                    "reason": item.reason or (item.last_error or ""),
                })

            formatted_all = format_classifications_for_display(classifications_from_db)

            success_count = sum(1 for i in items if i.status == EmailItemStatus.SUCCESS)
            failed_count = sum(1 for i in items if i.status == EmailItemStatus.FAILED)
            results = [
                {
                    "email_id": i.gmail_message_id,
                    "label": i.category or "UNKNOWN",
                    "success": i.status == EmailItemStatus.SUCCESS,
                    "error": None if i.status == EmailItemStatus.SUCCESS else (i.last_error or "Failed"),
                }
                for i in items
            ]

            labeling_rollup = {
                "success_count": success_count,
                "failed_count": failed_count,
                "total": len(items),
                "results": results,
            }

            return fetched_ids, formatted_all, labeling_rollup

        if not emails_to_process:
            run.status = EmailRunStatus.COMPLETED
            run.finished_at = datetime.utcnow()
            run.error = None
            db.commit()
            fetched_ids, formatted_all, labeling_rollup = build_rollup_for_fetched_emails()
            return {
                "run_id": run.id,
                "message": "All fetched emails were already processed (no new work needed)",
                "email": request.email,
                "requested_count": request.count,
                "actual_count": len(fetched_ids),
                "emails": emails,
                "classifications": formatted_all["classifications"],
                "summary": formatted_all["summary"],
                "labeling": labeling_rollup,
                "status": "completed",
            }

        # Claim work: mark selected items PROCESSING and increment attempt_count
        for item in items_to_process:
            item.status = EmailItemStatus.PROCESSING
            item.attempt_count = (item.attempt_count or 0) + 1
            item.last_error = None
        db.commit()
        
        # Step 4: Classify emails with LLM
        print(f"\n{'='*80}")
        print(f"STEP 4: Classifying emails with LLM")
        print(f"{'='*80}\n")
        classifications = classify_emails_batch(emails_to_process)

        # Persist classification results; keep EmailItem in PROCESSING until labeling succeeds.
        items_by_gmail_id = {item.gmail_message_id: item for item in items_to_process}
        for c in classifications:
            gmail_id = c.get("email_id")
            item = items_by_gmail_id.get(gmail_id)
            if not item:
                continue
            item.category = c.get("category")
            item.confidence = c.get("confidence")
            item.reason = c.get("reason")
            if c.get("category") == "ERROR":
                item.last_error = c.get("reason") or "LLM classification error"
        db.commit()
        
        # Format for response
        formatted = format_classifications_for_display(classifications)
        
        # Print summary
        print(f"\n{'='*80}")
        print("CLASSIFICATION SUMMARY:")
        print(f"{'='*80}")
        for category, count in formatted['summary'].items():
            if count > 0:
                print(f"  {category}: {count}")
        print(f"{'='*80}\n")
        classified_emails_time = time.perf_counter() 
        # Step 5: Apply labels to emails in Gmail
        labeling_error_message = None
        try:
            labeling_result = apply_labels_batch(user, emails_to_process, classifications, db)
        except Exception as label_error:
            print(f"⚠️  Error applying labels: {label_error}")
            import traceback
            print(traceback.format_exc())
            labeling_error_message = str(label_error)
            # Continue even if labeling fails - return classifications
            labeling_result = {
                'success_count': 0,
                'failed_count': len(classifications),
                'results': [],
                'total': 0,
                'error': str(label_error)
            }
        
        # Update per-email statuses based on labeling results
        success_ids = set()
        failed_ids = set()
        for r in (labeling_result.get("results") or []):
            gmail_id = r.get("email_id")
            if not gmail_id:
                continue
            if r.get("success") is True:
                success_ids.add(gmail_id)
            else:
                failed_ids.add(gmail_id)

        for item in items_to_process:
            if item.gmail_message_id in success_ids:
                item.status = EmailItemStatus.SUCCESS
                item.last_error = None
            elif item.gmail_message_id in failed_ids or labeling_error_message:
                item.status = EmailItemStatus.FAILED
                item.last_error = labeling_error_message or labeling_result.get("error") or "Labeling failed"
        db.commit()

        # Retry policy: retry FAILED emails once (attempt_count < 2)
        retry_items = [
            item for item in items_to_process
            if item.status == EmailItemStatus.FAILED and (item.attempt_count or 0) < 2
        ]
        if retry_items:
            retry_ids = {i.gmail_message_id for i in retry_items}
            retry_emails = [e for e in emails_to_process if e.get("id") in retry_ids]

            for item in retry_items:
                item.status = EmailItemStatus.PROCESSING
                item.attempt_count = (item.attempt_count or 0) + 1
                item.last_error = None
            db.commit()

            retry_classifications = classify_emails_batch(retry_emails)
            retry_items_by_id = {i.gmail_message_id: i for i in retry_items}
            for c in retry_classifications:
                gmail_id = c.get("email_id")
                item = retry_items_by_id.get(gmail_id)
                if not item:
                    continue
                item.category = c.get("category")
                item.confidence = c.get("confidence")
                item.reason = c.get("reason")
                if c.get("category") == "ERROR":
                    item.last_error = c.get("reason") or "LLM classification error (retry)"
            db.commit()

            try:
                retry_labeling_result = apply_labels_batch(user, retry_emails, retry_classifications, db)
                retry_label_error = None
            except Exception as e:
                retry_labeling_result = {"results": [], "error": str(e)}
                retry_label_error = str(e)

            retry_success_ids = set()
            for r in (retry_labeling_result.get("results") or []):
                gmail_id = r.get("email_id")
                if not gmail_id:
                    continue
                if r.get("success") is True:
                    retry_success_ids.add(gmail_id)

            for item in retry_items:
                if item.gmail_message_id in retry_success_ids:
                    item.status = EmailItemStatus.SUCCESS
                    item.last_error = None
                else:
                    item.status = EmailItemStatus.FAILED
                    item.last_error = retry_label_error or retry_labeling_result.get("error") or item.last_error or "Retry failed"
            db.commit()
        labeled_emails_time = time.perf_counter() 
        print(f"Time taken to validate request: {validate_request_time - start} seconds")
        print(f"Time taken to fetch emails: {fetched_emails_time - validate_request_time} seconds")
        print(f"Time taken to classify emails: {classified_emails_time - fetched_emails_time} seconds")
        print(f"Time taken to label emails: {labeled_emails_time - classified_emails_time} seconds")
   
       
        # Mark run completed (store any non-fatal labeling error for debugging)
        run.status = EmailRunStatus.COMPLETED
        run.finished_at = datetime.utcnow()
        run.error = labeling_error_message
        db.commit()

        # Return rollup for *all fetched emails* so summary includes already-processed ones too
        fetched_ids, formatted_all, labeling_rollup = build_rollup_for_fetched_emails()
        return {
            "run_id": run.id,
            "message": "Emails fetched, classified, and labeled successfully",
            "email": request.email,
            "requested_count": request.count,
            "actual_count": len(fetched_ids),
            "emails": emails,
            "classifications": formatted_all["classifications"],
            "summary": formatted_all["summary"],
            "labeling": labeling_rollup,
            "status": "completed"
        }
    except Exception as e:
        # Mark run failed (best-effort)
        try:
            if run is not None:
                run.status = EmailRunStatus.FAILED
                run.finished_at = datetime.utcnow()
                run.error = str(e)
                db.commit()
        except Exception:
            # Don't mask the original error if DB update fails
            pass
        print(f"Error in clean endpoint: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process emails: {str(e)}"
        )

