// Verbindung mit einer SQLite Datenbank
// Für unsere Leaderboard (also eine Tabelle)
// users: Name -- Zeit
// SQLite vorgeschlagen, weil embedded + simpel
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath=path.resolve(__dirname, 'db.sqlite');
const db = new sqlite3.Database(dbPath, err => {
    if(err) console.error("Problem bei Verbindung mit der Datenbank")
    else console.log("Verbunden mit der Datenbank")
});

module.exports=db;

