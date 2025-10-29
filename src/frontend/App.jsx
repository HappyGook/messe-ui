import schnoorLogo from '../assets/schnoor.svg'
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import {UserProvider} from "./UserProvider.jsx";
import './App.css'
import NameInput from "./NameInput.jsx";
import Confirm from "./Confirm.jsx";
import StopWatch from "./watches/StopWatch.jsx";
import CountDown from "./watches/CountDown.jsx";
import LeaderBoard from "./leaderboards/LeaderBoard.jsx";
import LeaderAll from "./leaderboards/LeaderAll.jsx";
import Admin from "./Admin.jsx";
import anglePic from "../assets/angle.png";

function App() {

    return (
    <>
        <img src={anglePic} alt="Corner Decoration" className="angle-image" />

      <div>
          <img src={schnoorLogo} className="logo schnoor" alt="Schnoor Logo"></img>
      </div>

      <UserProvider>
          <BrowserRouter>
              <Routes>
                  <Route path="/" element={<NameInput />}/>
                  <Route path="/confirm" element={<Confirm />}/>
                  <Route path="/stopwatch" element={<StopWatch />}/>
                  <Route path="/countdown" element={<CountDown />}/>
                  <Route path="/leaderboard" element={<LeaderBoard />}/>
                  <Route path="/leaderAll" element={<LeaderAll />}/>
                  <Route path="/admin" element={<Admin />}/>
              </Routes>
          </BrowserRouter>
      </UserProvider>
    </>
  )
}

export default App
