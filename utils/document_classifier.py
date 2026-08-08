import re

# Comprehensive Keyword Taxonomy
TAXONOMY_MAP = {
    'Personal Documents': {
        'Birth Certificate': ['birth certificate', 'birth registration', 'date of birth', 'born on', 'municipal corporation', 'registrar of births'],
        'Aadhaar': ['aadhaar', 'aadhar', 'uidai', 'unique identification', 'help@uidai.gov.in'],
        'PAN Card': ['pan card', 'pan number', 'permanent account number', 'income tax department'],
        'Passport': ['passport', 'republic of india passport', 'place of birth', 'nationality'],
        'Voter ID': ['voter id', 'epic number', 'electoral photo', 'election commission'],
        'Ration Card': ['ration card', 'family card', 'food supply card']
    },
    'Financial Documents': {
        'Bank Passbook': ['bank passbook', 'bank statement', 'account number', 'ifsc', 'savings account', 'passbook'],
        'Cheque': ['cheque', 'pay to', 'a/c payee', 'bearer rupees'],
        'Insurance': ['life insurance', 'health insurance', 'policy number', 'sum assured', 'premium', 'policyholder'],
        'Tax Documents': ['income tax', 'form 16', 'itr', 'gst', 'tax return', 'assessment year']
    },
    'Transportation': {
        'Driving License': ['driving license', 'driver license', 'dl number', 'dl no', 'driving licence', 'transport department'],
        'Vehicle RC': ['vehicle registration', 'registration certificate', 'rc book', 'chassis number', 'engine number', 'rto'],
        'Pollution Certificate': ['pollution certificate', 'puc', 'pollution under control', 'pucc', 'emission level'],
        'Motor Insurance': ['motor insurance', 'vehicle insurance', 'third party insurance', 'insured declared value']
    },
    'Education': {
        '10th Marksheet': ['10th marksheet', '10th mark sheet', 'sslc', 'class 10', 'board of secondary education'],
        '11th Marksheet': ['11th marksheet', '11th mark sheet', 'class 11', '11th class', 'higher secondary first year'],
        '12th Marksheet': ['12th marksheet', '12th mark sheet', 'hsc', 'class 12', 'board of intermediate'],
        'Degree Certificate': ['degree certificate', 'provisional certificate', 'bachelor of', 'master of', 'convocation', 'awarded the degree of'],
        'Semester Marksheet': ['semester marksheet', 'marksheet', 'grade sheet', 'semester', 'sgpa', 'cgpa', 'transfer certificate', 'bonafide certificate', 'college id', 'university']
    },
    'Certificates': {
        'Course Completion Certificates': ['certificate of completion', 'completion certificate', 'course certificate', 'skill certificate', 'coursera', 'udemy', 'nptel', 'infosys springboard'],
        'Workshop Certificates': ['workshop certificate', 'certificate of participation', 'attended workshop', 'symposium'],
        'Training Certificates': ['training certificate', 'completed training', 'vocational training']
    },
    'Internship': {
        'Internship Certificates': ['internship certificate', 'internship completion', 'internship offer letter', 'experience certificate', 'relieving letter', 'internship duration', 'company name']
    },
    'Projects & Achievements': {
        'Project Reports': ['project report', 'capstone project', 'hackathon', 'research paper', 'innovation challenge', 'codeathon']
    },
    'Resume & Career': {
        'Resume': ['resume', 'curriculum vitae', 'cv', 'portfolio', 'professional summary', 'work experience']
    }
}

DOCUMENT_TAXONOMY = TAXONOMY_MAP

# High Priority Phrases (Always checked BEFORE generic words like "certificate")
PRIORITY_RULES = [
    {
        'phrase': 'birth certificate',
        'category': 'Personal Documents',
        'subcategory': 'Birth Certificate',
        'keywords': ['Birth Certificate', 'Date of Birth', 'Registrar']
    },
    {
        'phrase': 'birth registration',
        'category': 'Personal Documents',
        'subcategory': 'Birth Certificate',
        'keywords': ['Birth Registration', 'Municipal Corporation']
    },
    {
        'phrase': 'driving license',
        'category': 'Transportation',
        'subcategory': 'Driving License',
        'keywords': ['Driving License', 'DL Number', 'Transport Department']
    },
    {
        'phrase': 'driver license',
        'category': 'Transportation',
        'subcategory': 'Driving License',
        'keywords': ['Driver License', 'DL Number']
    },
    {
        'phrase': 'driving licence',
        'category': 'Transportation',
        'subcategory': 'Driving License',
        'keywords': ['Driving Licence', 'Transport Department']
    },
    {
        'phrase': 'internship certificate',
        'category': 'Internship',
        'subcategory': 'Internship Certificates',
        'keywords': ['Internship Certificate', 'Internship Completion']
    },
    {
        'phrase': 'internship offer',
        'category': 'Internship',
        'subcategory': 'Internship Certificates',
        'keywords': ['Internship Offer Letter', 'Joining Date']
    },
    {
        'phrase': 'experience certificate',
        'category': 'Internship',
        'subcategory': 'Internship Certificates',
        'keywords': ['Experience Certificate', 'Service Certificate']
    },
    {
        'phrase': 'degree certificate',
        'category': 'Education',
        'subcategory': 'Degree Certificate',
        'keywords': ['Degree Certificate', 'University', 'Bachelor/Master']
    },
    {
        'phrase': 'provisional certificate',
        'category': 'Education',
        'subcategory': 'Degree Certificate',
        'keywords': ['Provisional Certificate', 'University']
    },
    {
        'phrase': 'certificate of completion',
        'category': 'Certificates',
        'subcategory': 'Course Completion Certificates',
        'keywords': ['Certificate of Completion', 'Course Certificate']
    },
    {
        'phrase': 'completion certificate',
        'category': 'Certificates',
        'subcategory': 'Course Completion Certificates',
        'keywords': ['Completion Certificate', 'Skill Certificate']
    },
    {
        'phrase': 'course certificate',
        'category': 'Certificates',
        'subcategory': 'Course Completion Certificates',
        'keywords': ['Course Certificate', 'Credential']
    }
]

def classify_document_advanced(filename: str, extracted_text: str = ""):
    """
    Intelligent Rule-Based Classifier with Phrase-First Matching, Dynamic Confidence Score Calculation,
    and AI Explanation.

    Returns:
    (category, subcategory, ai_tags, confidence_score, matched_keywords, classification_reason)
    """
    content = f"{filename} {extracted_text}".lower()
    
    # 1. PRIORITY PHRASE CHECKING (Executed BEFORE generic matching)
    for rule in PRIORITY_RULES:
        phrase = rule['phrase']
        if phrase in content:
            # Dynamic confidence calculation for priority match
            extra_keywords = []
            base_score = 0.85
            
            # Check secondary supporting keywords
            if 'date of birth' in content or 'born' in content: extra_keywords.append('Date of Birth')
            if 'registrar' in content or 'municipal' in content: extra_keywords.append('Registrar')
            if 'dl number' in content or 'valid till' in content: extra_keywords.append('DL Number')
            if 'university' in content or 'bachelor' in content: extra_keywords.append('University')
            if phrase in filename.lower(): base_score += 0.08
            
            all_matched = list(set([phrase.title()] + rule['keywords'] + extra_keywords))
            confidence = min(0.99, round(base_score + (len(extra_keywords) * 0.04), 2))
            
            matched_str = ", ".join(all_matched)
            reason = f"Matched high-priority phrase '{phrase.title()}' with {len(all_matched)} supporting document keywords."
            tags = f"{rule['category']}, {rule['subcategory']}, {matched_str}"
            
            return rule['category'], rule['subcategory'], tags, confidence, matched_str, reason

    # 2. MULTI-KEYWORD CONFIDENCE SCORE EVALUATION
    best_category = "Others"
    best_subcategory = "Other Document"
    highest_raw_score = 0.0
    matched_keywords_list = []

    for cat, subcats in TAXONOMY_MAP.items():
        for subcat, phrases in subcats.items():
            cat_score = 0.0
            matches = []
            
            for phrase in phrases:
                if phrase in content:
                    # Weight exact phrases higher than single words
                    weight = 0.40 if ' ' in phrase else 0.15
                    if phrase in filename.lower():
                        weight += 0.25
                    cat_score += weight
                    matches.append(phrase.title())
                    
            if cat_score > highest_raw_score:
                highest_raw_score = cat_score
                best_category = cat
                best_subcategory = subcat
                matched_keywords_list = matches

    # Calculate dynamic confidence percentage
    if highest_raw_score == 0:
        confidence = 0.15
    elif len(matched_keywords_list) == 1 and highest_raw_score < 0.3:
        confidence = 0.45 # Single weak keyword match
    else:
        confidence = min(0.96, round(0.50 + (highest_raw_score * 0.35), 2))

    matched_keywords_str = ", ".join(list(set(matched_keywords_list))) if matched_keywords_list else "None"

    # 3. LOW CONFIDENCE HANDLING (< 60% / 0.60)
    if confidence < 0.60:
        reason = f"We couldn't confidently identify this document (confidence {int(confidence * 100)}% < 60%). Please choose category manually."
        return 'Others', 'Other Document', 'Others, Unclassified', confidence, matched_keywords_str, reason

    reason = f"Matched key phrases [{matched_keywords_str}] with dynamic confidence {int(confidence * 100)}%."
    tags = f"{best_category}, {best_subcategory}, {matched_keywords_str}"

    return best_category, best_subcategory, tags, confidence, matched_keywords_str, reason
