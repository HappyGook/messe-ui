import { useStopwatch } from 'react-timer-hook';
import {useNavigate} from 'react-router-dom'
import "./Watches.css"
import "./../App.css"
import { useUser } from "../UserContext.jsx";
import useSound from 'use-sound';
import victorySound from '../sounds/victory.mp3';
import tickingSound from '../sounds/ticking.mp3';
import {useEffect} from "react";
import { showConfetti } from './Confetti.jsx';




function Stopwatch() {
    const { name } = useUser();
    const navigate=useNavigate()
    const [playVictory] = useSound(victorySound);
    const [playTicking, { stop: stopTicking }] = useSound(tickingSound, {
        interrupt: true,
        loop: true,
    });

    useEffect(() => {
        playTicking();
        return () => stopTicking();
    }, [playTicking, stopTicking]);

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
        stopTicking();
        playVictory();
        showConfetti();

        const time = formatTime({minutes, seconds, milliseconds});

        try {
            const response = await fetch("/api/save", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: name, time: time })
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Server error:', errorData);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Save successful:', result);

            setTimeout(() => {
                navigate("/leaderboard");
            }, 3000);

        } catch (e) {
            console.error("[FRONTEND] Problem beim speichern: ", e);
        }
    }


    return (
        <div style={{textAlign: 'center'}}>
            <h1>Notruf dings machen!</h1>
            <div className="watch" style={{fontSize:'100px'}}>
                <span>{String(minutes).padStart(2, '0')}</span>
                :<span>{String(seconds).padStart(2,'0')}</span>
                .<span>{Math.round(milliseconds/10)}</span>
            </div>
            <button className="submit-button" onClick={handleClick}><span>(Buzzer) Fertig!</span></button>
        </div>
    );
}

export default Stopwatch;