"""
Gmail Label Service
Handles creating and applying labels to emails using Gmail API
Uses batchModify for fast, efficient labeling
"""
from typing import List, Dict, Optional, Tuple
from database import User
from services.gmail_service import get_gmail_service
from services.llm_service import CATEGORIES


def get_label_name(category: str) -> str:
    """
    Map classification category to Gmail label name
    """
    # Use the category key as the label name (e.g., IMPORTANT_ACTION -> IMPORTANT_ACTION)
    if category in CATEGORIES:
        return category
    return "UNKNOWN"


def get_label_color(category: str) -> Dict[str, str]:
    """
    Get Gmail label color for a category
    Returns color object with textColor and backgroundColor
    Uses ONLY Gmail API allowed colors from the predefined palette
    """
    color_map = {
        'IMPORTANT_ACTION': {
            'textColor': '#ffffff',
            'backgroundColor': '#fb4c2f'  # Red (allowed: closest to #ea4335)
        },
        'FYI_READ_LATER': {
            'textColor': '#ffffff',
            'backgroundColor': '#16a766'  # Green (allowed: closest to #34a853)
        },
        'MARKETING': {
            'textColor': '#000000',
            'backgroundColor': '#fad165'  # Yellow (allowed: closest to #fbbc04)
        },
        'AUTOMATED': {
            'textColor': '#ffffff',
            'backgroundColor': '#4986e7'  # Blue (allowed: closest to #4285f4)
        },
        'LOW_VALUE_NOISE': {
            'textColor': '#ffffff',
            'backgroundColor': '#666666'  # Grey (allowed: closest to #5f6368)
        },
        'UNKNOWN': {
            'textColor': '#000000',
            'backgroundColor': '#ffad47'  # Orange (allowed: closest to #ff9800)
        }
    }
    
    return color_map.get(category, {
        'textColor': '#000000',
        'backgroundColor': '#cccccc'  # Default grey (allowed color)
    })


def create_label_if_not_exists(service, label_name: str, category: str = None) -> Optional[str]:
    """
    Create a Gmail label if it doesn't exist
    Returns the label ID
    """
    try:
        # First, check if label already exists
        labels = service.users().labels().list(userId='me').execute()
        for label in labels.get('labels', []):
            if label['name'] == label_name:
                # Label exists, check if we need to update color
                label_id = label['id']
                if category:
                    color = get_label_color(category)
                    # Try to update color if it's different
                    try:
                        # Check if color is already set correctly
                        existing_color = label.get('color', {})
                        existing_bg = existing_color.get('backgroundColor', '')
                        existing_text = existing_color.get('textColor', '')
                        
                        if (existing_bg != color.get('backgroundColor') or
                            existing_text != color.get('textColor')):
                            print(f"  🎨 Updating label color for '{label_name}': {color}")
                            service.users().labels().patch(
                                userId='me',
                                id=label_id,
                                body={'color': color}
                            ).execute()
                            print(f"  ✅ Updated label color: {label_name} (bg={color['backgroundColor']})")
                        else:
                            print(f"  ℹ️  Label '{label_name}' already has correct color")
                    except Exception as color_error:
                        error_msg = str(color_error)
                        print(f"  ⚠️  Could not update label color for '{label_name}': {error_msg}")
                        # Try to extract more details if it's an API error
                        if hasattr(color_error, 'content'):
                            print(f"     Error details: {color_error.content}")
                        # Continue anyway - label exists, just without color update
                return label_id
        
        # Label doesn't exist, create it with color
        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        
        # Add color if category is provided
        if category:
            color = get_label_color(category)
            label_object['color'] = color
            print(f"  🎨 Creating label '{label_name}' with color: bg={color['backgroundColor']}, text={color['textColor']}")
        
        try:
            created_label = service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            # Verify color was set
            created_color = created_label.get('color', {})
            if created_color:
                print(f"  ✅ Created label: {label_name} (ID: {created_label['id']}) with color bg={created_color.get('backgroundColor', 'none')}")
            else:
                print(f"  ⚠️  Created label: {label_name} (ID: {created_label['id']}) but color was not set")
            
            return created_label['id']
        except Exception as create_error:
            # If color causes error, try without color
            if category and 'color' in str(create_error).lower():
                print(f"  ⚠️  Color not accepted, creating label without color: {create_error}")
                label_object.pop('color', None)
                created_label = service.users().labels().create(
                    userId='me',
                    body=label_object
                ).execute()
                print(f"  ✅ Created label: {label_name} (ID: {created_label['id']}) without color")
                return created_label['id']
            else:
                raise
        
    except Exception as e:
        print(f"  ⚠️  Error creating label '{label_name}': {e}")
        return None


def ensure_labels_exist(service, categories: List[str]) -> Dict[str, str]:
    """
    Ensure all required labels exist in Gmail
    Returns dict mapping category -> label_id
    """
    label_map = {}
    
    print(f"\n{'='*60}")
    print(f"Ensuring Gmail labels exist...")
    print(f"{'='*60}")
    
    unique_categories = set(categories)
    for category in unique_categories:
        label_name = get_label_name(category)
        label_id = create_label_if_not_exists(service, label_name, category)
        if label_id:
            label_map[category] = label_id
        else:
            print(f"  ⚠️  Could not create/find label for category: {category}")
    
    print(f"✅ Label setup complete: {len(label_map)} labels ready\n")
    return label_map


def apply_labels_batch(
    user: User,
    emails: List[Dict],
    classifications: List[Dict],
    db
) -> Dict[str, any]:
    """
    Apply labels to emails using Gmail batchModify API for speed
    Groups emails by label and applies in batches
    
    Returns:
        {
            'success_count': int,
            'failed_count': int,
            'results': List[Dict]  # Per-email results
        }
    """
    print(f"\n{'='*80}")
    print(f"STEP 5: Applying labels to emails")
    print(f"{'='*80}\n")
    
    service = get_gmail_service(user, db)
    if not service:
        raise Exception("Failed to get Gmail service for labeling")
    
    # Group emails by category/label
    emails_by_label: Dict[str, List[str]] = {}  # label_name -> [email_ids]
    email_to_classification = {}  # email_id -> classification
    
    # Build mapping
    for classification in classifications:
        email_id = classification.get('email_id')
        category = classification.get('category', 'UNKNOWN')
        
        if not email_id:
            continue
        
        label_name = get_label_name(category)
        
        if label_name not in emails_by_label:
            emails_by_label[label_name] = []
        
        emails_by_label[label_name].append(email_id)
        email_to_classification[email_id] = classification
    
    # Ensure all labels exist
    all_categories = list(emails_by_label.keys())
    label_map = ensure_labels_exist(service, all_categories)
    
    # Apply labels using batchModify (up to 1000 emails per batch)
    results = []
    success_count = 0
    failed_count = 0
    
    batch_size = 1000  # Gmail API limit per batchModify call
    
    for label_name, email_ids in emails_by_label.items():
        label_id = label_map.get(label_name)
        
        if not label_id:
            print(f"  ❌ No label ID for '{label_name}', skipping {len(email_ids)} emails")
            failed_count += len(email_ids)
            for email_id in email_ids:
                results.append({
                    'email_id': email_id,
                    'label': label_name,
                    'success': False,
                    'error': f'Label ID not found for {label_name}'
                })
            continue
        
        # Process in batches of 1000 (Gmail API limit)
        for i in range(0, len(email_ids), batch_size):
            batch_ids = email_ids[i:i + batch_size]
            
            try:
                # Use batchModify to apply label to multiple emails at once
                service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': batch_ids,
                        'addLabelIds': [label_id]
                    }
                ).execute()
                
                # Record success for all emails in this batch
                for email_id in batch_ids:
                    success_count += 1
                    results.append({
                        'email_id': email_id,
                        'label': label_name,
                        'success': True,
                        'error': None
                    })
                
                print(f"  ✅ Applied label '{label_name}' to {len(batch_ids)} emails")
                
            except Exception as e:
                print(f"  ❌ Error applying label '{label_name}' to batch: {e}")
                failed_count += len(batch_ids)
                
                # Record failure for all emails in this batch
                for email_id in batch_ids:
                    results.append({
                        'email_id': email_id,
                        'label': label_name,
                        'success': False,
                        'error': str(e)
                    })
    
    print(f"\n{'='*80}")
    print(f"LABEL APPLICATION SUMMARY:")
    print(f"{'='*80}")
    print(f"  ✅ Successfully labeled: {success_count} emails")
    print(f"  ❌ Failed to label: {failed_count} emails")
    print(f"{'='*80}\n")
    
    return {
        'success_count': success_count,
        'failed_count': failed_count,
        'results': results,
        'total': len(results)
    }

