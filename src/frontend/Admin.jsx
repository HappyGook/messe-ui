import React, { useState } from 'react';
import './App.css';

const Admin = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState('');
    const [tableData, setTableData] = useState([]);
    const [error, setError] = useState('');

    const correctPassword = "admin123"; // Sollte noch sicherer behandelt werden XD

    const handlePasswordSubmit = (e) => {
        e.preventDefault();
        if (password === correctPassword) {
            setIsAuthenticated(true);
            fetchTableData();
        } else {
            setError('Incorrect password');
        }
    };

    const fetchTableData = async () => {
        try {
            const response = await fetch('/api/getall');
            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }
            const data = await response.json();
            setTableData(data);
        } catch (error) {
            setError('Error fetching data: ' + error.message);
        }
    };

    if (!isAuthenticated) {
        return (
            <div className="admin-login">
                <h2>Admin Access</h2>
                <form onSubmit={handlePasswordSubmit}>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter password"
                        className="password-input"
                    />
                    <button type="submit" className="submit-button">
                        Login
                    </button>
                </form>
                {error && <p className="error-message">{error}</p>}
            </div>
        );
    }

    return (
        <div className="admin-panel">
            <h2>Admin Panel</h2>
            <div className="table-container">
                <table>
                    <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Time</th>
                        <th>Created At</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tableData.map((row) => (
                        <tr key={row.id}>
                            <td>{row.id}</td>
                            <td>{row.name}</td>
                            <td>{row.time}</td>
                            <td>{row.created_at}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Admin;