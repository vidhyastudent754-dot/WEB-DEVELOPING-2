let students = [];
let attendanceData = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadStudents();
    displayCurrentDate();
    
    // Register form submission
    document.getElementById('register-form').addEventListener('submit', function(e) {
        e.preventDefault();
        registerStudent();
    });
});

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load data when switching tabs
    if (tabName === 'attendance') {
        loadAttendanceForm();
    } else if (tabName === 'students') {
        displayStudents();
    }
}

function displayCurrentDate() {
    const today = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);
}

async function loadStudents() {
    try {
        const response = await fetch('/api/students');
        students = await response.json();
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

async function registerStudent() {
    const form = document.getElementById('register-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch('/api/students', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const student = await response.json();
            showMessage('register-message', 'Student registered successfully!', 'success');
            form.reset();
            loadStudents();
        } else {
            showMessage('register-message', 'Error registering student. Please try again.', 'error');
        }
    } catch (error) {
        showMessage('register-message', 'Error: ' + error.message, 'error');
    }
}

function loadAttendanceForm() {
    const attendanceList = document.getElementById('attendance-list');
    
    if (students.length === 0) {
        attendanceList.innerHTML = '<p class="loading">No students registered yet. Please register students first.</p>';
        return;
    }
    
    attendanceList.innerHTML = students.map(student => `
        <div class="student-item">
            <div class="student-info">
                <h3>${student.name}</h3>
                <p>Roll No: ${student.roll_number} | Class: ${student.class}</p>
            </div>
            <div class="attendance-buttons">
                <button class="attendance-btn present" onclick="markAttendance(${student.id}, 'present', this)">Present</button>
                <button class="attendance-btn absent" onclick="markAttendance(${student.id}, 'absent', this)">Absent</button>
            </div>
        </div>
    `).join('');
    
    // Reset attendance data
    attendanceData = {};
}

function markAttendance(studentId, status, button) {
    attendanceData[studentId] = status;
    
    // Remove active class from both buttons
    const buttons = button.parentElement.querySelectorAll('.attendance-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Add active class to clicked button
    button.classList.add('active');
}

async function submitAttendance() {
    if (Object.keys(attendanceData).length === 0) {
        showMessage('attendance-message', 'Please mark attendance for at least one student.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ attendance: attendanceData })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            let message = `Attendance submitted successfully! ${result.absent_count} student(s) marked absent.`;
            
            if (result.email_results && result.email_results.length > 0) {
                message += '<div class="email-results"><h3>Email Notifications:</h3>';
                result.email_results.forEach(emailResult => {
                    const statusClass = emailResult.success ? 'success' : 'error';
                    message += `
                        <div class="email-result-item ${statusClass}">
                            <strong>${emailResult.student}</strong> (${emailResult.email}): 
                            ${emailResult.success ? 'Email sent' : 'Failed - ' + emailResult.message}
                        </div>
                    `;
                });
                message += '</div>';
            }
            
            showMessage('attendance-message', message, 'success');
            
            // Reset the form after 3 seconds
            setTimeout(() => {
                loadAttendanceForm();
                document.getElementById('attendance-message').style.display = 'none';
            }, 5000);
        } else {
            showMessage('attendance-message', 'Error submitting attendance. Please try again.', 'error');
        }
    } catch (error) {
        showMessage('attendance-message', 'Error: ' + error.message, 'error');
    }
}

function displayStudents() {
    const studentsList = document.getElementById('students-list');
    
    if (students.length === 0) {
        studentsList.innerHTML = '<p class="loading">No students registered yet.</p>';
        return;
    }
    
    studentsList.innerHTML = `
        <table class="student-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Roll Number</th>
                    <th>Class</th>
                    <th>Parent Email</th>
                </tr>
            </thead>
            <tbody>
                ${students.map(student => `
                    <tr>
                        <td>${student.name}</td>
                        <td>${student.roll_number}</td>
                        <td>${student.class}</td>
                        <td>${student.parent_email}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function showMessage(elementId, message, type) {
    const messageElement = document.getElementById(elementId);
    messageElement.innerHTML = message;
    messageElement.className = 'message ' + type;
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 5000);
    }
}
