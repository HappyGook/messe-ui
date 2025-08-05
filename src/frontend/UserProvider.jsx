import { useState } from "react";
import UserContext from "./UserContext.jsx";

export function UserProvider({ children }) {
    const [name, setName] = useState("");

    return (
        <UserContext.Provider value={{ name, setName }}>
            {children}
        </UserContext.Provider>
    );
}
