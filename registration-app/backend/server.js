const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Excel file path
const excelFilePath = path.join(__dirname, 'registrations.xlsx');

// Initialize Excel file if it doesn't exist
function initializeExcelFile() {
    if (!fs.existsSync(excelFilePath)) {
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet([
            ['ID', 'Name', 'Email', 'Phone', 'Date of Registration']
        ]);
        XLSX.utils.book_append_sheet(wb, ws, 'Registrations');
        XLSX.writeFile(wb, excelFilePath);
        console.log('✅ Excel file created successfully!');
    }
}

// Initialize on startup
initializeExcelFile();

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'Server is running!' });
});

// Get all registrations
app.get('/api/registrations', (req, res) => {
    try {
        if (!fs.existsSync(excelFilePath)) {
            return res.json([]);
        }

        const workbook = XLSX.readFile(excelFilePath);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet);

        res.json(data);
    } catch (error) {
        console.error('Error reading registrations:', error);
        res.status(500).json({ error: 'Failed to read registrations' });
    }
});

// Add new registration
app.post('/api/register', (req, res) => {
    try {
        const { name, email, phone } = req.body;

        // Validation
        if (!name || !email || !phone) {
            return res.status(400).json({ 
                error: 'All fields are required' 
            });
        }

        // Read existing data
        const workbook = XLSX.readFile(excelFilePath);
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet);

        // Generate new ID
        const newId = data.length > 0 ? Math.max(...data.map(r => r.ID || 0)) + 1 : 1;

        // Create new registration
        const newRegistration = {
            ID: newId,
            Name: name,
            Email: email,
            Phone: phone,
            'Date of Registration': new Date().toLocaleString()
        };

        // Add to data
        data.push(newRegistration);

        // Convert back to worksheet
        const newWorksheet = XLSX.utils.json_to_sheet(data);
        workbook.Sheets[sheetName] = newWorksheet;

        // Write to file
        XLSX.writeFile(workbook, excelFilePath);

        console.log('✅ New registration added:', newRegistration);
        res.status(201).json({ 
            message: 'Registration successful!', 
            data: newRegistration 
        });

    } catch (error) {
        console.error('Error saving registration:', error);
        res.status(500).json({ error: 'Failed to save registration' });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Server is running on http://localhost:${PORT}`);
    console.log(`📊 Excel file location: ${excelFilePath}`);
});