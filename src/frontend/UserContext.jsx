import { createContext, useContext } from "react";


const UserContext = createContext();


export function useUser() {
    return useContext(UserContext);
}

export default UserContext;
