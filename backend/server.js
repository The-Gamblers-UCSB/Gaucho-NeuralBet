// backend/server.js
import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import routes from "./routes/productRoute.js"; // <— your existing product/user routes
import nbaRouter from "./routes/nbaRoute.js"; // <— new NBA prediction routes
import { connectDB } from "./config/db.js"; // <— import database connection

dotenv.config();

// Debug environment
console.log("NODE_ENV:", process.env.NODE_ENV);
console.log("PORT:", process.env.PORT);
console.log("Python available:", process.platform);

const app = express();
const PORT = process.env.PORT || 5001;

// Connect to database
connectDB();

// middleware
app.use(express.json());
app.use(
	cors({
		origin: [
			"http://localhost:5173",
			"http://localhost:5174",
			"http://localhost:3000",
			"https://gaucho-neural-bet-pzwa-4aympv0fu-kalyans-projects-8f049e38.vercel.app",
		],
		credentials: true,
		methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
		allowedHeaders: ["Content-Type", "Authorization"],
	})
);

// routes
app.use("/api/users", routes); // your original set
app.use("/api/nba", nbaRouter); // prediction lives here

// health
app.get("/api/health", (_req, res) => {
	res.json({
		status: "healthy",
		service: "NBA + Users API",
		ts: new Date().toISOString(),
	});
});

// start
app.listen(PORT, () => {
	console.log(`Server started at port ${PORT}`);
});
