import {createContext, useContext, useState} from "react"

const UserContext=createContext()

export function UserProvider({children}) {
    const [name, setName] = useState("")
    return(
        <UserContext.Provider value={{name, setName}}>
            {children}
        </UserContext.Provider>
    )
}

export function useUser(){
    return useContext(UserContext)
}