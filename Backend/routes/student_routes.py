import json
import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
import requests as http_requests
from werkzeug.utils import secure_filename
from models import Drive, Application, Student, Company, User, Notification
from database import db
from auth_middleware import token_required, admin_required
from extensions import cache,limiter
import re 


student_bp = Blueprint('student', __name__)


DEPARTMENT_KEYWORDS = {
    'cse': ['cse', 'cs', 'computer science', 'software', 'developer', 'programmer', 'backend', 'frontend', 'full stack', 'data', 'ai', 'ml'],
    'cs': ['cse', 'cs', 'computer science', 'software', 'developer', 'programmer', 'backend', 'frontend', 'full stack', 'data', 'ai', 'ml'],
    'it': ['it', 'information technology', 'software', 'developer', 'programmer', 'backend', 'frontend', 'full stack', 'data'],
    'ece': ['ece', 'electronics', 'communication', 'embedded', 'vlsi', 'iot', 'hardware', 'network'],
    'eee': ['eee', 'electrical', 'electronics', 'power', 'embedded', 'hardware'],
    'me': ['me', 'mechanical', 'manufacturing', 'production', 'design', 'cad', 'automobile'],
    'ce': ['ce', 'civil', 'construction', 'structural', 'site', 'autocad'],
}


def _lower_text(*values):
    return ' '.join(str(v or '') for v in values).lower()


def _student_department_keywords(department):
    dept = (department or '').lower()
    keywords = set()
    for key, values in DEPARTMENT_KEYWORDS.items():
        if key in dept or any(value in dept for value in values[:3]):
            keywords.update(values)
    if dept:
        keywords.add(dept)
    return keywords


def _mentioned_departments(text):
    mentioned = set()
    for key, values in DEPARTMENT_KEYWORDS.items():
        if key in text or any(value in text for value in values):
            mentioned.add(key)
    return mentioned


def _required_cgpa(text):
    cgpa_match = re.search(
        r'(?:min(?:imum)?\s+)?cgpa\s*(?:[>:=]+\s*|of\s+)?(\d+\.?\d*)'
        r'|(\d+\.?\d*)\s*cgpa',
        text
    )
    if not cgpa_match:
        return None
    return float(cgpa_match.group(1) or cgpa_match.group(2))


def _required_year(text):
    year_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*year', text)
    return int(year_match.group(1)) if year_match else None


def _local_suggestions(student, drives_list):
    student_keywords = _student_department_keywords(student.department)
    student_location = (student.location or '').lower()
    student_cgpa = student.cgpa or 0
    student_year = student.year or 0
    ranked = []

    for drive in drives_list:
        searchable = _lower_text(
            drive.get('job_title'),
            drive.get('company'),
            drive.get('description'),
            drive.get('eligibility'),
            drive.get('location'),
        )
        eligibility = (drive.get('eligibility') or '').lower()
        score = 45
        reasons = []

        keyword_hits = [kw for kw in student_keywords if kw and kw in searchable]
        if keyword_hits:
            score += min(25, 8 + len(keyword_hits) * 4)
            reasons.append('it matches your department/background')

        mentioned_depts = _mentioned_departments(eligibility)
        if mentioned_depts and not keyword_hits:
            score -= 18

        if student_location and student_location in (drive.get('location') or '').lower():
            score += 10
            reasons.append('the location matches your profile')

        cgpa_needed = _required_cgpa(eligibility)
        if cgpa_needed is not None:
            if student_cgpa >= cgpa_needed:
                score += 12
                reasons.append(f'your CGPA meets the {cgpa_needed:g}+ requirement')
            else:
                score -= 25
                reasons.append(f'the drive asks for {cgpa_needed:g}+ CGPA')

        year_needed = _required_year(eligibility)
        if year_needed is not None:
            if student_year == year_needed:
                score += 10
                reasons.append(f'it is open for {year_needed} year students')
            else:
                score -= 15

        if student.resume_filename:
            score += 4

        if not reasons:
            reasons.append('it is an open approved drive you have not applied to yet')

        score = max(1, min(100, score))
        ranked.append({
            'drive_id': drive['id'],
            'job_title': drive.get('job_title') or 'Untitled role',
            'company': drive.get('company') or 'Unknown',
            'match_score': score,
            'reason': 'Recommended because ' + ', '.join(reasons[:3]) + '.',
            'salary': drive.get('salary', ''),
            'location': drive.get('location', ''),
            'eligibility': drive.get('eligibility', ''),
            'deadline': drive.get('deadline', ''),
        })

    return sorted(ranked, key=lambda item: item['match_score'], reverse=True)[:3]

# Get all Drives
@student_bp.route('/drives', methods=['GET'])
@token_required
def get_drives(current_user):
    search = request.args.get('search', '').strip().lower()
    location = request.args.get('location', '').strip().lower()

    if not search and not location:
        cached = cache.get('all_open_drives')
        if cached is not None:
            return jsonify(cached), 200

    drives = Drive.query.filter_by(is_closed=False, admin_status='Approved').all()
    result = []
    for d in drives:
        company = Company.query.get(d.company_id)
        user = User.query.get(company.user_id) if company else None
        if user and user.is_blacklisted:
            continue
        if search:
            haystack = ' '.join([
                d.job_title or '',
                d.description or '',
                d.eligibility or '',
                user.username if user else ''
            ]).lower()
            if search not in haystack:
                continue
        if location and location not in (d.location or '').lower():
            continue
        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'description': d.description,
            'salary': d.salary,
            'location': d.location,
            'eligibility': d.eligibility,
            'deadline': d.deadline,
            'company_name': user.username if user else 'Unknown',
        })

    if not search and not location:
        cache.set('all_open_drives', result, timeout=120)

    return jsonify(result), 200

# Apply to a drive 
@student_bp.route('/apply', methods=['POST'])    
@token_required
def apply(current_user):
    data = request.json
    student = Student.query.filter_by(user_id=data['student_id']).first()  
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    
    # Duplicate check
    existing = Application.query.filter_by(
        student_id=student.id, 
        drive_id=data['drive_id']
    ).first()
    if existing:
        return jsonify({'message': 'Already applied'}), 400

    # Eligibility check
    drive = Drive.query.get(data['drive_id'])
    if not drive:
        return jsonify({'message': 'Drive not found'}), 404

    if drive.eligibility:
        eligibility_text = drive.eligibility.lower()

        # Check department/branch
        if student.department:
            dept = student.department.lower()
            known_depts = ['cse', 'ece', 'me', 'ce', 'it', 'eee', 'cs']
            mentioned = [d for d in known_depts if d in eligibility_text]
            if mentioned and not any(d in dept for d in mentioned):
                return jsonify({'message': f'Not eligible: your branch ({student.department}) does not meet the criteria'}), 403

        # Check CGPA
        import re
        cgpa_match = re.search(
            r'(?:min(?:imum)?\s+)?cgpa\s*(?:[>:=]+\s*|of\s+)?(\d+\.?\d*)'
            r'|(\d+\.?\d*)\s*cgpa',
            eligibility_text
        )
        if cgpa_match:
            required_cgpa = float(cgpa_match.group(1) or cgpa_match.group(2))
            if student.cgpa is None:
                return jsonify({
                    'message': f'Not eligible: minimum CGPA required is {required_cgpa}. '
                            f'Please update your CGPA in your profile first.'
                }), 403
            if student.cgpa < required_cgpa:
                return jsonify({
                    'message': f'Not eligible: minimum CGPA required is {required_cgpa}, yours is {student.cgpa}'
                }), 403

        # Check year
        year_match = re.search(r'(\d+)(st|nd|rd|th)\s*year', eligibility_text)
        if year_match:
            required_year = int(year_match.group(1))
            if (student.year or 0) != required_year:
                return jsonify({'message': f'Not eligible: this drive is for {required_year} year students only'}), 403

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Application submitted'}), 201


@student_bp.route('/<int:user_id>/applications', methods=['GET'])
def get_applications(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify([]), 200
    apps = Application.query.filter_by(student_id=student.id).all()
    result = []
    for a in apps:
        drive = Drive.query.get(a.drive_id)
        company = Company.query.get(drive.company_id) if drive else None
        user = User.query.get(company.user_id) if company else None
        result.append({
            'drive_id': a.drive_id,
            'job_title': drive.job_title if drive else 'N/A',
            'company_name': user.username if user else 'N/A',
            'status': a.status,
            'interview_type': a.interview_type or 'N/A',
            'result': a.result or 'N/A',
            'remark': a.remark or 'N/A',
            'interview_date': str(a.interview_date) if a.interview_date else None,
            'interview_link': a.interview_link or '',
            'interview_notes': a.interview_notes or '',
        })
    return jsonify(result), 200


# Ai suggestion
@student_bp.route('/suggestions/<int:user_id>', methods=['GET'])
@limiter.limit("5 per minute;20 per hour")
def get_suggestions(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404

    # Build student profile context
    profile = {
        'name':       student.name or '',
        'department': student.department or '',
        'email':      student.email or '',
        'location':   student.location or '',
        'has_resume': bool(student.resume_filename),
    }

    # Get all open drives (excluding already applied)
    applied_ids = [a.drive_id for a in Application.query.filter_by(student_id=student.id).all()]
    drives = Drive.query.filter_by(is_closed=False, admin_status='Approved').all()
    drives = [d for d in drives if d.id not in applied_ids]

    if not drives:
        return jsonify([]), 200

    drives_list = []
    for d in drives:
        company = Company.query.get(d.company_id)
        c_user  = User.query.get(company.user_id) if company else None
        drives_list.append({
            'id':          d.id,
            'job_title':   d.job_title,
            'company':     c_user.username if c_user else 'Unknown',
            'description': d.description[:300],
            'eligibility': d.eligibility or '',
            'location':    d.location or '',
            'salary':      d.salary or '',
            'deadline':    d.deadline or '',
        })

    prompt = f"""You are a placement assistant. Given a student's profile and a list of job drives, 
rank the TOP 3 most suitable drives for the student and explain why each is a good match.

Student Profile:
- Name: {profile['name']}
- Department: {profile['department']}
- Location: {profile['location']}
- Has Resume: {profile['has_resume']}

Available Drives:
{json.dumps(drives_list, indent=2)}

Respond ONLY with a valid JSON array (no markdown, no extra text) of exactly up to 3 objects:
[
  {{
    "drive_id": <integer>,
    "job_title": "<string>",
    "company": "<string>",
    "match_score": <integer 1-100>,
    "reason": "<1-2 sentence explanation of why this matches the student>"
  }}
]"""

    try:
        # api_key = current_app.config.get('ANTHROPIC_API_KEY', '')
        api_key = current_app.config.get('OPENAI_API_KEY', '')
        if not api_key:
            return jsonify(_local_suggestions(student, drives_list)), 200
        response = http_requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.2,
                'max_tokens': 800,
            },
            timeout=30
        )
        result = response.json()

        if response.status_code != 200:
            return jsonify(_local_suggestions(student, drives_list)), 200

        choices = result.get('choices')
        if not choices:
            return jsonify(_local_suggestions(student, drives_list)), 200

        text = choices[0].get('message', {}).get('content', '').strip()
        if not text:
            return jsonify(_local_suggestions(student, drives_list)), 200

        try:
            suggestions = json.loads(text)
        except json.JSONDecodeError:
            import re
            match = re.search(r'(\[.*\])', text, re.S)
            if not match:
                return jsonify(_local_suggestions(student, drives_list)), 200
            suggestions = json.loads(match.group(1))

        # Attach full drive details back
        drive_map = {d['id']: d for d in drives_list}
        for s in suggestions:
            d = drive_map.get(s['drive_id'], {})
            s['salary']      = d.get('salary', '')
            s['location']    = d.get('location', '')
            s['eligibility'] = d.get('eligibility', '')
            s['deadline']    = d.get('deadline', '')

        return jsonify(suggestions), 200

    except Exception:
        return jsonify(_local_suggestions(student, drives_list)), 200
    

@student_bp.route('/profile/<int:user_id>', methods=['GET'])     # view student profile
def get_profile(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    user = User.query.get(student.user_id)
    return jsonify({
        'name': student.name or '',
        'department': student.department or '',
        'resume_uploaded': bool(student.resume_filename),
        'resume_filename': student.resume_filename or '',
        'email': student.email or '',        
        'phone': student.phone or '',        
        'location': student.location or '', 
        'cgpa': student.cgpa,       
        'year': student.year, 
    }), 200

# Update profile
@student_bp.route('/profile/<int:user_id>', methods=['PUT'])     # update student profile
def update_profile(user_id):
    data = request.json
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    student.department = data.get('department', student.department)
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)        
    student.phone = data.get('phone', student.phone)       
    student.location = data.get('location', student.location)
    student.cgpa = data.get('cgpa', student.cgpa)
    student.year = data.get('year', student.year) 
    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200



# Upload Resume
@student_bp.route('/resume/upload/<int:user_id>', methods=['POST'])
def upload_resume(user_id):
    if 'resume' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'message': 'Only PDF files allowed'}), 400
    
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    
    filename = secure_filename(f"resume_{user_id}.pdf")
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    
    student.resume_filename = filename
    db.session.commit()
    return jsonify({'message': 'Resume uploaded successfully'}), 200

# View Resume
@student_bp.route('/resume/view/<int:user_id>', methods=['GET'])
def view_resume(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student or not student.resume_filename:
        return jsonify({'message': 'Resume not found'}), 404
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'], 
        student.resume_filename, 
    )

# Download Resume
@student_bp.route('/resume/download/<int:user_id>', methods=['GET'])
def download_resume(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student or not student.resume_filename:
        return jsonify({'message': 'Resume not found'}), 404
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        student.resume_filename,
        as_attachment=True,
        download_name=f"{student.name or 'student'}_resume.pdf"
    )

# Withdraw My application
@student_bp.route('/withdraw', methods=['DELETE'])
@token_required
def withdraw(current_user):
    data = request.json
    student = Student.query.filter_by(user_id=data['student_id']).first()
    if not student:
        return jsonify({'message':'Student not found'}),404
    application = Application.query.filter_by(
        student_id=student.id,
        drive_id=data['drive_id']
    ).first()
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    if application.status != 'Applied':
        return jsonify({'message': 'Cannot withdraw — application is already being processed'}), 400
    db.session.delete(application)
    db.session.commit()
    return jsonify({'message': 'Application Withdrawn'}),200

# Notification 
@student_bp.route('/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify([]), 200
    notifs = Notification.query.filter_by(student_id=student.id)\
                .order_by(Notification.created_at.desc()).limit(20).all()
    return jsonify([{
        'id':         n.id,
        'message':    n.message,
        'is_read':    n.is_read,
        'created_at': n.created_at.strftime('%d %b, %I:%M %p')
    } for n in notifs]), 200


@student_bp.route('/notifications/read', methods=['POST'])
def mark_notifications_read():
    data = request.json
    student = Student.query.filter_by(user_id=data['user_id']).first()
    if student:
        Notification.query.filter_by(student_id=student.id, is_read=False)\
            .update({'is_read': True})
        db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200
