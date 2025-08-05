import reactLogo from '../assets/react.svg'
import schnoorLogo from '../assets/schnoor.svg'
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import {UserProvider} from "./UserProvider.jsx";
import './App.css'
import NameInput from "./NameInput.jsx";
import Confirm from "./Confirm.jsx";
import StopWatch from "./watches/StopWatch.jsx";
import CountDown from "./watches/CountDown.jsx";

function App() {

  return (
    <>
      <div>
        <a href="https://www.youtube.com/watch?v=xvFZjo5PgG0#ddg-play" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
          <img src={schnoorLogo} className="logo schnoor" alt="Schnoor Logo"></img>
      </div>

      <UserProvider>
          <BrowserRouter>
              <Routes>
                  <Route path="/" element={<NameInput />}/>
                  <Route path="/confirm" element={<Confirm />}/>
                  <Route path="/stopwatch" element={<StopWatch />}/>
                  <Route path="/countdown" element={<CountDown />}/>
              </Routes>
          </BrowserRouter>
      </UserProvider>
    </>
  )
}

export default App
