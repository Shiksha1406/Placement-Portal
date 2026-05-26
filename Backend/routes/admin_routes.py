import csv
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import Blueprint, request, jsonify, make_response
from models import User, Company, Student, Drive, Application, Notification
from datetime import datetime
from database import db
from auth_middleware import admin_required
from extensions import cache, limiter

admin_bp = Blueprint('admin', __name__)


#Pending companies 
@admin_bp.route('/pending-companies', methods=['GET'])
@admin_required    #(ensures security)
def pending_companies(current_user):
    companies = Company.query.filter_by(approved=False).all()
    result = []
    for c in companies:
        user = User.query.get(c.user_id)
        if user and not user.is_blacklisted:
            result.append({'id': c.id, 'user_id': c.user_id, 'username': user.username})
    return jsonify(result), 200


#Approve Company
@admin_bp.route('/approve-company/<int:company_id>', methods=['POST'])
@admin_required
def approve_company(current_user, company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'message': 'Company not found'}), 404
    company.approved = True
    db.session.commit()
    return jsonify({'message': 'Company approved'}), 200



@admin_bp.route('/students', methods=['GET'])
@admin_required 
def get_students(current_user):
    search = request.args.get('search', '').strip().lower()
    department = request.args.get('department', '').strip()
    blacklisted = request.args.get('blacklisted')
    students = Student.query.all()
    result = []
    for s in students:
        user = User.query.get(s.user_id)
        if not user:
            continue
        if blacklisted == 'true' and not user.is_blacklisted:
            continue
        if blacklisted == 'false' and user.is_blacklisted:
            continue
        if department and (s.department or '').lower() != department.lower():
            continue
        if search and search not in user.username.lower() and search not in (s.name or '').lower():
            continue
        result.append({
            'id': s.id,
            'user_id': s.user_id,
            'username': user.username,
            'department': s.department,
            'is_blacklisted': user.is_blacklisted
        })
    return jsonify(result), 200



@admin_bp.route('/companies', methods=['GET'])
@admin_required
def get_companies(current_user):
    search = request.args.get('search', '').strip().lower()
    approved = request.args.get('approved')
    blacklisted = request.args.get('blacklisted')
    companies = Company.query.all()
    result = []
    for c in companies:
        user = User.query.get(c.user_id)
        if not user:
            continue
        if approved == 'true' and not c.approved:
            continue
        if approved == 'false' and c.approved:
            continue
        if blacklisted == 'true' and not user.is_blacklisted:
            continue
        if blacklisted == 'false' and user.is_blacklisted:
            continue
        if search and search not in user.username.lower():
            continue
        result.append({
            'id': c.id,
            'user_id': c.user_id,
            'username': user.username,
            'approved': c.approved,
            'is_blacklisted': user.is_blacklisted
        })
    return jsonify(result), 200

#Blacklist user
@admin_bp.route('/blacklist/<int:user_id>', methods=['POST'])
@admin_required
def blacklist_user(current_user,user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.is_blacklisted = True
    # If company is blacklisted, close all their drives
    if user.role == 'company':
        company = Company.query.filter_by(user_id=user_id).first()
        if company:
            Drive.query.filter_by(company_id=company.id).update({'is_closed': True})
            cache.delete('all_open_drives')
    db.session.commit()
    return jsonify({'message': 'User blacklisted'}), 200

#Unblacklist 
@admin_bp.route('/unblacklist/<int:user_id>', methods=['POST'])
@admin_required
def unblacklist_user(current_user,user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.is_blacklisted = False
    db.session.commit()
    return jsonify({'message': 'User unblacklisted'}), 200



@admin_bp.route('/applications', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_all_applications')
def get_all_applications(current_user):
    apps = Application.query.all()
    result = []
    for a in apps:
        student = Student.query.get(a.student_id)
        drive = Drive.query.get(a.drive_id)
        student_user = User.query.get(student.user_id) if student else None
        company = Company.query.get(drive.company_id) if drive else None
        company_user = User.query.get(company.user_id) if company else None
        result.append({
            'id': a.id,
            'student_name': student_user.username if student_user else 'N/A',
            'drive_name': drive.job_title if drive else 'N/A',
            'company_name': company_user.username if company_user else 'N/A',
            'status': a.status
        })
    return jsonify(result), 200


@admin_bp.route('/applications/<int:app_id>', methods=['PUT'])
@admin_required
def update_application(current_user, app_id):
    data = request.json
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404

    old_status = application.status

    if 'status' in data:
        application.status = data['status']
    if 'interview_type' in data:
        application.interview_type = data['interview_type']
    if 'result' in data:
        application.result = data['result']
    if 'remark' in data:
        application.remark = data['remark']

    # Create notification when status changes
    if 'status' in data and data['status'] != old_status:
        drive = Drive.query.get(application.drive_id)
        job_title = drive.job_title if drive else 'a drive'
        messages = {
            'Shortlisted': f"🎉 You have been shortlisted for {job_title}!",
            'Rejected':    f"❌ Your application for {job_title} was not selected.",
            'Waitlisted':  f"⏳ You have been waitlisted for {job_title}.",
        }
        msg = messages.get(data['status'])
        if msg:
            db.session.add(Notification(
                student_id=application.student_id,
                message=msg,
                is_read=False,
                created_at=datetime.utcnow()
            ))

    db.session.commit()
    cache.delete('admin_all_applications')
    return jsonify({'message': 'Application updated'}), 200


@admin_bp.route('/drives', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_all_drives')
def get_all_drives(current_user):
    drives = Drive.query.all()
    result = []
    for d in drives:
        company = Company.query.get(d.company_id)
        company_user = User.query.get(company.user_id) if company else None
        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'company_name': company_user.username if company_user else 'N/A',
            'is_closed': d.is_closed,
            'admin_status': d.admin_status or 'Pending'
        })
    return jsonify(result), 200


@admin_bp.route('/student-profile/<int:user_id>', methods=['GET'])
@admin_required
def get_student_profile(current_user, user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return jsonify({'message': 'Student not found'}), 404
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    applications = Application.query.filter_by(student_id=student.id).all()
    apps_data = []
    for a in applications:
        drive = Drive.query.get(a.drive_id)
        if drive:
            company = Company.query.get(drive.company_id)
            company_user = User.query.get(company.user_id) if company else None
            apps_data.append({
                'job_title': drive.job_title,
                'company_name': company_user.username if company_user else 'N/A',
                'status': a.status
            })

    return jsonify({
        'id': student.id,
        'user_id': student.user_id,
        'username': user.username,
        'name': student.name,
        'department': student.department,
        'is_blacklisted': user.is_blacklisted,
        'resume_uploaded': bool(student.resume_filename),
        'applications': apps_data,
        'email': student.email or '',
        'phone': student.phone or '',
        'location': student.location or ''
    }), 200


@admin_bp.route('/company-profile/<int:user_id>', methods=['GET'])
@admin_required
def get_company_profile(current_user, user_id):
    company = Company.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({'message': 'Company not found'}), 404
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    drives = Drive.query.filter_by(company_id=company.id).all()
    drives_data = []
    for d in drives:
        app_count = Application.query.filter_by(drive_id=d.id).count()
        drives_data.append({
            'job_title': d.job_title,
            'is_closed': d.is_closed,
            'application_count': app_count,
            'location': d.location,
        })
        
    return jsonify({
        'id': company.id,
        'user_id': company.user_id,
        'username': user.username,
        'approved': company.approved,
        'is_blacklisted': user.is_blacklisted,
        'overview': company.overview or '',
        'company_name': company.company_name or '',
        'hr_contact': company.hr_contact or '',
        'website': company.website or '',
        'drives': drives_data
    }), 200

# Pending Drives
@admin_bp.route('/drives/pending', methods=['GET'])
@admin_required
def pending_drives(current_user):
    drives = Drive.query.filter_by(admin_status='Pending').all()
    result = []
    for d in drives:
        company = Company.query.get(d.company_id)
        company_user = User.query.get(company.user_id) if company else None
        result.append({
            'id':d.id,
            'job_title': d.job_title,
            'drive_name':getattr(d, 'drive_name', ''),
            'description': d.description,
            'eligibility': getattr(d, 'eligibility', ''),
            'deadline': str(d.deadline) if d.deadline else '',
            'company_name': company_user.username if company_user else 'N/A',
            'admin_status': d.admin_status
        })
    return jsonify(result),200

#Approve Drive
@admin_bp.route('/drives/<int:drive_id>/approve', methods=['POST'])
@admin_required
def approve_drive(current_user, drive_id):
    drive = Drive.query.get(drive_id)
    if not drive:
        return jsonify({'message': 'Drive not found'}), 404
    drive.admin_status = 'Approved'
    db.session.commit()
    cache.delete('admin_all_drives')
    cache.delete('all_open_drives')
    return jsonify({'message': 'Drive approved'}), 200

#Reject Drive
@admin_bp.route('/drives/<int:drive_id>/reject', methods=['POST'])
@admin_required
def reject_drive(current_user, drive_id):
    drive = Drive.query.get(drive_id)
    if not drive:
        return jsonify({'message': 'Drive not found'}), 404
    drive.admin_status = 'Rejected'
    db.session.commit()
    cache.delete('admin_all_drives')
    cache.delete('all_open_drives')
    return jsonify({'message': 'Drive rejected'}), 200

#Export CSV
@admin_bp.route('/export/csv', methods=['GET'])
@admin_required
def export_csv(current_user):
    export_type = request.args.get('type', 'applications')
    if export_type not in {'applications', 'drives', 'students', 'companies'}:
        return jsonify({'message': 'Invalid export type'}), 400
 
    output = io.StringIO()
    writer = csv.writer(output)
 
    if export_type == 'applications':
        writer.writerow(['#', 'Student', 'Department', 'Company', 'Job Title', 'Status', 'Interview Type', 'Result', 'Remark'])
        for i, a in enumerate(Application.query.all(), 1):
            student = Student.query.get(a.student_id)
            drive   = Drive.query.get(a.drive_id)
            s_user  = User.query.get(student.user_id) if student else None
            company = Company.query.get(drive.company_id) if drive else None
            c_user  = User.query.get(company.user_id) if company else None
            writer.writerow([i,
                s_user.username if s_user else 'N/A',
                student.department if student else 'N/A',
                c_user.username if c_user else 'N/A',
                drive.job_title if drive else 'N/A',
                a.status, a.interview_type or '', a.result or '', a.remark or ''])
 
    elif export_type == 'drives':
        writer.writerow(['#', 'Drive Name', 'Job Title', 'Company', 'Location', 'Deadline', 'Status', 'Applications'])
        for i, d in enumerate(Drive.query.all(), 1):
            company = Company.query.get(d.company_id)
            c_user  = User.query.get(company.user_id) if company else None
            writer.writerow([i, d.drive_name or '', d.job_title,
                c_user.username if c_user else 'N/A',
                d.location or '', d.deadline or '',
                'Closed' if d.is_closed else 'Open',
                Application.query.filter_by(drive_id=d.id).count()])
 
    elif export_type == 'students':
        writer.writerow(['#', 'Username', 'Name', 'Department', 'Email', 'Phone', 'Location', 'Resume', 'Status', 'Applications'])
        for i, s in enumerate(Student.query.all(), 1):
            user = User.query.get(s.user_id)
            writer.writerow([i,
                user.username if user else 'N/A',
                s.name or '', s.department or '', s.email or '',
                s.phone or '', s.location or '',
                'Yes' if s.resume_filename else 'No',
                'Blacklisted' if (user and user.is_blacklisted) else 'Active',
                Application.query.filter_by(student_id=s.id).count()])
 
    elif export_type == 'companies':
        writer.writerow(['#', 'Username', 'Status', 'Blacklisted', 'Drives'])
        for i, c in enumerate(Company.query.all(), 1):
            user = User.query.get(c.user_id)
            writer.writerow([i,
                user.username if user else 'N/A',
                'Approved' if c.approved else 'Pending',
                'Yes' if (user and user.is_blacklisted) else 'No',
                Drive.query.filter_by(company_id=c.id).count()])
 
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{export_type}_report.csv"'
    return response
 
 
# Export PDF 
@admin_bp.route('/export/pdf', methods=['GET'])
@admin_required
def export_pdf(current_user):
    export_type = request.args.get('type', 'applications')
    if export_type not in {'applications', 'drives', 'students', 'companies'}:
        return jsonify({'message': 'Invalid export type'}), 400
 
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ])
    elements = []
 
    if export_type == 'applications':
        elements += [Paragraph('Placement Portal — Applications Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Student', 'Department', 'Company', 'Job Title', 'Status', 'Interview', 'Result']]
        for i, a in enumerate(Application.query.all(), 1):
            student = Student.query.get(a.student_id)
            drive   = Drive.query.get(a.drive_id)
            s_user  = User.query.get(student.user_id) if student else None
            company = Company.query.get(drive.company_id) if drive else None
            c_user  = User.query.get(company.user_id) if company else None
            data.append([str(i),
                s_user.username if s_user else 'N/A',
                student.department if student else 'N/A',
                c_user.username if c_user else 'N/A',
                drive.job_title if drive else 'N/A',
                a.status, a.interview_type or '—', a.result or '—'])
 
    elif export_type == 'drives':
        elements += [Paragraph('Placement Portal — Drives Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Drive Name', 'Job Title', 'Company', 'Location', 'Deadline', 'Status', 'Applications']]
        for i, d in enumerate(Drive.query.all(), 1):
            company = Company.query.get(d.company_id)
            c_user  = User.query.get(company.user_id) if company else None
            data.append([str(i), d.drive_name or '—', d.job_title,
                c_user.username if c_user else 'N/A',
                d.location or '—', d.deadline or '—',
                'Closed' if d.is_closed else 'Open',
                str(Application.query.filter_by(drive_id=d.id).count())])
 
    elif export_type == 'students':
        elements += [Paragraph('Placement Portal — Students Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Username', 'Name', 'Department', 'Email', 'Status', 'Resume', 'Applications']]
        for i, s in enumerate(Student.query.all(), 1):
            user = User.query.get(s.user_id)
            data.append([str(i),
                user.username if user else 'N/A',
                s.name or '—', s.department or '—', s.email or '—',
                'Blacklisted' if (user and user.is_blacklisted) else 'Active',
                'Yes' if s.resume_filename else 'No',
                str(Application.query.filter_by(student_id=s.id).count())])
 
    elif export_type == 'companies':
        elements += [Paragraph('Placement Portal — Companies Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Username', 'Status', 'Blacklisted', 'Drives']]
        for i, c in enumerate(Company.query.all(), 1):
            user = User.query.get(c.user_id)
            data.append([str(i),
                user.username if user else 'N/A',
                'Approved' if c.approved else 'Pending',
                'Yes' if (user and user.is_blacklisted) else 'No',
                str(Drive.query.filter_by(company_id=c.id).count())])
 
    table = Table(data, repeatRows=1)
    table.setStyle(header_style)
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
 
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{export_type}_report.pdf"'
    return response