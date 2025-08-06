import { useState, useEffect } from 'react';
import './App.css';

function LeaderBoard() {
    const [leaders, setLeaders] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

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
        <div className="leaderboard">
            <h2>Leaderboard</h2>
            {leaders.length === 0 ? (
                <p>No records yet!</p>
            ) : (
                <table>
                    <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Name</th>
                        <th>Time</th>
                    </tr>
                    </thead>
                    <tbody>
                    {leaders.map((leader, index) => (
                        <tr key={index}>
                            <td>{index + 1}</td>
                            <td>{leader.name}</td>
                            <td>{leader.time}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default LeaderBoard;