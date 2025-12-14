from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from database import get_db, User
from services.gmail_service import fetch_emails
from services.llm_service import classify_emails_batch, format_classifications_for_display
from services.gmail_label_service import apply_labels_batch

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
    
    # Fetch emails from Gmail
    try:
        print(f"\n{'='*80}")
        print(f"STEP 3: Fetching emails from Gmail")
        print(f"{'='*80}\n")
        result = fetch_emails(user, request.count, db)
        
        emails = result.get('emails', [])
        
        if not emails:
            return {
                "message": "No emails found",
                "email": request.email,
                "requested_count": request.count,
                "actual_count": 0,
                "emails": [],
                "classifications": [],
                "status": "no_emails"
            }
        
        # Step 4: Classify emails with LLM
        print(f"\n{'='*80}")
        print(f"STEP 4: Classifying emails with LLM")
        print(f"{'='*80}\n")
        classifications = classify_emails_batch(emails)
        
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
        
        # Step 5: Apply labels to emails in Gmail
        try:
            labeling_result = apply_labels_batch(user, emails, classifications, db)
        except Exception as label_error:
            print(f"⚠️  Error applying labels: {label_error}")
            import traceback
            print(traceback.format_exc())
            # Continue even if labeling fails - return classifications
            labeling_result = {
                'success_count': 0,
                'failed_count': len(classifications),
                'results': [],
                'total': 0,
                'error': str(label_error)
            }
        
        return {
            "message": "Emails fetched, classified, and labeled successfully",
            "email": request.email,
            "requested_count": request.count,
            "actual_count": result.get('actual_count', 0),
            "emails": emails,
            "classifications": formatted['classifications'],
            "summary": formatted['summary'],
            "labeling": {
                "success_count": labeling_result.get('success_count', 0),
                "failed_count": labeling_result.get('failed_count', 0),
                "total": labeling_result.get('total', 0),
                "results": labeling_result.get('results', [])
            },
            "status": "completed"
        }
    except Exception as e:
        print(f"Error in clean endpoint: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process emails: {str(e)}"
        )

