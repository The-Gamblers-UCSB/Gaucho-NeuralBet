// backend/routes/nbaRoute.js
import { Router } from 'express';
import { runPrediction } from '../api/statPrediction.js';

const router = Router();

// POST /api/nba/predict
router.post('/predict', async (req, res) => {
  try {
    const { playerName, stat } = req.body;
    if (!playerName || !stat) {
      return res.status(400).json({ success: false, error: 'Player name and stat are required' });
    }

    const result = await runPrediction(playerName, stat);
    if (!result?.success) {
      return res.status(500).json({ success: false, error: result?.error || 'Prediction failed' });
    }

    return res.json(result);
  } catch (err) {
    console.error('Predict route error:', err);
    return res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

export default router;
