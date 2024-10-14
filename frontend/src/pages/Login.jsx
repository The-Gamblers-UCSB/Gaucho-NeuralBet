import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Box, Button, FormControl, FormLabel, Input, Heading, Stack, useToast } from '@chakra-ui/react';

function Login() {
  console.log("Hello");
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const navigate = useNavigate();
  const toast = useToast();  

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { email, password } = formData;

    try {
      const response = await axios.post('http://localhost:5001/api/users/login', { email, password });
      console.log('User logged in successfully!', response.data);
      toast({
        title: "Login successful.",
        description: "You are now logged in.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
      
    } catch (error) {
      console.error('Error during login:', error.response?.data || error.message);
      toast({
        title: "Login failed.",
        description: error.response?.data || error.message,
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
      <Box
        bg="white"
        p={8}
        rounded="lg"
        shadow="lg"
        maxW="md"
        w="full"
      >
        <Heading as="h2" size="lg" textAlign="center" mb={6} color="blue.600">
          Welcome Back
        </Heading>
        <form onSubmit={handleSubmit}>
          <Stack spacing={4}>
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
              Login
            </Button>
          </Stack>
        </form>
      </Box>
    </Box>
  );
}

export default Login;
