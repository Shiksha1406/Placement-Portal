from celery import Celery
from celery.schedules import crontab


def create_app():
    from app import app
    return app


app = create_app()

celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'],
)

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    broker_connection_retry_on_startup=True,
)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

celery.conf.beat_schedule = {
    'monthly-placement-report': {
        'task': 'tasks.send_monthly_report',
        'schedule': crontab(hour=8, minute=0, day_of_month=1),
    },
    'daily-deadline-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),  
    },
}
celery.conf.timezone = 'Asia/Kolkata'


#Status metadata

_STATUS_META = {
    'Shortlisted': {
        'icon': '🎉',
        'subject': 'Congratulations — You have been Shortlisted!',
        'heading': 'You have been shortlisted!',
        'color': '#16a34a',
        'bg': '#f0fdf4',
        'border': '#bbf7d0',
        'body': (
            'Great news! You have been shortlisted for the <strong>{job_title}</strong> '
            'position at <strong>{company_name}</strong>. '
            'The recruitment team will reach out with next steps shortly — keep an eye on '
            'your inbox and notifications.'
        ),
    },
    'Waitlisted': {
        'icon': '⏳',
        'subject': 'Application Update — You are on the Waitlist',
        'heading': 'You have been waitlisted',
        'color': '#b45309',
        'bg': '#fffbeb',
        'border': '#fde68a',
        'body': (
            'Your application for <strong>{job_title}</strong> at '
            '<strong>{company_name}</strong> is currently on the waitlist. '
            'This means you are still under consideration. '
            'We will notify you as soon as there is an update — stay tuned!'
        ),
    },
    'Rejected': {
        'icon': '📋',
        'subject': 'Application Update — {company_name}',
        'heading': 'Application status update',
        'color': '#dc2626',
        'bg': '#fef2f2',
        'border': '#fecaca',
        'body': (
            'Thank you for applying for <strong>{job_title}</strong> at '
            '<strong>{company_name}</strong>. After careful review, we regret to inform '
            'you that your application has not been selected at this time. '
            'We encourage you to keep applying — there are many more opportunities ahead!'
        ),
    },
    'Selected': {
        'icon': '🎉',
        'subject': 'Congratulations — You have been Selected!',
        'heading': 'You have been selected!',
        'color': '#0369a1',
        'bg': '#eff6ff',
        'border': '#bfdbfe',
        'body': (
            'Congratulations! We are thrilled to inform you that you have been '
            'selected for the <strong>{job_title}</strong> position at '
            '<strong>{company_name}</strong>. '
            'The team will be in touch shortly with further details. '
            'Best of luck on this exciting new journey!'
        ),
    },
}


def _build_email_html(student_name, job_title, company_name, new_status):
    """Return a clean HTML email body for the given status."""
    meta = _STATUS_META.get(new_status, {})
    icon = meta.get('icon', 'ℹ️')
    heading = meta.get('heading', f'Application status: {new_status}')
    color = meta.get('color', '#334155')
    bg = meta.get('bg', '#f8fafc')
    border = meta.get('border', '#e2e8f0')
    body = meta.get('body', 'Your application status has been updated.').format(
        job_title=job_title, company_name=company_name
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Application Update</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:16px;overflow:hidden;
                      box-shadow:0 4px 24px rgba(0,0,0,0.08);">
          <tr>
            <td style="background:{color};padding:28px 40px;">
              <p style="margin:0;font-size:28px;">{icon}</p>
              <h1 style="margin:10px 0 0;color:#ffffff;font-size:22px;font-weight:600;
                         letter-spacing:-0.3px;">{heading}</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:32px 40px;">
              <p style="margin:0 0 16px;font-size:15px;color:#334155;line-height:1.6;">
                Hi <strong>{student_name}</strong>,
              </p>
              <p style="margin:0 0 24px;font-size:15px;color:#334155;line-height:1.7;">
                {body}
              </p>
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:{bg};border:1px solid {border};
                            border-radius:10px;margin-bottom:24px;">
                <tr>
                  <td style="padding:18px 22px;">
                    <p style="margin:0 0 6px;font-size:11px;font-weight:600;
                               color:{color};text-transform:uppercase;
                               letter-spacing:0.8px;">Application status</p>
                    <p style="margin:0;font-size:17px;font-weight:600;color:{color};">
                      {new_status}
                    </p>
                    <p style="margin:6px 0 0;font-size:13px;color:#64748b;">
                      {job_title} &nbsp;·&nbsp; {company_name}
                    </p>
                  </td>
                </tr>
              </table>
              <p style="margin:0;font-size:14px;color:#64748b;line-height:1.6;">
                You can check all your application updates in real-time on the
                <strong>Placement Portal</strong>.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background:#f8fafc;padding:20px 40px;border-top:1px solid #e2e8f0;">
              <p style="margin:0;font-size:12px;color:#94a3b8;line-height:1.6;">
                This is an automated notification from the Placement Portal.
                Please do not reply to this email.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


# Tasks

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_status_email(self, student_email, student_name, job_title, company_name, new_status):
    """
    Send an application-status update email to a student.
    Retries up to 3 times (60 s apart) on transient mail server errors.
    """
    if not student_email:
        print(f'[tasks] send_status_email skipped — no email for "{student_name}"')
        return
    if not app.config.get('MAIL_SERVER'):
        print('[tasks] send_status_email skipped — MAIL_SERVER not configured')
        return

    meta = _STATUS_META.get(new_status, {})
    subject = meta.get('subject', f'Application Update — {new_status}').format(
        company_name=company_name, job_title=job_title
    )

    try:
        from flask_mail import Message
        from extensions import mail

        msg = Message(
            subject=subject,
            recipients=[student_email],
            html=_build_email_html(student_name, job_title, company_name, new_status),
            body=(
                f'Hi {student_name},\n\n'
                f'Your application status for {job_title} at {company_name} '
                f'has been updated to: {new_status}.\n\n'
                f'Log in to the Placement Portal to view full details.\n'
            ),
        )
        mail.send(msg)
        print(f'[tasks] Email sent to {student_email} — status: {new_status}')
    except Exception as exc:
        print(f'[tasks] Email failed for {student_email}: {exc}')
        raise self.retry(exc=exc)


def _build_report_html(month_label, stats):
    """Build the HTML body for the monthly admin report email."""

    def row(label, value, color='#334155'):
        return (
            f'<tr>'
            f'<td style="padding:10px 16px;font-size:14px;color:#64748b;'
            f'border-bottom:1px solid #f1f5f9;">{label}</td>'
            f'<td style="padding:10px 16px;font-size:14px;font-weight:600;'
            f'color:{color};text-align:right;border-bottom:1px solid #f1f5f9;">{value}</td>'
            f'</tr>'
        )

    status_rows = ''.join([
        row('Applied', stats['applied'], '#334155'),
        row('Shortlisted', stats['shortlisted'], '#16a34a'),
        row('Waitlisted', stats['waitlisted'], '#b45309'),
        row('Rejected', stats['rejected'], '#dc2626'),
        row('Selected', stats['selected'], '#0369a1'),
    ])

    dept_rows = ''.join(
        row(dept or 'Unknown', count)
        for dept, count in sorted(stats['dept_breakdown'].items(), key=lambda x: -x[1])
    )

    top_drives_rows = ''.join(
        f'<tr>'
        f'<td style="padding:10px 16px;font-size:13px;color:#334155;'
        f'border-bottom:1px solid #f1f5f9;">{d["job_title"]}</td>'
        f'<td style="padding:10px 16px;font-size:13px;color:#64748b;'
        f'border-bottom:1px solid #f1f5f9;">{d["company"]}</td>'
        f'<td style="padding:10px 16px;font-size:13px;font-weight:600;'
        f'color:#0369a1;text-align:right;border-bottom:1px solid #f1f5f9;">'
        f'{d["applications"]}</td>'
        f'</tr>'
        for d in stats['top_drives']
    )

    top_drives_section = (
        '<tr><td style="padding:28px 40px 0;">'
        '<p style="margin:0 0 12px;font-size:11px;font-weight:600;color:#94a3b8;'
        'text-transform:uppercase;letter-spacing:0.8px;">Top drives by applications</p>'
        '<table width="100%" cellpadding="0" cellspacing="0" '
        'style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;">'
        '<tr style="background:#f8fafc;">'
        '<th style="padding:10px 16px;font-size:11px;color:#94a3b8;text-align:left;font-weight:600;">Job title</th>'
        '<th style="padding:10px 16px;font-size:11px;color:#94a3b8;text-align:left;font-weight:600;">Company</th>'
        '<th style="padding:10px 16px;font-size:11px;color:#94a3b8;text-align:right;font-weight:600;">Apps</th>'
        '</tr>'
        + top_drives_rows +
        '</table></td></tr>'
    ) if stats['top_drives'] else ''

    dept_section = (
        '<tr><td style="padding:28px 40px 0;">'
        '<p style="margin:0 0 12px;font-size:11px;font-weight:600;color:#94a3b8;'
        'text-transform:uppercase;letter-spacing:0.8px;">Applications by department</p>'
        '<table width="100%" cellpadding="0" cellspacing="0" '
        'style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;">'
        + dept_rows +
        '</table></td></tr>'
    ) if stats['dept_breakdown'] else ''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monthly Placement Report</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
  <tr><td align="center">
  <table width="600" cellpadding="0" cellspacing="0"
         style="background:#ffffff;border-radius:16px;overflow:hidden;
                box-shadow:0 4px 24px rgba(0,0,0,0.08);">
    <tr>
      <td style="background:#0f172a;padding:32px 40px;">
        <p style="margin:0;font-size:12px;font-weight:600;color:#94a3b8;
                  text-transform:uppercase;letter-spacing:1px;">Placement Portal</p>
        <h1 style="margin:8px 0 0;color:#ffffff;font-size:24px;font-weight:600;">Monthly Report</h1>
        <p style="margin:6px 0 0;font-size:14px;color:#94a3b8;">{month_label}</p>
      </td>
    </tr>
    <tr>
      <td style="padding:32px 40px 0;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="25%" style="padding-right:8px;">
              <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px;text-align:center;">
                <p style="margin:0;font-size:26px;font-weight:700;color:#16a34a;">{stats['total_applications']}</p>
                <p style="margin:4px 0 0;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;">Applications</p>
              </div>
            </td>
            <td width="25%" style="padding:0 8px;">
              <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px;text-align:center;">
                <p style="margin:0;font-size:26px;font-weight:700;color:#1d4ed8;">{stats['total_drives']}</p>
                <p style="margin:4px 0 0;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;">Drives</p>
              </div>
            </td>
            <td width="25%" style="padding:0 8px;">
              <div style="background:#fefce8;border:1px solid #fde68a;border-radius:10px;padding:16px;text-align:center;">
                <p style="margin:0;font-size:26px;font-weight:700;color:#b45309;">{stats['total_students']}</p>
                <p style="margin:4px 0 0;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;">Students</p>
              </div>
            </td>
            <td width="25%" style="padding-left:8px;">
              <div style="background:#fdf4ff;border:1px solid #e9d5ff;border-radius:10px;padding:16px;text-align:center;">
                <p style="margin:0;font-size:26px;font-weight:700;color:#7e22ce;">{stats['total_companies']}</p>
                <p style="margin:4px 0 0;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:0.6px;">Companies</p>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 40px 0;">
        <p style="margin:0 0 12px;font-size:11px;font-weight:600;color:#94a3b8;
                  text-transform:uppercase;letter-spacing:0.8px;">Application status breakdown</p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="border:1px solid #e2e8f0;border-radius:10px;overflow:hidden;">
          {status_rows}
        </table>
      </td>
    </tr>
    {top_drives_section}
    {dept_section}
    <tr>
      <td style="padding:28px 40px;">
        <p style="margin:0;font-size:12px;color:#94a3b8;line-height:1.6;">
          This report is auto-generated by Celery Beat on the 1st of every month.<br>
          Please do not reply to this email.
        </p>
      </td>
    </tr>
  </table>
  </td></tr>
</table>
</body>
</html>"""


@celery.task(bind=True, max_retries=2, default_retry_delay=120)
def send_monthly_report(self):
    """
    Celery Beat task — runs on the 1st of every month at 08:00 IST.
    Queries live DB stats and emails a placement summary to every admin user.
    """
    from datetime import datetime
    from models import User, Student, Company, Drive, Application
    from flask_mail import Message
    from extensions import mail

    if not app.config.get('MAIL_SERVER'):
        print('[tasks] send_monthly_report skipped — MAIL_SERVER not configured')
        return

    all_apps = Application.query.all()
    all_drives = Drive.query.all()
    all_students = Student.query.all()
    all_companies = Company.query.filter_by(approved=True).all()

    status_counts = {'Applied': 0, 'Shortlisted': 0, 'Waitlisted': 0, 'Rejected': 0, 'Selected': 0}
    dept_breakdown = {}

    for a in all_apps:
        key = a.status if a.status in status_counts else 'Applied'
        status_counts[key] += 1
        student = Student.query.get(a.student_id)
        if student and student.department:
            dept_breakdown[student.department] = dept_breakdown.get(student.department, 0) + 1

    drive_app_counts = []
    for d in all_drives:
        count = Application.query.filter_by(drive_id=d.id).count()
        company = Company.query.get(d.company_id)
        c_user = User.query.get(company.user_id) if company else None
        drive_app_counts.append({
            'job_title': d.job_title,
            'company': c_user.username if c_user else 'Unknown',
            'applications': count,
        })
    top_drives = sorted(drive_app_counts, key=lambda x: -x['applications'])[:5]

    stats = {
        'total_applications': len(all_apps),
        'total_drives': len(all_drives),
        'total_students': len(all_students),
        'total_companies': len(all_companies),
        'applied': status_counts['Applied'],
        'shortlisted': status_counts['Shortlisted'],
        'waitlisted': status_counts['Waitlisted'],
        'rejected': status_counts['Rejected'],
        'selected': status_counts['Selected'],
        'dept_breakdown': dept_breakdown,
        'top_drives': top_drives,
    }

    month_label = datetime.now().strftime('%B %Y')
    html_body = _build_report_html(month_label, stats)

    admin_emails = [
        u.username for u in User.query.filter_by(role='admin').all()
        if '@' in (u.username or '')
    ]
    if not admin_emails:
        print('[tasks] send_monthly_report — no admin email addresses found')
        return

    try:
        msg = Message(
            subject=f'Placement Portal — Monthly Report ({month_label})',
            recipients=admin_emails,
            html=html_body,
            body=(
                f'Monthly Placement Report — {month_label}\n\n'
                f'Total applications : {stats["total_applications"]}\n'
                f'Total drives       : {stats["total_drives"]}\n'
                f'Total students     : {stats["total_students"]}\n'
                f'Total companies    : {stats["total_companies"]}\n\n'
                f'Status breakdown\n'
                f'  Applied     : {stats["applied"]}\n'
                f'  Shortlisted : {stats["shortlisted"]}\n'
                f'  Waitlisted  : {stats["waitlisted"]}\n'
                f'  Rejected    : {stats["rejected"]}\n'
                f'  Selected    : {stats["selected"]}\n'
            ),
        )
        mail.send(msg)
        print(f'[tasks] Monthly report sent to {admin_emails} for {month_label}')
    except Exception as exc:
        print(f'[tasks] Monthly report failed: {exc}')
        raise self.retry(exc=exc)


@celery.task(bind=True)
def generate_csv_export(self, export_type):
    import csv
    import io
    from models import Application, Student, Drive, Company, User

    output = io.StringIO()
    writer = csv.writer(output)

    if export_type == 'applications':
        writer.writerow(['#', 'Student', 'Department', 'Company', 'Job Title', 'Status', 'Interview Type', 'Result', 'Remark'])
        for i, a in enumerate(Application.query.all(), 1):
            student = Student.query.get(a.student_id)
            drive = Drive.query.get(a.drive_id)
            s_user = User.query.get(student.user_id) if student else None
            company = Company.query.get(drive.company_id) if drive else None
            c_user = User.query.get(company.user_id) if company else None
            writer.writerow([
                i,
                s_user.username if s_user else 'N/A',
                student.department if student else 'N/A',
                c_user.username if c_user else 'N/A',
                drive.job_title if drive else 'N/A',
                a.status, a.interview_type or '', a.result or '', a.remark or '',
            ])

    elif export_type == 'drives':
        writer.writerow(['#', 'Drive Name', 'Job Title', 'Company', 'Location', 'Deadline', 'Status', 'Applications'])
        for i, d in enumerate(Drive.query.all(), 1):
            company = Company.query.get(d.company_id)
            c_user = User.query.get(company.user_id) if company else None
            writer.writerow([
                i, d.drive_name or '', d.job_title,
                c_user.username if c_user else 'N/A',
                d.location or '', d.deadline or '',
                'Closed' if d.is_closed else 'Open',
                Application.query.filter_by(drive_id=d.id).count(),
            ])

    elif export_type == 'students':
        writer.writerow(['#', 'Username', 'Name', 'Department', 'Email', 'Phone', 'Location', 'Resume', 'Status', 'Applications'])
        for i, s in enumerate(Student.query.all(), 1):
            user = User.query.get(s.user_id)
            writer.writerow([
                i, user.username if user else 'N/A',
                s.name or '', s.department or '', s.email or '',
                s.phone or '', s.location or '',
                'Yes' if s.resume_filename else 'No',
                'Blacklisted' if (user and user.is_blacklisted) else 'Active',
                Application.query.filter_by(student_id=s.id).count(),
            ])

    elif export_type == 'companies':
        writer.writerow(['#', 'Username', 'Status', 'Blacklisted', 'Drives'])
        for i, c in enumerate(Company.query.all(), 1):
            user = User.query.get(c.user_id)
            writer.writerow([
                i,
                user.username if user else 'N/A',
                'Approved' if c.approved else 'Pending',
                'Yes' if (user and user.is_blacklisted) else 'No',
                Drive.query.filter_by(company_id=c.id).count(),
            ])

    return output.getvalue()


@celery.task(bind=True)
def generate_pdf_export(self, export_type):
    import io
    import base64
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from models import Application, Student, Drive, Company, User

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30,
    )
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
            drive = Drive.query.get(a.drive_id)
            s_user = User.query.get(student.user_id) if student else None
            company = Company.query.get(drive.company_id) if drive else None
            c_user = User.query.get(company.user_id) if company else None
            data.append([
                str(i),
                s_user.username if s_user else 'N/A',
                student.department if student else 'N/A',
                c_user.username if c_user else 'N/A',
                drive.job_title if drive else 'N/A',
                a.status, a.interview_type or '—', a.result or '—',
            ])

    elif export_type == 'drives':
        elements += [Paragraph('Placement Portal — Drives Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Drive Name', 'Job Title', 'Company', 'Location', 'Deadline', 'Status', 'Applications']]
        for i, d in enumerate(Drive.query.all(), 1):
            company = Company.query.get(d.company_id)
            c_user = User.query.get(company.user_id) if company else None
            data.append([
                str(i), d.drive_name or '—', d.job_title,
                c_user.username if c_user else 'N/A',
                d.location or '—', d.deadline or '—',
                'Closed' if d.is_closed else 'Open',
                str(Application.query.filter_by(drive_id=d.id).count()),
            ])

    elif export_type == 'students':
        elements += [Paragraph('Placement Portal — Students Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Username', 'Name', 'Department', 'Email', 'Status', 'Resume', 'Applications']]
        for i, s in enumerate(Student.query.all(), 1):
            user = User.query.get(s.user_id)
            data.append([
                str(i), user.username if user else 'N/A',
                s.name or '—', s.department or '—', s.email or '—',
                'Blacklisted' if (user and user.is_blacklisted) else 'Active',
                'Yes' if s.resume_filename else 'No',
                str(Application.query.filter_by(student_id=s.id).count()),
            ])

    elif export_type == 'companies':
        elements += [Paragraph('Placement Portal — Companies Report', styles['h2']), Spacer(1, 12)]
        data = [['#', 'Username', 'Status', 'Blacklisted', 'Drives']]
        for i, c in enumerate(Company.query.all(), 1):
            user = User.query.get(c.user_id)
            data.append([
                str(i),
                user.username if user else 'N/A',
                'Approved' if c.approved else 'Pending',
                'Yes' if (user and user.is_blacklisted) else 'No',
                str(Drive.query.filter_by(company_id=c.id).count()),
            ])

    table = Table(data, repeatRows=1)
    table.setStyle(header_style)
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_daily_reminders(self):
    """
    Celery Beat task — runs every day at 08:00 IST.
    Sends deadline reminder emails to students whose applied drives
    have a deadline within the next 3 days.
    """
    import requests as _requests
    from models import Student, Drive, Application, User
    from flask_mail import Message
    from extensions import mail
    from datetime import datetime, timedelta

    today   = datetime.now().date()
    upcoming = today + timedelta(days=3)

    mail_ready   = bool(app.config.get('MAIL_SERVER'))

    if not app.config.get('MAIL_SERVER'):
        print('[tasks] send_daily_reminders skipped — MAIL_SERVER not configured')
        return


    drives = Drive.query.filter_by(is_closed=False, admin_status='Approved').all()

    for drive in drives:
        if not drive.deadline:
            continue
        try:
            deadline = datetime.strptime(drive.deadline, '%Y-%m-%d').date()
        except ValueError:
            continue

        if not (today <= deadline <= upcoming):
            continue

        days_left = (deadline - today).days
        days_label = 'today' if days_left == 0 else (
            'tomorrow' if days_left == 1 else f'in {days_left} days'
        )


        applications = Application.query.filter_by(drive_id=drive.id).all()

        for a in applications:
            student = Student.query.get(a.student_id)
            if not student:
                continue
            user = User.query.get(student.user_id)
            if not user or user.is_blacklisted:
                continue
            
            name       = student.name or user.username
            job_title  = drive.job_title
            deadline_s = drive.deadline

            #Email
            if mail_ready and student.email:
                try:
                    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Deadline Reminder</title></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
  <tr><td align="center">
  <table width="540" cellpadding="0" cellspacing="0"
         style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
    <tr>
      <td style="background:#f59e0b;padding:24px 36px;">
        <p style="margin:0;font-size:28px;">⏰</p>
        <h1 style="margin:8px 0 0;color:#fff;font-size:20px;font-weight:600;">Deadline Reminder</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:28px 36px;">
        <p style="margin:0 0 16px;font-size:15px;color:#334155;">Hi <strong>{name}</strong>,</p>
        <p style="margin:0 0 20px;font-size:15px;color:#334155;line-height:1.7;">
          The application deadline for <strong>{job_title}</strong> closes
          <strong>{days_label}</strong> on <strong>{deadline_s}</strong>.
          Don't miss out — log in to the Placement Portal to review your application.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;margin-bottom:20px;">
          <tr><td style="padding:16px 20px;">
            <p style="margin:0 0 4px;font-size:11px;font-weight:600;color:#b45309;
                      text-transform:uppercase;letter-spacing:.8px;">Drive closing</p>
            <p style="margin:0;font-size:16px;font-weight:600;color:#b45309;">{job_title}</p>
            <p style="margin:4px 0 0;font-size:13px;color:#64748b;">Deadline: {deadline_s}</p>
          </td></tr>
        </table>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          This is an automated reminder from the Placement Portal. Please do not reply.
        </p>
      </td>
    </tr>
  </table>
  </td></tr>
</table>
</body></html>"""
                    msg = Message(
                        subject=f'⏰ Reminder: {job_title} deadline is {days_label}',
                        recipients=[student.email],
                        html=html_body,
                        body=(
                            f'Hi {name},\n\n'
                            f'The application deadline for {job_title} closes '
                            f'{days_label} on {deadline_s}.\n\n'
                            f'Log in to the Placement Portal to check your status.\n'
                        ),
                    )
                    mail.send(msg)
                    print(f'[tasks] Email reminder → {student.email} | {job_title}')
                except Exception as e:
                    print(f'[tasks] Email reminder failed for {student.email}: {e}')


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_interview_email(self, student_email, student_name, job_title,
                         company_name, interview_date, interview_type,
                         interview_link, interview_notes):
    if not student_email:
        return
    if not app.config.get('MAIL_SERVER'):
        return

    from flask_mail import Message
    from extensions import mail

    link_row = (
        f'<p style="margin:8px 0 0;font-size:13px;color:#0369a1;">'
        f'<a href="{interview_link}">Join Link: {interview_link}</a></p>'
    ) if interview_link else ''

    notes_row = (
        f'<p style="margin:8px 0 0;font-size:13px;color:#64748b;">'
        f'Notes: {interview_notes}</p>'
    ) if interview_notes else ''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
  <tr><td align="center">
  <table width="560" cellpadding="0" cellspacing="0"
         style="background:#fff;border-radius:16px;overflow:hidden;
                box-shadow:0 4px 24px rgba(0,0,0,.08);">
    <tr>
      <td style="background:#0369a1;padding:28px 40px;">
        <p style="margin:0;font-size:28px;">📅</p>
        <h1 style="margin:10px 0 0;color:#fff;font-size:22px;font-weight:600;">
          Interview Scheduled</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:32px 40px;">
        <p style="margin:0 0 16px;font-size:15px;color:#334155;">
          Hi <strong>{student_name}</strong>,</p>
        <p style="margin:0 0 24px;font-size:15px;color:#334155;line-height:1.7;">
          Your interview for <strong>{job_title}</strong> at
          <strong>{company_name}</strong> has been scheduled.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#eff6ff;border:1px solid #bfdbfe;
                      border-radius:10px;margin-bottom:24px;">
          <tr><td style="padding:18px 22px;">
            <p style="margin:0;font-size:11px;font-weight:600;color:#0369a1;
                      text-transform:uppercase;letter-spacing:.8px;">Interview details</p>
            <p style="margin:8px 0 0;font-size:15px;font-weight:600;color:#0369a1;">
              {interview_date}</p>
            <p style="margin:6px 0 0;font-size:13px;color:#64748b;">
              Type: {interview_type}</p>
            {link_row}
            {notes_row}
          </td></tr>
        </table>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          This is an automated notification. Please do not reply.</p>
      </td>
    </tr>
  </table>
  </td></tr>
</table>
</body></html>"""

    try:
        msg = Message(
            subject=f'📅 Interview Scheduled — {job_title} at {company_name}',
            recipients=[student_email],
            html=html,
            body=(
                f'Hi {student_name},\n\n'
                f'Your interview for {job_title} at {company_name} '
                f'is scheduled on {interview_date}.\n'
                f'Type: {interview_type}\n'
                f'{("Link: " + interview_link) if interview_link else ""}\n'
                f'{("Notes: " + interview_notes) if interview_notes else ""}\n\n'
                f'Log in to the Placement Portal for full details.\n'
            ),
        )
        mail.send(msg)
        print(f'[tasks] Interview email sent to {student_email}')
    except Exception as exc:
        print(f'[tasks] Interview email failed for {student_email}: {exc}')
        raise self.retry(exc=exc)
    

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_final_result_email(self, student_email, student_name, job_title, company_name, result):
    if not student_email:
        return
    if not app.config.get('MAIL_SERVER'):
        return

    from flask_mail import Message
    from extensions import mail

    if result == 'Passed':
        subject = 'Congratulations — You have been Selected!'
        heading = 'You have been selected!'
        color   = '#16a34a'
        bg      = '#f0fdf4'
        border  = '#bbf7d0'
        icon    = '🎉'
        body    = (f'We are thrilled to inform you that you have <strong>passed</strong> '
                   f'the interview for <strong>{job_title}</strong> at '
                   f'<strong>{company_name}</strong>. Welcome aboard!')
    else:
        subject = f'Interview Result — {job_title} at {company_name}'
        heading = 'Interview result update'
        color   = '#dc2626'
        bg      = '#fef2f2'
        border  = '#fecaca'
        icon    = '📋'
        body    = (f'Thank you for interviewing for <strong>{job_title}</strong> at '
                   f'<strong>{company_name}</strong>. Unfortunately, you were not '
                   f'selected this time. Keep applying!')

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
  <tr><td align="center">
  <table width="560" cellpadding="0" cellspacing="0"
         style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">
    <tr>
      <td style="background:{color};padding:28px 40px;">
        <p style="margin:0;font-size:28px;">{icon}</p>
        <h1 style="margin:10px 0 0;color:#fff;font-size:22px;font-weight:600;">{heading}</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:32px 40px;">
        <p style="margin:0 0 16px;font-size:15px;color:#334155;">Hi <strong>{student_name}</strong>,</p>
        <p style="margin:0 0 24px;font-size:15px;color:#334155;line-height:1.7;">{body}</p>
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:{bg};border:1px solid {border};border-radius:10px;margin-bottom:24px;">
          <tr><td style="padding:18px 22px;">
            <p style="margin:0;font-size:11px;font-weight:600;color:{color};
                      text-transform:uppercase;letter-spacing:.8px;">Result</p>
            <p style="margin:8px 0 0;font-size:17px;font-weight:600;color:{color};">{result}</p>
            <p style="margin:6px 0 0;font-size:13px;color:#64748b;">{job_title} · {company_name}</p>
          </td></tr>
        </table>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          This is an automated notification. Please do not reply.</p>
      </td>
    </tr>
  </table>
  </td></tr>
</table>
</body></html>"""

    try:
        msg = Message(
            subject=subject,
            recipients=[student_email],
            html=html,
            body=(
                f'Hi {student_name},\n\n'
                f'Your interview result for {job_title} at {company_name}: {result}\n\n'
                f'Log in to the Placement Portal for details.\n'
            ),
        )
        mail.send(msg)
        print(f'[tasks] Final result email sent to {student_email} — result: {result}')
    except Exception as exc:
        print(f'[tasks] Final result email failed for {student_email}: {exc}')
        raise self.retry(exc=exc)