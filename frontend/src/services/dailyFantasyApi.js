// services/dailyFantasyApi.js
import axios from 'axios';

const API_URL = 'https://api.sportsgameodds.com/v1';
const API_KEY = '38c31b32b4b5af29a1834ccb6aeda8ac'; // Replace with your actual API key


export const getPlayerStats = async () => {
    const options = {
        method: 'GET',
        url: API_URL
        headers: {'X-Api-Key': API_KEY}
      };
      
      try {
        const { data } = await axios.request(options);
        console.log(data);
      } catch (error) {
        console.error(error);
      }
};
