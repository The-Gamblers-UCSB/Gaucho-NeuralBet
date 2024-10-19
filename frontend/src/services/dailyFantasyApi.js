// services/dailyFantasyApi.js
import axios from 'axios';

const API_URL = 'https://api.dailyfantasyapi.io';
const API_KEY = '307de419-aabf-40e5-a6e9-9a0977df375d'; // Replace with your actual API key

// Example function to get player stats
export const getPlayerStats = async () => {
    try {
        const response = await axios.get(`${API_URL}/player-stats`, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching player stats:', error);
        return null;
    }
};
