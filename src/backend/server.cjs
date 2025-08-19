const express = require('express')
const db = require('./db.cjs')

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

// Leaderboard abrufen
app.get('/api/leaderboard', (req, res) => {
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
