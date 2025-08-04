import React from 'react';
import { useStopwatch } from 'react-timer-hook';
import "./StopWatch.css"

function Stopwatch() {
    const {
        milliseconds,
        seconds,
        minutes,
        pause,
    } = useStopwatch({ autoStart: true, interval: 20 });


    return (
        <div style={{textAlign: 'center'}}>
            <h1>Notruf dings machen!</h1>
            <div className="stopwatch" style={{fontSize:'100px'}}>
                <span>{minutes}</span> : <span>{seconds}</span> : <span>{Math.round(milliseconds/10)}</span>
            </div>
            <button onClick={pause}>Fertig!</button>
        </div>
    );
}

export default Stopwatch;