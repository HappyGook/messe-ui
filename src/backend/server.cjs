const express = require('express')
const db = require('./db.cjs')
const rc522 = require("rc522-rfid");
const SoftSPI = require("rpi-softspi");

const app = express();
app.use(express.json());

app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// Add error handler for uncaught exceptions
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

// Add error handler for unhandled rejections
process.on('unhandledRejection', (err) => {
    console.error('Unhandled Rejection:', err);
});

let lastNfcRead = { id: null, time: null };

rc522((rfidSerialNumber) => {
    lastRead = { id: rfidSerialNumber, time: new Date().toISOString() };
    console.log("Card detected:", lastRead);
});

// API endpoint to get last NFC tag
app.get('/api/nfc', (req, res) => {
    res.json(lastNfcRead);
});

// Neue Zeile in DB anlegen (user - Zeit)
app.post('/api/save', (req, res) => {
    console.log('Received save request body:', req.body);

    const { name, time } = req.body;

    if (!name || !time) {
        console.log('Missing required fields:', { name, time });
        return res.status(400).json({
            error: 'Name and time are required',
            received: { name, time }
        });
    }

    const query = `INSERT INTO users (name, time) VALUES (?, ?)`;

    db.run(query, [name, time], function(err) {
        if (err) {
            console.error("Database error:", err);
            return res.status(500).json({
                error: 'Failed to save to database',
                details: err.message
            });
        }
        res.status(201).json({
            message: 'User saved successfully',
            userId: this.lastID
        });
    });
});

// Leaderboards abrufen
app.get('/api/leaderboard', (req, res) => {
    console.log('Leaderboard request received');
    
    const query = `
        SELECT name, time
        FROM users
        WHERE datetime(created_at) >= datetime('now', '-1 hour')
        ORDER BY time
    `;

    db.all(query, [], (err, rows) => {
        if (err) {
            console.error("[BACKEND] Database error:", err);
            return res.status(500).json({
                error: "Database error",
                details: err.message
            });
        }
        
        console.log("[BACKEND] Sending leaderboard data:", rows);
        
        // Make sure we're sending a valid JSON response
        if (!rows) rows = [];
        
        res.setHeader('Content-Type', 'application/json');
        res.json(rows);
    });
});

app.get('/api/leaderAll', (req, res) => {
    console.log('Leaderboard request received');

    const query = `
        SELECT name, time
        FROM users
        ORDER BY time
    `;

    db.all(query, [], (err, rows) => {
        if (err) {
            console.error("[BACKEND] Database error:", err);
            return res.status(500).json({
                error: "Database error",
                details: err.message
            });
        }

        console.log("[BACKEND] Sending leaderboard data:", rows);

        // Make sure we're sending a valid JSON response
        if (!rows) rows = [];

        res.setHeader('Content-Type', 'application/json');
        res.json(rows);
    });
});

// Name check
app.post('/api/name',(req,res)=>{
    const name = req.body.name
    console.log('Name-check request received for name:', name);

    const query = `
        SELECT name
        FROM users
        WHERE name = ?
    `;
    db.get(query,[name],(err,row)=>{
        if(err){
            console.error("[BACKEND] Database error:", err);
            return res.status(500).json({
                error: "Database error",
                details: err.message
            });
        }
        if(!row){
            console.log("[BACKEND] Name is free!");
            res.json({success:true, message: "Verfügbar!"})
        } else {
            console.log("[BACKEND] Name ist bereits vergeben!");
            res.status(400).json({
                error: "Name ist bereits vergeben",
                details: "Name ist bereits vergeben"
            });
        }
    })
})

// Adminseite requests

// Reihen löschen
app.post('/api/delete', (req, res) => {
    console.log('[BACKEND] Received delete request body:', req.body);

    const ids = req.body;
    if (!Array.isArray(ids) || ids.length === 0) {
        console.log('[BACKEND] Invalid request: ids array is required');
        return res.status(400).json({
            error: 'Array of IDs is required',
            received: ids
        });
    }

    const placeholders = ids.map(() => '?').join(',');
    const query = `DELETE FROM users WHERE id IN (${placeholders})`;

    db.run(query, ids, function(err) {
        if (err) {
            console.error("[BACKEND] Database error:", err);
            return res.status(500).json({
                error: 'Failed to delete from database',
                details: err.message
            });
        }
        console.log(`[BACKEND] Successfully deleted ${this.changes} rows`);
        res.json({
            message: `Successfully deleted ${this.changes} rows`
        });
    });
});

// Reihen - Bearbeitung
app.post('/api/modify', (req, res) => {
    console.log('[BACKEND] Received modify request body:', req.body);

    if (!Array.isArray(req.body) || req.body.length === 0) {
        console.log('[BACKEND] Invalid request: array of rows is required');
        return res.status(400).json({
            error: 'Array of rows is required',
            received: req.body
        });
    }

    const updates = req.body.map(row => {
        return new Promise((resolve, reject) => {
            if (!row.id || !row.name || !row.time) {
                reject(new Error('Each row must contain id, name, and time'));
                return;
            }

            const query = `UPDATE users SET name = ?, time = ? WHERE id = ?`;
            db.run(query, [row.name, row.time, row.id], function(err) {
                if (err) reject(err);
                else resolve(this.changes);
            });
        });
    });

    Promise.all(updates)
        .then(results => {
            const totalUpdated = results.reduce((sum, curr) => sum + curr, 0);
            console.log(`[BACKEND] Successfully modified ${totalUpdated} rows`);
            res.json({
                message: `Successfully modified ${totalUpdated} rows`
            });
        })
        .catch(err => {
            console.error("[BACKEND] Database error:", err);
            res.status(500).json({
                error: 'Failed to modify database entries',
                details: err.message
            });
        });
});

//Reihen hinzufügen
app.post('/api/add', (req, res) => {
    console.log('[BACKEND] Received add request body:', req.body);

    if (!Array.isArray(req.body) || req.body.length === 0) {
        console.log('[BACKEND] Invalid request: array of rows is required');
        return res.status(400).json({
            error: 'Array of rows is required',
            received: req.body
        });
    }

    const insertions = req.body.map(row => {
        return new Promise((resolve, reject) => {
            if (!row.name || !row.time) {
                reject(new Error('Each row must contain name and time'));
                return;
            }

            const query = `INSERT INTO users (name, time, created_at) VALUES (?, ?, datetime('now'))`;
            db.run(query, [row.name, row.time], function(err) {
                if (err) reject(err);
                else resolve(this.lastID);
            });
        });
    });

    Promise.all(insertions)
        .then(ids => {
            console.log(`[BACKEND] Successfully added ${ids.length} rows`);
            res.status(201).json({
                message: `Successfully added ${ids.length} rows`,
                insertedIds: ids
            });
        })
        .catch(err => {
            console.error("[BACKEND] Database error:", err);
            res.status(500).json({
                error: 'Failed to add database entries',
                details: err.message
            });
        });
});

// Tabelle abrufen
app.get('/api/getall', (req, res) => {
    console.log('[BACKEND] Full table data request received');

    const query = `
        SELECT id, name, time, created_at
        FROM users
        ORDER BY id
    `;

    db.all(query, [], (err, rows) => {
        if (err) {
            console.error("[BACKEND] Database error:", err);
            return res.status(500).json({
                error: "Database error",
                details: err.message
            });
        }

        console.log("[BACKEND] Sending full table data:", rows);

        // Make sure valid JSON response
        if (!rows) rows = [];

        res.setHeader('Content-Type', 'application/json');
        res.json(rows);
    });
});




app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Something broke!'
    });
});

const PORT = process.env.PORT || 3123;
const server = app.listen(PORT, () => {
    console.log('Server is running on port 3123');
});

// Handle server errors
server.on('error', (err) => {
    console.error('Server error:', err);
});
