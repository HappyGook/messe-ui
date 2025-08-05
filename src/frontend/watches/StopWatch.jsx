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

    function handleClick(){
        pause()
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