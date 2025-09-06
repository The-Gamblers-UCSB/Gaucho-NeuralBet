import mongoose from "mongoose";
import dotenv from "dotenv";

dotenv.config();
dotenv.config({ path: "../.env" });

export const connectDB = async () => {
	try {
		// Check if MONGO_URI is defined
		if (!process.env.MONGO_URI) {
			console.error("MONGO_URI environment variable is not defined");
			process.exit(1);
		}

		console.log("Attempting to connect to MongoDB...");
		const conn = await mongoose.connect(process.env.MONGO_URI, {
			// Add connection options for better reliability
			maxPoolSize: 10,
			serverSelectionTimeoutMS: 5000,
			socketTimeoutMS: 45000,
		});
		console.log(`MongoDB Connected: ${conn.connection.host}`);
	} catch (error) {
		console.error("Database connection error:", error.message);
		process.exit(1);
	}
};
