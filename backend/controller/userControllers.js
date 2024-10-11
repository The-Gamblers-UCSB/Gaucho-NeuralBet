import User from '../models/userModel.js'; 
import bcrypt from 'bcryptjs';  

export const registerUser = async (req, res) => {
  try {
    const { name, email, password } = req.body;  
    const userExists = await User.findOne({ email });
    if (userExists) {
      return res.status(400).json({ message: 'User already exists' });
    }

    
    const newUser = new User({
      name,
      email,
      password,  
    });

    await newUser.save(); 

   
    res.status(201).json({ message: 'User registered successfully', user: newUser });
  } catch (error) {
   
    res.status(500).json({ message: 'Server error', error });
  }
};


export const loginUser = async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

   
    const isPasswordCorrect = await bcrypt.compare(password, user.password);
    if (!isPasswordCorrect) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

   
    res.status(200).json({ message: 'Login successful', user: user.name });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error });
  }
}
 
