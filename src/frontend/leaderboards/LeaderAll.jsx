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
            const response = await fetch('/api/leaderAll', {
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

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    const displayedLeaders = showAll ? leaders : leaders.slice(0, initialDisplayCount);

    return (
        <div>
            <div className="leaderboard">
                <h2>Vollständiges Leaderboard</h2>
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
                            <button
                                onClick={() => setShowAll(!showAll)}
                            >
                                <span>
                                    {showAll ? 'Top 7 zeigen' : 'Alle zeigen'}
                                </span>
                            </button>
                        )}
                        <div>
                            <button onClick={()=>navigate("/leaderboard")}>
                                <span> Leaderboard der letzten Stunde </span>
                            </button>
                        </div>

                    </>

                )}
            </div>
            <button className="submit-button" onClick={() => { setName(""); navigate("/"); }}>
                <span> Nochmal Spielen </span>
            </button>

        </div>

    );
}

export default LeaderBoard;