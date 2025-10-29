import React from 'react';
import Countdown from 'react-countdown';
import {useNavigate} from 'react-router-dom'
import "./Watches.css"

export default function CountDown(){
    const navigate=useNavigate()

    React.useEffect(()=>{
        const timer = setTimeout(()=>{
            navigate("/stopwatch")
        }, 5000)
        return ()=> clearTimeout(timer)
    }, [navigate])

    const renderer = ({ total }) => {
        const seconds = (total / 1000).toFixed(2); // two decimal digits
        return <div className="watch" style={{fontSize:'100px'}}>{seconds}</div>;
    };

    return (
        <Countdown
            date={Date.now() + 5000}
            precision={2}
            intervalDelay={0}
            renderer={renderer}
        />
    );
}