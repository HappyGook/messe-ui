import React from 'react';
import { useStopwatch } from 'react-timer-hook';
import {useNavigate} from 'react-router-dom'
import "./Watches.css"

function Stopwatch() {
    const navigate=useNavigate()
    const {
        milliseconds,
        seconds,
        minutes,
        pause,
    } = useStopwatch({ autoStart: true, interval: 20 });


    function formatTime({minutes, seconds, milliseconds}){
        const pad = (num, size=2) => String(num).padStart(size, '0');
        const ms = String(milliseconds).padStart(3, '0');
        return `00:${pad(minutes)}:${pad(seconds)}.${ms}`
    }

    // Name und Zeit nach Backend schicken, wenn der Benutzer fertig ist
    async function handleClick() {
        pause()
        const time = formatTime({minutes, seconds, milliseconds})
        try {
            await fetch("/api/save", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({name: name, time:time})
            })
        } catch (e) {
            console.log("[FRONTEND] Problem beim speichern: ", e)
        }
        navigate("/leaderboard")
    }

    return (
        <div style={{textAlign: 'center'}}>
            <h1>Notruf dings machen!</h1>
            <div className="watch" style={{fontSize:'100px'}}>
                <span>{minutes}</span> : <span>{seconds}</span> : <span>{Math.round(milliseconds/10)}</span>
            </div>
            <button className="submit-button" onClick={handleClick}><span>(Buzzer) Fertig!</span></button>
        </div>
    );
}

export default Stopwatch;