import {useNavigate} from 'react-router-dom'
import {useUser} from "./UserContext.jsx";
import {useState} from "react";




export default function NameInput(){

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
            navigate("/confirm")
        }

    }

    const handleChange=(e)=>{
        setError("")
        setName(e.target.value)
    }



    return(
        <div>
            <form onSubmit={handleSubmit}>
                <h2>Geben Sie ihr Nickname ein!</h2>
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