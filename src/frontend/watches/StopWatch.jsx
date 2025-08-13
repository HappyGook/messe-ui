import React from 'react';
import { useStopwatch } from 'react-timer-hook';
import {useNavigate} from 'react-router-dom'
import "./Watches.css"
import "./../App.css"
import { useUser } from "../UserContext.jsx";


function Stopwatch() {
    const { name } = useUser();
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
        pause();
        const time = formatTime({minutes, seconds, milliseconds});

        // Debug log
        console.log('Sending data:', { name, time });

        try {
            const response = await fetch("/api/save", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: name, time: time })
            });

            // Debug log
            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Server error:', errorData);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Save successful:', result);
            navigate("/leaderboard");
        } catch (e) {
            console.error("[FRONTEND] Problem beim speichern: ", e);
        }
    }


    return (
        <div style={{textAlign: 'center'}}>
            <h1>Notruf dings machen!</h1>
            <div className="watch" style={{fontSize:'100px'}}>
                <span>{minutes}</span> : <span>{seconds}</span> . <span>{Math.round(milliseconds/10)}</span>
            </div>
            <button className="submit-button" onClick={handleClick}><span>(Buzzer) Fertig!</span></button>
        </div>
    );
}

export default Stopwatch;