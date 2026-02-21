const express = require('express');
const fs = require('fs');           // ← added
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static('.'));

const DATA_FILE = './students.json';
let students = [];

// Load students from file when server starts (if file exists)
if (fs.existsSync(DATA_FILE)) {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        students = JSON.parse(data);
        console.log(`Loaded ${students.length} student(s) from ${DATA_FILE}`);
    } catch (err) {
        console.error('Error reading students.json - starting with empty list:', err.message);
        students = [];
    }
}

app.post('/register', (req, res) => {
    let { name, email, age, course } = req.body;

    if (!name || !email || !age || !course) {
        return res.status(400).json({ success: false, message: 'All fields required' });
    }

    // Basic cleanup
    name = String(name).trim();
    email = String(email).trim().toLowerCase();
    course = String(course).trim();
    age = Number(age);

    if (isNaN(age) || age < 16 || age > 120) {
        return res.status(400).json({ success: false, message: 'Age must be a number between 16 and 120' });
    }

    // Optional: prevent duplicate emails
    if (students.some(student => student.email === email)) {
        return res.status(409).json({ success: false, message: 'This email is already registered' });
    }

    const newStudent = { name, email, age, course, registeredAt: new Date().toISOString() };
    students.push(newStudent);

    // Save to file (async - doesn't block response)
    fs.writeFile(DATA_FILE, JSON.stringify(students, null, 2), (err) => {
        if (err) {
            console.error('Failed to save students.json:', err.message);
            // Note: we still return success to user — data is in memory
        } else {
            console.log(`Saved ${students.length} student(s)`);
        }
    });

    res.json({ success: true, message: 'Registration successful!' });
});

app.get('/health', (req, res) => {
    res.json({ status: 'OK' });
});

// Optional: endpoint to see all students (useful for testing)
app.get('/students', (req, res) => {
    res.json(students);
});

if (process.env.NODE_ENV !== 'test') {
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
        console.log(`Data will be saved to: ${DATA_FILE}`);
    });
}

module.exports = app;