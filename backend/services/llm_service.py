"""
LLM Service for Email Classification
Uses OpenAI to classify emails into categories
"""
from openai import OpenAI
import config
import json
from typing import List, Dict, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lazy-load OpenAI client to avoid initialization errors
_client: Optional[OpenAI] = None

def get_openai_client() -> OpenAI:
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        # Check if API key is valid (not placeholder)
        api_key = config.OPENAI_API_KEY
        if not api_key or api_key == "sk-placeholder-for-now" or api_key == "placeholder":
            raise ValueError("OpenAI API key not configured. Please add your OPENAI_API_KEY to backend/.env file. Get one from https://platform.openai.com/api-keys")
        
        try:
            # Try to create client - handle version incompatibility
            _client = OpenAI(api_key=config.OPENAI_API_KEY)
        except (TypeError, AttributeError) as e:
            # Handle version incompatibility with httpx
            if 'proxies' in str(e) or 'unexpected keyword' in str(e):
                # Create httpx client explicitly to avoid proxy issues
                import httpx
                try:
                    http_client = httpx.Client(timeout=60.0)
                    _client = OpenAI(
                        api_key=config.OPENAI_API_KEY,
                        http_client=http_client
                    )
                except Exception as e2:
                    # If that also fails, try without http_client
                    print(f"Warning: Could not create OpenAI client with custom http_client: {e2}")
                    # Try with minimal initialization
                    _client = OpenAI(api_key=config.OPENAI_API_KEY)
            else:
                raise
    return _client

# Category definitions
CATEGORIES = {
    "IMPORTANT_ACTION": {
        "name": "Important Action Required",
        "description": "Emails requiring user action (meetings, tasks, urgent items, responses needed)",
        "label": "IMPORTANT_ACTION"
    },
    "FYI_READ_LATER": {
        "name": "FYI / Read Later",
        "description": "Informational emails that can be read later (newsletters, articles, updates)",
        "label": "FYI_READ_LATER"
    },
    "MARKETING": {
        "name": "Marketing / Promotions",
        "description": "Promotional and marketing content (sales, deals, ads, promotional newsletters)",
        "label": "MARKETING"
    },
    "AUTOMATED": {
        "name": "Automated / Transaction",
        "description": "Automated and transactional emails (receipts, confirmations, notifications, system messages)",
        "label": "AUTOMATED"
    },
    "LOW_VALUE_NOISE": {
        "name": "Low Value / Noise",
        "description": "Low-value emails, spam-like content, or noise that doesn't require attention",
        "label": "LOW_VALUE_NOISE"
    },
    "UNKNOWN": {
        "name": "Unknown / Unclassified",
        "description": "Emails that could not be classified (fallback category)",
        "label": "UNKNOWN"
    }
}


def create_classification_prompt(emails: List[Dict]) -> str:
    """
    Create a prompt for classifying multiple emails
    Optimized for speed: shorter body previews, more emails per batch
    """
    categories_text = "\n".join([
        f"{i+1}. {cat['name']} ({key}): {cat['description']}"
        for i, (key, cat) in enumerate(CATEGORIES.items())
    ])
    
    emails_text = ""
    for i, email in enumerate(emails, 1):
        emails_text += f"\n--- Email {i} ---\n"
        emails_text += f"Subject: {email.get('subject', 'No Subject')}\n"
        emails_text += f"From: {email.get('from', 'Unknown')}\n"
        # Use snippet if available (faster than body), otherwise short body preview
        snippet = email.get('snippet', '')
        if snippet:
            emails_text += f"Content: {snippet[:300]}\n"
        else:
            body = email.get('body', '')
            if body:
                emails_text += f"Content: {body[:300]}{'...' if len(body) > 300 else ''}\n"
    
    num_emails = len(emails)
    prompt = f"""You are an email classification assistant. Classify each email into one of these categories:

{categories_text}

CRITICAL REQUIREMENTS:
1. You MUST return exactly {num_emails} classifications, one for each email provided
2. Return classifications in the EXACT same order as the emails (Email 1 = first classification, Email 2 = second, etc.)
3. If you cannot confidently classify an email, use category "UNKNOWN" with confidence 0.0
4. Every email must have a classification - do not skip any emails

For each email, return a JSON object with:
- category: one of the category keys (IMPORTANT_ACTION, FYI_READ_LATER, MARKETING, AUTOMATED, LOW_VALUE_NOISE, or UNKNOWN if uncertain)
- confidence: a number between 0.0 and 1.0 indicating confidence
- reason: a brief explanation (1-2 sentences) for the classification

Emails to classify ({num_emails} total):
{emails_text}

Return ONLY valid JSON array with exactly {num_emails} classifications in this format:
[
  {{
    "category": "IMPORTANT_ACTION",
    "confidence": 0.95,
    "reason": "Meeting invitation requires response"
  }},
  {{
    "category": "MARKETING",
    "confidence": 0.85,
    "reason": "Promotional newsletter"
  }},
  ...
]

Remember: You must return exactly {num_emails} classifications, one for each email, in order.
"""
    return prompt


def classify_single_batch(batch: List[Dict], batch_num: int, total_batches: int) -> List[Dict]:
    """
    Classify a single batch of emails (for parallel processing)
    Includes rate limit handling with retries
    """
    try:
        # Check API key first
        api_key = config.OPENAI_API_KEY
        if not api_key or api_key == "sk-placeholder-for-now" or api_key == "placeholder":
            error_msg = "OpenAI API key not configured. Please add your OPENAI_API_KEY to backend/.env file. Get one from https://platform.openai.com/api-keys"
            raise ValueError(error_msg)
        
        # Create prompt for this batch
        prompt = create_classification_prompt(batch)
        
        # Call OpenAI API with retry logic for rate limits
        client = get_openai_client()
        
        max_retries = 3
        retry_delay = 20  # Start with 20 seconds (OpenAI's suggested wait time)
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Fast and cost-efficient
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an email classification assistant. Always return valid JSON only, no additional text."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000  # Increased for larger batches (25 emails need ~1500-2000 tokens)
                )
                break  # Success, exit retry loop
                
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error
                if '429' in error_str or 'rate_limit' in error_str.lower() or 'rate limit' in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                        print(f"  ⏳ Batch {batch_num}: Rate limit hit, waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise  # Max retries reached
                else:
                    raise  # Not a rate limit error, re-raise immediately
        
        # Parse response
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Better JSON parsing with validation
        classifications = None
        try:
            classifications = json.loads(content)
        except json.JSONDecodeError as json_error:
            # Try to extract JSON from malformed response
            print(f"  ⚠️  Batch {batch_num}: JSON parse error, attempting recovery: {json_error}")
            # Try to find JSON array in the response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    classifications = json.loads(json_match.group(0))
                    print(f"  ✅ Batch {batch_num}: Recovered JSON from malformed response")
                except:
                    pass
            
            if classifications is None:
                raise ValueError(f"Could not parse JSON response: {json_error}. Response preview: {content[:200]}")
        
        # Validate JSON structure
        if not isinstance(classifications, list):
            raise ValueError(f"Expected JSON array, got {type(classifications)}. Response: {content[:200]}")
        
        # Validate and add email IDs, ensuring we have classifications for ALL emails
        results = []
        expected_count = len(batch)
        actual_count = len(classifications)
        
        # Process valid classifications
        for j, classification in enumerate(classifications):
            if j < expected_count:
                # Validate classification structure
                if not isinstance(classification, dict):
                    print(f"  ⚠️  Batch {batch_num}: Classification {j} is not a dict, creating fallback")
                    classification = {
                        'category': 'UNKNOWN',
                        'confidence': 0.0,
                        'reason': 'Invalid classification format from LLM'
                    }
                
                # Ensure required fields exist
                if 'category' not in classification:
                    classification['category'] = 'UNKNOWN'
                if 'confidence' not in classification:
                    classification['confidence'] = 0.0
                if 'reason' not in classification:
                    classification['reason'] = 'No reason provided by LLM'
                
                # Validate category is valid
                if classification['category'] not in CATEGORIES:
                    print(f"  ⚠️  Batch {batch_num}: Invalid category '{classification['category']}', using UNKNOWN")
                    classification['category'] = 'UNKNOWN'
                    classification['confidence'] = 0.0
                
                classification['email_id'] = batch[j]['id']
                classification['email_subject'] = batch[j].get('subject', 'No Subject')
                results.append(classification)
        
        # Check if we're missing classifications and pad with UNKNOWN
        if len(results) < expected_count:
            missing_count = expected_count - len(results)
            print(f"  ⚠️  Batch {batch_num}: Missing {missing_count} classifications (got {len(results)}, expected {expected_count}), padding with UNKNOWN")
            
            # Add UNKNOWN classifications for missing emails
            for j in range(len(results), expected_count):
                results.append({
                    'email_id': batch[j]['id'],
                    'email_subject': batch[j].get('subject', 'No Subject'),
                    'category': 'UNKNOWN',
                    'confidence': 0.0,
                    'reason': 'LLM did not return classification for this email'
                })
        
        print(f"  ✅ Batch {batch_num}/{total_batches}: Classified {len(results)}/{expected_count} emails")
        return results
        
    except Exception as e:
        print(f"  ❌ Batch {batch_num} error: {str(e)}")
        # Return error classifications for this batch
        return [{
            'email_id': email['id'],
            'email_subject': email.get('subject', 'No Subject'),
            'category': 'ERROR',
            'confidence': 0.0,
            'reason': f'Classification error: {str(e)}'
        } for email in batch]


def classify_emails_batch(emails: List[Dict]) -> List[Dict]:
    """
    Classify a batch of emails using OpenAI
    Optimized for speed: larger batches, concurrent processing
    """
    if not emails:
        return []
    
    # Optimized batch size - process more emails per request
    # Balance between speed and rate limits
    # Token estimate: ~150 tokens per email (subject + from + snippet)
    # 20 emails = ~3000 input tokens + ~300 prompt = ~3300 tokens (well under 128k limit)
    batch_size = 20  # Optimized for 10 concurrent workers
    all_classifications = []
    
    print(f"\n{'='*60}")
    print(f"LLM CLASSIFICATION: Processing {len(emails)} emails in batches of {batch_size}")
    print(f"{'='*60}\n")
    
    # Create batches
    batches = []
    for i in range(0, len(emails), batch_size):
        batch_num = i // batch_size + 1
        batches.append((batch_num, emails[i:i + batch_size]))
    
    total_batches = len(batches)
    
    # Rate limit configuration:
    # Free tier: 3 RPM → sequential processing
    # Tier 1 ($5+): 60 RPM → up to 10 concurrent workers (safe for max 200 emails)
    # Tier 2+ ($50+): 500+ RPM → can use even more workers
    
    # Optimized for Tier 1: 10 workers with batch size 20
    # Max scenario: 200 emails = 10 batches, all in parallel = 10 RPM (well under 60 RPM limit)
    max_workers = 10  # Tier 1: 10 concurrent batches (safe for 60 RPM, max 200 emails)
    # For free tier users, change this back to 1
    
    if max_workers == 1:
        print(f"Processing {total_batches} batches sequentially (free tier mode)...\n")
    else:
        print(f"Processing {total_batches} batches with {max_workers} concurrent workers (Tier 1+ mode)...\n")
    
    if max_workers == 1:
        # Sequential processing for free tier (3 RPM limit)
        for batch_num, batch in batches:
            try:
                results = classify_single_batch(batch, batch_num, total_batches)
                all_classifications.extend(results)
                # Small delay between batches to stay under rate limit
                if batch_num < total_batches:
                    time.sleep(2)  # 2 second delay between batches
            except Exception as e:
                print(f"  ❌ Batch {batch_num} failed: {e}")
                # Add error classifications
                for email in batch:
                    all_classifications.append({
                        'email_id': email['id'],
                        'email_subject': email.get('subject', 'No Subject'),
                        'category': 'ERROR',
                        'confidence': 0.0,
                        'reason': f'Batch processing error: {str(e)}'
                    })
    else:
        # Parallel processing for Tier 1+ (60+ RPM limit)
        # No delays needed - rate limits are high enough
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batch processing tasks
            future_to_batch = {
                executor.submit(classify_single_batch, batch, batch_num, total_batches): (batch_num, batch)
                for batch_num, batch in batches
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_num, batch = future_to_batch[future]
                try:
                    results = future.result()
                    all_classifications.extend(results)
                except Exception as e:
                    print(f"  ❌ Batch {batch_num} failed: {e}")
                    # Add error classifications
                    for email in batch:
                        all_classifications.append({
                            'email_id': email['id'],
                            'email_subject': email.get('subject', 'No Subject'),
                            'category': 'ERROR',
                            'confidence': 0.0,
                            'reason': f'Batch processing error: {str(e)}'
                        })
    
    print(f"\n✅ Classification complete: {len(all_classifications)}/{len(emails)} emails classified")
    
    return all_classifications


def get_category_info(category_key: str) -> Dict:
    """
    Get information about a category
    """
    return CATEGORIES.get(category_key, {
        "name": "Unknown",
        "description": "Unknown category",
        "label": "UNKNOWN"
    })


def format_classifications_for_display(classifications: List[Dict]) -> Dict:
    """
    Format classifications for display/response
    Groups by category and provides summary
    """
    summary = {cat: 0 for cat in CATEGORIES.keys()}
    summary['ERROR'] = 0  # Keep ERROR for backward compatibility
    
    for classification in classifications:
        category = classification.get('category', 'ERROR')
        summary[category] = summary.get(category, 0) + 1
    
    return {
        'classifications': classifications,
        'summary': summary,
        'total': len(classifications)
    }

