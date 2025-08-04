import { useUser } from "./UserContext.jsx";
import {useNavigate} from "react-router-dom";

function Confirm(){
    const {name} = useUser()
    const navigate=useNavigate()

    // Hier wird der Buzzer die Funktion vom Starten! button übernehmen
    return(
        <div>
            <h2>Willst du mit dem Nickname {name} starten?</h2>
            <button className="submit-button" onClick={()=>navigate("/stopwatch")}><span>Starten!</span></button>
            <button className="edit-button" onClick={()=>navigate("/")}><span>Nickname Bearbeiten</span></button>
        </div>
    )
}

export default Confirm