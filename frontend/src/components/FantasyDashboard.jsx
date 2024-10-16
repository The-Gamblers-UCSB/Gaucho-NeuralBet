import React, { useEffect, useState } from 'react';
import { getPlayerStats } from '../services/dailyFantasyApi';  // Adjust path if needed

const FantasyDashboard = () => {
    const [playerStats, setPlayerStats] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getPlayerStats();
                if (data && data.players) {
                    setPlayerStats(data.players);
                } else {
                    setPlayerStats([]);
                }
            } catch (err) {
                setError('Failed to fetch player stats.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <div>
            <h1>Daily Fantasy Player Stats</h1>
            {isLoading ? (
                <p>Loading player stats...</p>
            ) : error ? (
                <p>{error}</p>
            ) : playerStats.length > 0 ? (
                <ul>
                    {playerStats.map(player => (
                        <li key={player.id}>
                            <strong>{player.name}</strong>: {player.points} points
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No player stats available.</p>
            )}
        </div>
    );
};

export default FantasyDashboard;
