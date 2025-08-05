// Verbindung mit einer SQLite Datenbank
// Für unsere Leaderboard (also eine Tabelle)
// users: Name -- Zeit
// SQLite vorgeschlagen, weil embedded + simpel
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'db.sqlite');
const db = new sqlite3.Database(dbPath, err => {
    if (err) {
        console.error("Problem bei Verbindung mit der Datenbank:", err);
        return;
    }
    console.log("Verbunden mit der Datenbank");


    db.run(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            time TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `, (err) => {
        if (err) {
            console.error("Problem bei der Tabellenerstellung:", err);
        } else {
            console.log("Users table is ready");
        }
    });
});

module.exports = db;
