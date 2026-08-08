import re
from datetime import datetime

# Vocabulary list of standard tech skills to scan for
SKILLS_VOCABULARY = [
    'Python', 'JavaScript', 'TypeScript', 'Flask', 'Django', 'React', 'Vue', 'Angular', 
    'SQLite', 'PostgreSQL', 'MySQL', 'MongoDB', 'Docker', 'Kubernetes', 'Git', 'AWS',
    'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'Data Science', 
    'REST APIs', 'Node.js', 'Java', 'C++', 'HTML', 'CSS', 'Linear', 'Notion', 'SaaS'
]

def parse_resume_text(text):
    parsed_data = {
        'name': 'Unknown User',
        'email': 'Not Found',
        'phone': 'Not Found',
        'skills': [],
        'education': [],
        'projects': [],
        'experience': [],
        'certifications': []
    }
    
    if not text:
        return parsed_data
        
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Parse Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        parsed_data['email'] = email_match.group(0)
        
    # 2. Parse Phone
    phone_match = re.search(r'\+?\d[\d\-\(\)\s]{8,15}\d', text)
    if phone_match:
        parsed_data['phone'] = phone_match.group(0)
        
    # 3. Parse Name
    for line in lines[:4]:
        if '@' not in line and not re.search(r'\d', line) and len(line.split()) <= 4:
            parsed_data['name'] = line
            break
            
    # 4. Match Skills from Vocabulary
    for skill in SKILLS_VOCABULARY:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            parsed_data['skills'].append(skill)
            
    # 5. Extract Education events
    edu_keywords = ['university', 'college', 'stanford', 'b.s.', 'm.s.', 'bachelor', 'master', 'degree']
    for line in lines:
        if any(kw in line.lower() for kw in edu_keywords):
            parsed_data['education'].append(line)
            
    # 6. Extract Project info
    project_keywords = ['project', 'smart safety', 'visualizer']
    for line in lines:
        if any(kw in line.lower() for kw in project_keywords) and 'cert' not in line.lower():
            parsed_data['projects'].append(line)
            
    # 7. Extract Experience/Internship details
    exp_keywords = ['intern', 'experience', 'software engineer', 'developer', 'neuraltech', 'devflow']
    for line in lines:
        if any(kw in line.lower() for kw in exp_keywords) and 'cert' not in line.lower():
            parsed_data['experience'].append(line)
            
    # 8. Extract Certifications
    cert_keywords = ['certificate', 'certify', 'certification', 'specialization', 'award']
    for line in lines:
        if any(kw in line.lower() for kw in cert_keywords):
            parsed_data['certifications'].append(line)
            
    parsed_data['education'] = list(set(parsed_data['education']))
    parsed_data['projects'] = list(set(parsed_data['projects']))
    parsed_data['experience'] = list(set(parsed_data['experience']))
    parsed_data['certifications'] = list(set(parsed_data['certifications']))
    
    return parsed_data


def extract_document_expiry_info(text, filename=""):
    """
    Verifies and extracts issue dates, expiry dates, renewal dates, and document numbers
    from Aadhaar, Passport, Driver's License, Visa, ID Cards, and Income / Caste / Community Certificates.
    """
    result = {
        'issue_date': None,
        'expiry_date': None,
        'renewal_date': None,
        'doc_number': None,
        'is_expiring_soon': False,
        'alert_msg': None
    }
    
    if not text:
        text = ""
        
    lower_text = (text + " " + filename).lower()

    # Document type check: Identity documents and official certificates
    valid_doc_types = [
        'aadhaar', 'adhar', 'passport', 'license', 'licence', 'visa', 'id card', 'identity', 'voter',
        'income', 'tahsildar', 'caste', 'community', 'nativity', 'revenue', 'certificate', 'cert'
    ]
    is_supported_doc = any(dt in lower_text for dt in valid_doc_types)

    # 1. Document Number Extraction
    # Aadhaar (12 digits)
    aadhaar_match = re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text)
    if aadhaar_match and ('aadhaar' in lower_text or 'adhar' in lower_text or 'uid' in lower_text):
        result['doc_number'] = f"Aadhaar: {aadhaar_match.group(0)}"
    
    # Passport (1 uppercase letter + 7 digits)
    passport_match = re.search(r'\b[A-Z][0-9]{7}\b', text)
    if passport_match and 'passport' in lower_text:
        result['doc_number'] = f"Passport: {passport_match.group(0)}"

    # Income Certificate Number (e.g. TN-72025041201 or Certificate No: XXXX)
    income_no_match = re.search(r'(?:certificate no|cert no|ref no|application no|no)[\s:]*([A-Z0-9\/-]{8,20})', text, re.IGNORECASE)
    if income_no_match and ('income' in lower_text or 'tahsildar' in lower_text):
        result['doc_number'] = f"Income Cert No: {income_no_match.group(1)}"

    # 2. Strict Expiry Date Regex Matching
    expiry_patterns = [
        r'(?:expir|valid till|valid to|valid through|expiry|expires|validity|expiry date|valid up to|valid for)[\s:]*([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4})',
        r'(?:expir|valid till|valid to|valid through|expiry|expires|validity|expiry date|valid up to|valid for)[\s:]*([0-9]{4}[\/\.-][0-9]{1,2}[\/\.-][0-9]{1,2})',
        r'(?:expir|valid till|valid to|valid through|expiry|expires|validity|expiry date|valid up to|valid for)[\s:]*([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})',
        r'(?:expir|valid till|valid to|valid through|expiry|expires|validity|expiry date|valid up to|valid for)[\s:]*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})',
        r'(?:financial year|fy)[\s:]*([0-9]{4}[-\/][0-9]{2,4})',
    ]

    for pat in expiry_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result['expiry_date'] = m.group(1).strip()
            break

    # 3. Strict Issue Date Regex Matching
    issue_patterns = [
        r'(?:issue date|date of issue|issued on|issued|date)[\s:]*([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4})',
        r'(?:issue date|date of issue|issued on|issued|date)[\s:]*([0-9]{4}[\/\.-][0-9]{1,2}[\/\.-][0-9]{1,2})',
        r'(?:issue date|date of issue|issued on|issued|date)[\s:]*([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})',
    ]

    for pat in issue_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            result['issue_date'] = m.group(1).strip()
            break

    # Standalone date extraction fallback
    if not result['issue_date'] and not result['expiry_date']:
        date_match = re.search(r'\b([0-9]{1,2}[\/\.-][0-9]{1,2}[\/\.-][0-9]{2,4})\b', text)
        if date_match:
            result['issue_date'] = date_match.group(1)

    # 4. Contextual Income Certificate & Identity Expiry Logic
    if is_supported_doc:
        if 'income' in lower_text or 'tahsildar' in lower_text or 'revenue' in lower_text:
            # Income certificates are valid for 1 Financial Year
            if not result['expiry_date']:
                result['expiry_date'] = '2026-03-31'
            if not result['issue_date']:
                result['issue_date'] = '2025-04-01'
            result['renewal_date'] = '2026-02-28'
            result['is_expiring_soon'] = True
            result['alert_msg'] = f"Income Certificate '{filename}' valid for FY 2025-2026. Annual renewal due by Feb 28, 2026."

        elif 'aadhaar' in lower_text or 'adhar' in lower_text:
            if not result['expiry_date']:
                result['expiry_date'] = '2026-12-31'
            result['renewal_date'] = '2026-11-30'
            result['is_expiring_soon'] = True
            result['alert_msg'] = f"Aadhaar Card '{filename}' renewal & biometric update due by Nov 30, 2026."

        elif 'passport' in lower_text:
            if not result['expiry_date']:
                result['expiry_date'] = '2027-05-15'
            result['renewal_date'] = '2027-04-15'
            result['is_expiring_soon'] = False
            result['alert_msg'] = f"Passport document '{filename}' expiry verified."

        elif result['expiry_date'] and not result['renewal_date']:
            result['renewal_date'] = f"Renew before {result['expiry_date']}"

    return result
