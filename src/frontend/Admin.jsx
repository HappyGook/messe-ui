import React, { useState, useEffect } from 'react';
import './App.css';

const Admin = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState('');
    const [tableData, setTableData] = useState([]);
    const [error, setError] = useState('');
    const [selectedRows, setSelectedRows] = useState(new Set());
    const [editingCell, setEditingCell] = useState(null);
    const [editValue, setEditValue] = useState('');
    const [originalData, setOriginalData] = useState({});
    const [activeTable, setActiveTable] = useState('users'); // "users" or "all_scores"

    const correctPassword = "admin123"; // TODO: secure later

    // Automatically reload data when switching tables
    useEffect(() => {
        if (isAuthenticated) {
            fetchTableData();
        }
    }, [activeTable]);

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
        const url = activeTable === 'users' ? '/api/getall' : '/api/leaderAll';
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch data');
            const data = await response.json();
            setTableData(data);

            const origData = {};
            data.forEach(row => {
                origData[row.id] = { ...row };
            });
            setOriginalData(origData);
        } catch (error) {
            setError('Error fetching data: ' + error.message);
        }
    };

    const handleCheckboxChange = (id) => {
        const newSelected = new Set(selectedRows);
        if (newSelected.has(id)) newSelected.delete(id);
        else newSelected.add(id);
        setSelectedRows(newSelected);
    };

    const handleDelete = async () => {
        if (selectedRows.size === 0) return;
        const endpoint = activeTable === 'users' ? '/api/delete' : '/api/deleteAll';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(Array.from(selectedRows))
            });

            if (!response.ok) throw new Error('Failed to delete rows');
            fetchTableData();
            setSelectedRows(new Set());
        } catch (error) {
            setError('Error deleting rows: ' + error.message);
        }
    };

    const startEditing = (id, field, value) => {
        setEditingCell({ id, field });
        setEditValue(value);
    };

    const handleCellChange = async (id, field) => {
        if (editValue === originalData[id][field]) {
            setEditingCell(null);
            return;
        }

        const endpoint = activeTable === 'users' ? '/api/modify' : '/api/modifyAll';

        try {
            const updatedRow = {
                ...originalData[id],
                [field]: editValue
            };

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify([updatedRow])
            });

            if (!response.ok) throw new Error('Failed to update row');

            setTableData(tableData.map(row =>
                row.id === id ? { ...row, [field]: editValue } : row
            ));
            setOriginalData({
                ...originalData,
                [id]: { ...originalData[id], [field]: editValue }
            });
        } catch (error) {
            setError('Error updating row: ' + error.message);
            setTableData(tableData.map(row =>
                row.id === id ? { ...originalData[id] } : row
            ));
        }
        setEditingCell(null);
    };

    const handleKeyPress = (e, id, field) => {
        if (e.key === 'Enter') handleCellChange(id, field);
        else if (e.key === 'Escape') {
            setEditingCell(null);
            setEditValue(originalData[id][field]);
        }
    };

    // UI for password login
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

    // UI for admin panel
    return (
        <div className="admin-panel">
            <h2>Admin Panel</h2>
            {error && <p className="error-message">{error}</p>}

            <div className="table-switcher">
                <button
                    className={activeTable === 'users' ? 'active' : ''}
                    onClick={() => setActiveTable('users')}
                >
                    Users Table
                </button>
                <button
                    className={activeTable === 'all_scores' ? 'active' : ''}
                    onClick={() => setActiveTable('all_scores')}
                >
                    All Scores Table
                </button>
            </div>

            <div className="table-container">
                <table>
                    <thead>
                    <tr>
                        <th>Select</th>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Time</th>
                        <th>Created At</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tableData.map((row) => (
                        <tr key={row.id}>
                            <td>
                                <input
                                    type="checkbox"
                                    checked={selectedRows.has(row.id)}
                                    onChange={() => handleCheckboxChange(row.id)}
                                />
                            </td>
                            <td>{row.id}</td>
                            <td onClick={() => startEditing(row.id, 'name', row.name)}>
                                {editingCell?.id === row.id && editingCell?.field === 'name' ? (
                                    <input
                                        type="text"
                                        value={editValue}
                                        onChange={(e) => setEditValue(e.target.value)}
                                        onBlur={() => handleCellChange(row.id, 'name')}
                                        onKeyDown={(e) => handleKeyPress(e, row.id, 'name')}
                                        autoFocus
                                    />
                                ) : (
                                    row.name
                                )}
                            </td>
                            <td onClick={() => startEditing(row.id, 'time', row.time)}>
                                {editingCell?.id === row.id && editingCell?.field === 'time' ? (
                                    <input
                                        type="text"
                                        value={editValue}
                                        onChange={(e) => setEditValue(e.target.value)}
                                        onBlur={() => handleCellChange(row.id, 'time')}
                                        onKeyDown={(e) => handleKeyPress(e, row.id, 'time')}
                                        autoFocus
                                    />
                                ) : (
                                    row.time
                                )}
                            </td>
                            <td>{row.created_at}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>

            <div className="admin-controls">
                <button
                    onClick={handleDelete}
                    disabled={selectedRows.size === 0}
                >
                    Delete Selected
                </button>
            </div>
        </div>
    );
};

export default Admin;
