import os

from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from datetime import datetime

app = Flask(__name__)

# Email configuration
EMAIL_ADDRESS = "vidhyastudent754@gmail.com"
EMAIL_PASSWORD = "bzow hxne muhz aqxq"
EMAIL_SMTP = "smtp.gmail.com"
EMAIL_PORT = 587

# In-memory data storage
students = []
attendance = {}

def send_absence_email(parent_email, student_name, class_name, date):
    try:
        subject = f"🎓 Absence Notification - {student_name}"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .alert-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .alert-box h3 {{
            color: #856404;
            margin: 0 0 10px 0;
        }}
        .student-info {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .student-info p {{
            margin: 8px 0;
            color: #333;
        }}
        .student-info strong {{
            color: #667eea;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin: 20px 0;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 School Attendance Alert</h1>
            <p>Important Notification Regarding Your Child</p>
        </div>
        <div class="content">
            <div class="alert-box">
                <h3>⚠️ Absence Notification</h3>
                <p>We regret to inform you that your child was marked absent from school.</p>
            </div>
            
            <div class="student-info">
                <p><strong>Student Name:</strong> {student_name}</p>
                <p><strong>Class:</strong> {class_name}</p>
                <p><strong>Date of Absence:</strong> {date}</p>
            </div>
            
            <p>Dear Parent,</p>
            <p>This is to inform you that your child, <strong>{student_name}</strong>, was absent from class <strong>{class_name}</strong> on <strong>{date}</strong>.</p>
            
            <p>Please ensure they attend the next class and complete any missed work. If this absence was planned or if there are any concerns, please contact the school administration.</p>
            
            <a href="#" class="button">Contact School Administration</a>
            
            <p>Thank you for your attention to this matter.</p>
        </div>
        <div class="footer">
            <p><strong>School Administration</strong></p>
            <p>Email: vidhyastudent754@gmail.com</p>
            <p>This is an automated message. Please do not reply directly to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = parent_email
        msg['Subject'] = subject
        
        # Attach both plain text and HTML versions
        plain_text = f"""
Dear Parent,

This is to inform you that your child, {student_name}, was absent from class {class_name} on {date}.

Please ensure they attend the next class and complete any missed work.

Best regards,
School Administration
"""
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/students', methods=['GET', 'POST'])
def students():
    if request.method == 'GET':
        return jsonify(students)
    elif request.method == 'POST':
        data = request.json
        student = {
            'id': len(students) + 1,
            'name': data['name'],
            'roll_number': data['roll_number'],
            'class': data['class'],
            'parent_email': data['parent_email']
        }
        students.append(student)
        return jsonify(student), 201

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    
    date = datetime.now().strftime("%Y-%m-%d")
    absent_students = []
    
    if date not in attendance:
        attendance[date] = {}
    
    for student_id, status in data['attendance'].items():
        attendance[date][student_id] = status
        if status == 'absent':
            student = next((s for s in students if str(s['id']) == str(student_id)), None)
            if student:
                absent_students.append(student)
    
    # Send emails to parents of absent students
    email_results = []
    for student in absent_students:
        success, message = send_absence_email(
            student['parent_email'],
            student['name'],
            student['class'],
            date
        )
        email_results.append({
            'student': student['name'],
            'email': student['parent_email'],
            'success': success,
            'message': message
        })
    
    return jsonify({
        'date': date,
        'absent_count': len(absent_students),
        'email_results': email_results
    })

@app.route('/api/attendance/<date>', methods=['GET'])
def get_attendance(date):
    if date in attendance:
        return jsonify(attendance[date])
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", "3000")))
