// backend/services/statsPrediction.js
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

// Adjust these if your structure differs
const projectRoot = path.join(__dirname, '..');                   // /backend
const pythonScriptPath = path.join(projectRoot, 'nba_prediction_api.py');

// Try different Python commands for Railway deployment
const getPythonPath = () => {
  if (process.env.NODE_ENV === 'production') {
    // Try different Python commands for Railway - use 'python' instead of 'python3'
    return 'python';
  }
  return path.join(projectRoot, '..', 'venv', 'bin', 'python');
};

export function runPrediction(playerName, stat) {
  return new Promise((resolve) => {
    const pythonPath = getPythonPath();
    console.log('Using Python path:', pythonPath);
    console.log('Script path:', pythonScriptPath);
    console.log('Working directory:', projectRoot);
    
    const child = spawn(pythonPath, [pythonScriptPath, playerName, stat], {
      cwd: projectRoot,            // run inside /backend so CSVs are found
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));

    child.on('close', (code) => {
      console.log('Python process exited with code:', code);
      console.log('stdout:', stdout);
      console.log('stderr:', stderr);
      
      if (code !== 0) {
        console.error('Python error:', stderr || stdout);
        return resolve({ success: false, error: 'Python script execution failed' });
      }

      try {
        // find the JSON line (your script prints exactly one JSON object)
        const lines = stdout.trim().split('\n').map(l => l.trim());
        const lastJson = lines.reverse().find((l) => l.startsWith('{') && l.endsWith('}'));
        if (!lastJson) throw new Error('No JSON in output');

        const parsed = JSON.parse(lastJson);
        return resolve(parsed);
      } catch (e) {
        console.error('Parse error:', e, '\nRaw stdout:', stdout);
        return resolve({ success: false, error: 'Failed to parse prediction result' });
      }
    });

    child.on('error', (err) => {
      console.error('Spawn error:', err);
      return resolve({ success: false, error: 'Failed to start Python process' });
    });
  });
}
