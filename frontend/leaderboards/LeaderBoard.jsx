import { useState, useEffect } from 'react';
import './LeaderBoard.css';
import '../App.css'
import {useNavigate} from 'react-router-dom'
import { useUser } from "../UserContext.jsx";  // <-- import context


function LeaderBoard() {
    const [leaders, setLeaders] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAll, setShowAll] = useState(false);
    const navigate = useNavigate();
    const initialDisplayCount = 7;
    const { setName } = useUser();

    useEffect(() => {
        fetchLeaders();
    }, []);

    const fetchLeaders = async () => {
    try {
        console.log('Starting leaderboard fetch');
        const response = await fetch('/api/leaderboard', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers));
        
        const responseText = await response.text();
        console.log('Raw response:', responseText);
        
        if (!responseText) {
            console.log('Empty response received');
            setLeaders([]);
            return;
        }
        
        try {
            const data = JSON.parse(responseText);
            console.log('Parsed data:', data);
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            setLeaders(Array.isArray(data) ? data : []);
        } catch (e) {
            console.error('JSON parse error:', e);
            setError('Invalid server response format');
        }
    } catch (err) {
        console.error('Fetch error:', err);
        setError(`Failed to fetch leaderboard data: ${err.message}`);
    } finally {
        setLoading(false);
    }
};

    const handleReset = async () => {
        if (!window.confirm("Alle aktuellen User in All Scores verschieben und löschen?")) return;

        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            console.log("Reset result:", data);
            // Refresh leaderboard after reset
            fetchLeaders();
        } catch (err) {
            console.error("Reset failed:", err);
            setError(`Reset failed: ${err.message}`);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    const displayedLeaders = showAll ? leaders : leaders.slice(0, initialDisplayCount);

    return (
        <div>
            <div style={{ position: 'relative', paddingTop: '40px' }}>
                {/* Reset button top-left */}
                <button
                    onClick={handleReset}
                    style={{
                        position: 'absolute',
                        top: '0',
                        left: '0',
                        backgroundColor: 'red',
                        color: 'white',
                        border: 'none',
                        padding: '5px 10px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        zIndex: 10
                    }}
                >
                    Reset
                </button>
        </div>
            <div className="leaderboard">
                <h2>Leaderboard der letzten Stunde</h2>
                {leaders.length === 0 ? (
                    <p>No records yet!</p>
                ) : (
                    <>
                        <table className="leader-table">
                            <thead>
                            </thead>
                            <tbody>
                            {displayedLeaders.map((leader, index) => (
                                <tr
                                    key={index}
                                    className={
                                        {
                                            0: "first-leader",
                                            1: "second-leader",
                                            2: "third-leader"
                                        }[index] || "leader"
                                    }
                                >
                                    <td>{index + 1}</td>
                                    <td>{leader.name}</td>
                                    <td>{leader.time.substring(3)}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                        {leaders.length > initialDisplayCount && (
                            <button className="transfer-button"
                                onClick={() => setShowAll(!showAll)}
                            >
                                <span>
                                    {showAll ? 'Top 7 zeigen' : 'Alle zeigen'}
                                </span>
                            </button>

                        )}

                    </>
                )}
                <div>
                    <button className="transfer-button" onClick={()=>navigate("/leaderAll")}>
                        <span> Komplettes Leaderboard (alle Stunden)</span>
                    </button>
                </div>
            </div>
            <button className="submit-button" onClick={() => { setName(""); navigate("/"); }}>
                <span> Nochmal Spielen </span>
            </button>

        </div>

    );
}

export default LeaderBoard;