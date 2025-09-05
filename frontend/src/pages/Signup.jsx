import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import {
	Box,
	Button,
	FormControl,
	FormLabel,
	Input,
	Heading,
	Stack,
	useToast,
} from "@chakra-ui/react";

function Signup() {
	const [formData, setFormData] = useState({
		name: "",
		email: "",
		password: "",
	});

	const navigate = useNavigate();
	const toast = useToast(); // For success and error messages

	const handleChange = (e) => {
		setFormData({
			...formData,
			[e.target.name]: e.target.value,
		});
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		const { name, email, password } = formData;

		try {
			const response = await axios.post(
				"https://gaucho-neuralbet-production.up.railway.app/api/users/register",
				{ name, email, password }
			);
			console.log("User registered successfully!", response.data);

			// Store token in localStorage if provided
			if (response.data.token) {
				localStorage.setItem("token", response.data.token);
				localStorage.setItem(
					"user",
					JSON.stringify(response.data.user)
				);
			}

			toast({
				title: "Registration successful!",
				description: "You can now log in.",
				status: "success",
				duration: 5000,
				isClosable: true,
			});
			navigate("/login"); // Navigate to login page after successful registration
		} catch (error) {
			console.error(
				"Error during registration:",
				error.response?.data || error.message
			);
			toast({
				title: "Registration failed",
				description:
					error.response?.data?.message ||
					error.message ||
					"An error occurred during registration",
				status: "error",
				duration: 5000,
				isClosable: true,
			});
		}
	};

	return (
		<Box
			bg="gray.800"
			minH="100vh"
			display="flex"
			alignItems="center"
			justifyContent="center"
			p={6}
		>
			<Box bg="white" p={8} rounded="lg" shadow="lg" maxW="md" w="full">
				<Heading
					as="h2"
					size="lg"
					textAlign="center"
					mb={6}
					color="blue.600"
				>
					Create an Account
				</Heading>
				<form onSubmit={handleSubmit}>
					<Stack spacing={4}>
						<FormControl id="name" isRequired>
							<FormLabel>Name</FormLabel>
							<Input
								type="text"
								name="name"
								value={formData.name}
								onChange={handleChange}
								placeholder="Enter your name"
								bg="gray.100"
							/>
						</FormControl>

						<FormControl id="email" isRequired>
							<FormLabel>Email</FormLabel>
							<Input
								type="email"
								name="email"
								value={formData.email}
								onChange={handleChange}
								placeholder="Enter your email"
								bg="gray.100"
							/>
						</FormControl>

						<FormControl id="password" isRequired>
							<FormLabel>Password</FormLabel>
							<Input
								type="password"
								name="password"
								value={formData.password}
								onChange={handleChange}
								placeholder="Enter your password"
								bg="gray.100"
							/>
						</FormControl>

						<Button
							type="submit"
							colorScheme="blue"
							size="lg"
							w="full"
						>
							Sign Up
						</Button>
					</Stack>
				</form>

				<Box textAlign="center" mt={6}>
					<Button
						variant="outline"
						colorScheme="blue"
						size="lg"
						onClick={() => navigate("/login")}
					>
						Already Have an Account? Login
					</Button>
				</Box>
			</Box>
		</Box>
	);
}

export default Signup;
