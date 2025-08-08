import { useState, useEffect } from 'react';
import './LeaderBoard.css';
import './App.css'
import {useNavigate} from 'react-router-dom'

function LeaderBoard() {
    const [leaders, setLeaders] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate=useNavigate()

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

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <div className="leaderboard">
                <h2>Leaderboard</h2>
                {leaders.length === 0 ? (
                    <p>No records yet!</p>
                ) : (
                    <table className="leader-table">
                        <thead>
                        </thead>
                        <tbody>
                        {leaders.map((leader, index) => (
                            <tr
                                key={index}
                                className={index === 0 ? 'top-leader' : 'leader'}
                            >
                                <td>{index + 1}</td>
                                <td>{leader.name}</td>
                                <td>{leader.time.substring(3)}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                )}
            </div>
            <button className="submit-button" onClick={() => navigate("/")}> <span> Nochmal Spielen </span> </button>
        </div>

    );
}

export default LeaderBoard;