from flask import Blueprint, request, jsonify
from models import Drive, Application, Company, Student, User, Notification
from database import db
from auth_middleware import token_required
from extensions import cache


company_bp = Blueprint('company', __name__)


#Create drive
@company_bp.route('/drives', methods=['POST'])
@token_required
def create(current_user):
    data = request.json
    comp = Company.query.filter_by(user_id=data['company_id']).first()
    if not comp:
        return jsonify({'message': 'Company not found'}), 404
    if not comp.approved:
        return jsonify({'message': 'Company not approved'}), 403
    
    drive = Drive(
        company_id=comp.id,
        drive_name=data.get('drive_name', ''),
        job_title=data['job_title'],
        description=data['description'],
        salary=data.get('salary',''),
        location=data.get('location',''),
        eligibility=data.get('eligibility',''),
        deadline=data.get('deadline',''),
    )

    db.session.add(drive)
    db.session.commit()
    cache.delete('all_open_drives')
    return jsonify({'message': 'Drive created successfully'}), 201



# Get drives by company
@company_bp.route('/<int:company_id>/drives', methods=['GET'])
@token_required
def get_drives(current_user, company_id):
    from datetime import datetime
    today = datetime.now().date()
    comp = Company.query.filter_by(user_id=current_user.id).first()
    if not comp:
        return jsonify([]), 200
    drives = Drive.query.filter_by(company_id=comp.id).all()
    result = []
    for d in drives:
        # Auto-close drive if deadline has passed
        if d.deadline:
            try:
                deadline = datetime.strptime(d.deadline, '%Y-%m-%d').date()
                if deadline < today and not d.is_closed:
                    d.is_closed = True
                    db.session.commit()
                    cache.delete('all_open_drives')
            except ValueError:
                pass
        result.append({
            'id': d.id,
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'description': d.description,
            'salary': d.salary,
            'location': d.location,
            'eligibility': d.eligibility,
            'deadline': d.deadline,
            'is_closed': d.is_closed,
            'admin_status': d.admin_status
        })
    return jsonify(result), 200


# Get applications for a drive
@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@token_required
def get_drive_applications(current_user, drive_id):
    status = request.args.get('status', '').strip()
    department = request.args.get('department', '').strip().lower()
    search = request.args.get('search', '').strip().lower()

    apps = Application.query.filter_by(drive_id=drive_id).all()
    result = []
    for a in apps:
        student = Student.query.get(a.student_id)
        user = User.query.get(student.user_id) if student else None
        if status and a.status != status:
            continue
        if department and (student.department or '').lower() != department:
            continue
        if search and search not in (user.username if user else '').lower():
            continue
        result.append({
            'id': a.id,
            'student_name': user.username if user else 'N/A',
            'student_user_id': student.user_id if student else None,
            'department': student.department if student else 'N/A',
            'status': a.status,
            'interview_type': a.interview_type,
            'interview_date': a.interview_date or '',
            'interview_link': a.interview_link or '',
            'interview_notes': a.interview_notes or '',
            'result': a.result,
            'remark': a.remark,
            'resume_uploaded': bool(student.resume_filename) if student else False,
        })
    return jsonify(result), 200


# Update application status
@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@token_required
def update_status(current_user, app_id):
    data = request.json
    app = db.session.get(Application, app_id)
    if not app:
        return jsonify({'message': 'Application not found'}), 404

    app.status = data.get('status', app.status)
    app.interview_type = data.get('interview_type', app.interview_type)
    app.result = data.get('result', app.result)
    app.remark = data.get('remark', data.get('remarks', app.remark))
    db.session.commit()

    new_status = data.get('status')  # only act if status explicitly changed
    if new_status in ('Shortlisted', 'Waitlisted', 'Rejected', 'Selected'):
        student = Student.query.get(app.student_id)
        drive   = Drive.query.get(app.drive_id)
        company = Company.query.get(drive.company_id) if drive else None
        c_user  = User.query.get(company.user_id) if company else None

        # Send email (non-blocking)
        try:
            from tasks import send_status_email
            send_status_email.delay(
                student_email=student.email if student else '',
                student_name=student.name if student else '',
                job_title=drive.job_title if drive else '',
                company_name=c_user.username if c_user else '',
                new_status=new_status
            )
        except Exception as e:
            print(f"[Warning] Email task failed: {e}")

        if new_status == 'Selected':
            msg = (
                f"🎉 Congratulations! You have been selected for "
                f"{drive.job_title if drive else 'a position'} at "
                f"{c_user.username if c_user else 'a company'}!"
            )
        else:
            msg = (
                f"You have been {new_status.lower()} for "
                f"{drive.job_title if drive else 'a position'} at "
                f"{c_user.username if c_user else 'a company'}."
            )
        notif = Notification(student_id=app.student_id, message=msg)
        db.session.add(notif)
        db.session.commit()

    return jsonify({'message': 'Status updated successfully'}), 200


# Schedule Interview
@company_bp.route('/applications/<int:app_id>/schedule-interview', methods=['PUT'])
@token_required
def schedule_interview(current_user, app_id):
    data = request.json
    app = db.session.get(Application, app_id)
    if not app:
        return jsonify({'message': 'Application not found'}), 404

    app.interview_type  = data.get('interview_type', app.interview_type)
    app.interview_date  = data.get('interview_date', app.interview_date)
    app.interview_link  = data.get('interview_link', app.interview_link)
    app.interview_notes = data.get('interview_notes', app.interview_notes)
    app.status          = 'Shortlisted'
    db.session.commit()

    drive   = Drive.query.get(app.drive_id)
    company = Company.query.get(drive.company_id) if drive else None
    c_user  = User.query.get(company.user_id) if company else None
    date_str = data.get('interview_date', '')
    msg = (
        f"📅 Your interview for {drive.job_title if drive else 'a position'} at "
        f"{c_user.username if c_user else 'a company'} is scheduled"
        f"{' on ' + date_str if date_str else ''}. "
        f"Type: {app.interview_type or 'TBD'}."
    )
    db.session.add(Notification(student_id=app.student_id, message=msg))
    db.session.commit()

    # Send interview scheduled email
    student = Student.query.get(app.student_id)
    if student and student.email:
        try:
            from tasks import send_interview_email
            send_interview_email.delay(
                student_email=student.email,
                student_name=student.name or '',
                job_title=drive.job_title if drive else '',
                company_name=c_user.username if c_user else '',
                interview_date=app.interview_date or '',
                interview_type=app.interview_type or '',
                interview_link=app.interview_link or '',
                interview_notes=app.interview_notes or '',
            )
        except Exception as e:
            print(f'[Warning] Interview email task failed: {e}')

    return jsonify({'message': 'Interview scheduled successfully'}), 200


# Final Result
@company_bp.route('/applications/<int:app_id>/final-result', methods=['PUT'])
@token_required
def update_final_result(current_user, app_id):
    data = request.json
    app = db.session.get(Application, app_id)
    if not app:
        return jsonify({'message': 'Application not found'}), 404

    result = data.get('result')
    app.result = result
    app.remark = data.get('remark', app.remark)
    if result == 'Passed':
        app.status = 'Selected'
    elif result == 'Failed':
        app.status = 'Rejected'
    db.session.commit()

    drive   = Drive.query.get(app.drive_id)
    company = Company.query.get(drive.company_id) if drive else None
    c_user  = User.query.get(company.user_id) if company else None

    if result in ('Passed', 'Failed'):
        student = Student.query.get(app.student_id)
        if student and student.email:
            try:
                from tasks import send_final_result_email
                send_final_result_email.delay(
                    student_email=student.email,
                    student_name=student.name or '',
                    job_title=drive.job_title if drive else '',
                    company_name=c_user.username if c_user else '',
                    result=result,
                )
            except Exception as e:
                print(f'[Warning] Final result email task failed: {e}')
   

    if result == 'Passed':
        msg = f"🎉 Congratulations! You have been selected for {drive.job_title if drive else 'a position'} at {c_user.username if c_user else 'a company'}!"
    elif result == 'Pending':
        msg = f" Your Interview Status is under Examination for {drive.job_title if drive else 'a position'} at {c_user.username if c_user else 'a company'}."
    else:
        msg = f"❌ Unfortunately you were not selected for {drive.job_title if drive else 'a position'} at {c_user.username if c_user else 'a company'}."
    db.session.add(Notification(student_id=app.student_id, message=msg))
    db.session.commit()
    return jsonify({'message': 'Final result updated'}), 200


# Close a drive
@company_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@token_required
def close_drive(current_user, drive_id):
    drive = db.session.get(Drive, drive_id)
    if not drive:
        return jsonify({'message': 'Drive not found'}), 404
    drive.is_closed = True
    db.session.commit()
    cache.delete('all_open_drives')
    return jsonify({'message': 'Drive closed successfully'}), 200


#Edit a Drive
@company_bp.route('/drives/<int:drive_id>',methods=['PUT'])
@token_required
def edit_drive(current_user, drive_id):
    drive = db.session.get(Drive,drive_id)
    if not drive:
        return jsonify({'message': 'Drive Not found'}),404
    if drive.is_closed:
        return jsonify({'message': 'Cannot edit a closed drive'}),400
    data = request.json
    drive.drive_name = data.get('drive_name', drive.drive_name)
    drive.job_title = data.get('job_title', drive.job_title)
    drive.description = data.get('description', drive.description)
    drive.salary = data.get('salary', drive.salary)
    drive.location = data.get('location', drive.location)
    drive.eligibility = data.get('eligibility', drive.eligibility)
    drive.deadline = data.get('deadline', drive.deadline)
    db.session.commit()
    cache.delete('all_open_drives')
    return jsonify({'message': 'Drive updated successfully'}),200


# Get company profile
@company_bp.route('/profile/<int:user_id>', methods=['GET'])
@token_required
def get_profile(current_user, user_id):
    comp = Company.query.filter_by(user_id=user_id).first()
    if not comp:
        return jsonify({'message': 'Company not found'}), 404
    user=User.query.get(user_id)
    return jsonify({
        'username': user.username,
        'overview': comp.overview or '',
        'approved': comp.approved,
        'company_name': comp.company_name or '',
        'hr_contact': comp.hr_contact or '',
        'website': comp.website or '',
    }), 200


# Update company overview
@company_bp.route('/profile/<int:user_id>', methods=['PUT'])
@token_required
def update_profile(current_user, user_id):
    data = request.json
    comp = Company.query.filter_by(user_id=user_id).first()
    if not comp:
        return jsonify({'message': 'Company not found'}), 404
    comp.overview = data.get('overview', comp.overview)
    comp.company_name = data.get('company_name', comp.company_name)
    comp.hr_contact = data.get('hr_contact', comp.hr_contact)
    comp.website = data.get('website', comp.website)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

# Get Report
@company_bp.route('/report/<int:user_id>', methods=['GET'])
@token_required
def get_report(current_user, user_id):
    comp = Company.query.filter_by(user_id=user_id).first()
    if not comp:
        return jsonify({'message': 'Company not found'}), 404

    drives = Drive.query.filter_by(company_id=comp.id).all()
    drives_data = []
    total_apps = total_shortlisted = total_selected = total_rejected = 0

    for d in drives:
        apps = Application.query.filter_by(drive_id=d.id).all()
        shortlisted = sum(1 for a in apps if a.status == 'Shortlisted')
        rejected = sum(1 for a in apps if a.status == 'Rejected')
        waitlisted = sum(1 for a in apps if a.status == 'Waitlisted')
        selected = sum(1 for a in apps if a.status == 'Selected')

        dept_breakdown = {}
        for a in apps:
            student = Student.query.get(a.student_id)
            if student and student.department:
                dept_breakdown[student.department] = dept_breakdown.get(student.department, 0) + 1

        total_apps += len(apps)
        total_shortlisted += shortlisted
        total_selected += selected
        total_rejected += rejected

        drives_data.append({
            'drive_id': d.id,
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'location': d.location,
            'deadline': d.deadline,
            'is_closed': d.is_closed,
            'total': len(apps),
            'applied': sum(1 for a in apps if a.status == 'Applied'),
            'shortlisted': shortlisted,
            'selected': selected,
            'rejected': rejected,
            'waitlisted': waitlisted,
            'departments': list(dept_breakdown.keys()),
        })

    return jsonify({
        'total_drives': len(drives),
        'open_drives': sum(1 for d in drives if not d.is_closed),
        'closed_drives': sum(1 for d in drives if d.is_closed),
        'total_applications': total_apps,
        'total_shortlisted': total_shortlisted,
        'total_selected': total_selected,
        'total_rejected': total_rejected,
        'total_waitlisted': total_apps - total_shortlisted - total_selected - total_rejected,
        'drives': drives_data,
    }), 200
