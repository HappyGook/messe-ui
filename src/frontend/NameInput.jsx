import {useNavigate} from 'react-router-dom'
import {useUser} from "./UserContext.jsx";




export default function NameInput(){

    const {name, setName}=useUser()
    const navigate=useNavigate()


    const handleSubmit = (event) => {
        event.preventDefault();
        if(name && name.length<14){
            navigate("/confirm")
        } else{
            alert("Engabe ist leer")
        }
    }

    const handleChange=(e)=>{
        setName(e.target.value)
    }



    return(
        <div>
            <form onSubmit={handleSubmit}>
                <h2>Geben Sie ihr Nickname ein!</h2>
                <p>
                    Maximal 13 Zeichen!
                </p>
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