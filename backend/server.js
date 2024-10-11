import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { connectDB } from './config/db.js';  
import routes from './routes/productRoute.js';  

dotenv.config(); 

const app = express();
const PORT = process.env.PORT || 5001;


app.use(cors());
app.use(express.json());


app.use('/api/users', routes);

app.listen(PORT, () => {
  connectDB();
  console.log(`Server started at http://localhost:${PORT}`);
});
