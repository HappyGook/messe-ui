import { useUser } from "./UserContext.jsx";
import {useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";

function Confirm(){
    const {name} = useUser()
    const navigate=useNavigate()
    const [status, setStatus] = useState(false);

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch("/api/buzzer");
                const data = await res.json();
                if (data.clicked === true) {
                    setStatus(true);
                    navigate("/stopwatch");
                }
            } catch (err) {
                console.error("Status poll failed", err);
            }
        }, 500);

        return () => clearInterval(interval);
    }, [navigate]);

    // Hier wird der Buzzer die Funktion vom Starten! button übernehmen
    return(
        <div>
            <h2>{name}, bist Du bereit? Dann drucke den Buzzer zum Starten!</h2>
            <button className="submit-button" onClick={()=>navigate("/stopwatch")}><span>(Buzzer) Starten!</span></button>

            {status && <p style={{ color: "green" }}> Bereit! Starte...</p>}
        </div>
    )
}

export default Confirm