import {useNavigate} from 'react-router-dom'
import {useUser} from "./UserContext.jsx";
import {useState} from "react";
import { useIdleTimer } from "./useIdleTimer.jsx";



export default function NameInput(){
    useIdleTimer()
    const {name, setName}=useUser()
    const [error, setError] = useState(null);
    const navigate=useNavigate()


    const handleSubmit = (event) => {
        event.preventDefault();
        let len=name.length;
        if(len>13){
            setError("Eingabe ist zu lang!")
        }else if(!len){
            setError("Eingabe ist leer!")
        }else{
            try{
                fetch("/api/name", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({name: name})
                }).then(response=>{
                    if (response.ok) {
                        navigate("/confirm");
                    } else {
                        return response.json().then(data => {
                            setError(data.error || "Name ist bereits vergeben");
                        });
                    }
                }).catch(err => {
                    console.error("Problem beim Namen-Check", err);
                    setError("Ein Fehler ist aufgetreten");
                });
            } catch (err) {
                console.log("Problem beim Namen-Check",err)
            }
        }

    }

    const handleChange=(e)=>{
        setError("")
        setName(e.target.value)
    }



    return(
        <div>
            <form onSubmit={handleSubmit}>
                <h2>Gib Dein Nickname ein!</h2>
                <p>
                    Maximal 13 Zeichen!

                </p>
                <div>
                    {error}
                </div>
                <input
                    type="text"
                    value={name}
                    onChange={handleChange}
                />
                <div>
                    <button className="submit-button"><span>Eingeben</span></button>
                </div>
            </form>
        </div>
    )
}