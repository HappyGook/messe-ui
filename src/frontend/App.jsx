import { useState } from 'react'
import reactLogo from '../assets/react.svg'
import schnoorLogo from '../assets/schnoor.svg'
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import {UserProvider} from "./UserContext.jsx";
import './App.css'
import NameInput from "./NameInput.jsx";
import Confirm from "./Confirm.jsx";

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
          <img src={schnoorLogo} className="logo schnoor" alt="Schnoor Logo"></img>
      </div>

      <UserProvider>
          <BrowserRouter>
              <Routes>
                  <Route path="/" element={<NameInput />}/>
                  <Route path="/confirm" element={<Confirm />}/>
              </Routes>
          </BrowserRouter>
      </UserProvider>
    </>
  )
}

export default App
