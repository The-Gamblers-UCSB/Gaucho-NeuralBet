import User from "../models/userModel.js";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";

export const registerUser = async (req, res) => {
	try {
		const { name, email, password } = req.body;

		// Check if user already exists
		const userExists = await User.findOne({ email });
		if (userExists) {
			return res.status(400).json({ message: "User already exists" });
		}

		// Hash the password
		const saltRounds = 10;
		const hashedPassword = await bcrypt.hash(password, saltRounds);

		// Create new user with hashed password
		const newUser = new User({
			name,
			email,
			password: hashedPassword,
		});

		await newUser.save();

		// Generate JWT token
		const token = jwt.sign(
			{ userId: newUser._id, email: newUser.email },
			process.env.JWT_SECRET || "your-secret-key",
			{ expiresIn: "7d" }
		);

		// Return user data without password and include token
		res.status(201).json({
			message: "User registered successfully",
			user: {
				id: newUser._id,
				name: newUser.name,
				email: newUser.email,
			},
			token,
		});
	} catch (error) {
		console.error("Registration error:", error);
		res.status(500).json({ message: "Server error", error: error.message });
	}
};

export const loginUser = async (req, res) => {
	const { email, password } = req.body;

	try {
		// Find user by email
		const user = await User.findOne({ email });
		if (!user) {
			return res.status(404).json({ message: "User not found" });
		}

		// Compare password with hashed password
		const isPasswordCorrect = await bcrypt.compare(password, user.password);
		if (!isPasswordCorrect) {
			return res.status(400).json({ message: "Invalid credentials" });
		}

		// Generate JWT token
		const token = jwt.sign(
			{ userId: user._id, email: user.email },
			process.env.JWT_SECRET || "your-secret-key",
			{ expiresIn: "7d" }
		);

		// Return user data without password and include token
		res.status(200).json({
			message: "Login successful",
			user: {
				id: user._id,
				name: user.name,
				email: user.email,
			},
			token,
		});
	} catch (error) {
		console.error("Login error:", error);
		res.status(500).json({ message: "Server error", error: error.message });
	}
};
