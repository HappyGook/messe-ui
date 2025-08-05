const express = require('express')
const path = require('path')
const db = require('/db.cjs')

const app = express();
app.use(express.json());

// Neue Zeile in DB anlegen (user - Zeit)
app.post('/api/save',(req,res)=>{
    const {name,time}=req.body

    if(!name||!time){
        return res.status(400).json({
            error: "Name oder Zeit fehlen"
        })
    }

    const query=`INSERT INTO users (name, time) VALUES (?, ?)`
    db.run(query,[name,time],(err)=>{
        if(err){
            console.log("[BACKEND] Problem beim speichern: ", err)
            return res.status(500).json({
                error: "Problem beim speichern"
            })
        }
        res.status(200).json({
            message: "Daten gespeichert"
        })
    })
})

// Leaderboard abrufen
app.get('/api/leaderboard',(req,res)=>{
    const query=`SELECT name, time
                 FROM users
                 ORDER BY time
                 LIMIT 10`

    db.run(query,[],(err,rows)=>{
        if(err){
            console.log("[BACKEND] Problem beim Leaderboard abrufen: ", err)
            return res.status(500).json({
                error: "Problem beim abrufen"
            })
        }
        res.status(200).json(rows)
    })
})

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Something broke!'
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
