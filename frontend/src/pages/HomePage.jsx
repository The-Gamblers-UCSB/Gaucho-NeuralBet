import React, { useEffect } from 'react';
import { FaTwitter, FaGithub, FaLinkedin } from 'react-icons/fa';
import { ChakraProvider, Button, useToast, Box, Text, Flex, Stack, Link } from '@chakra-ui/react';
import axios from 'axios';

function HomePage() {
  const toast = useToast(); // Initialize the toast

  // Example function to handle button click
  const handleFetchData = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/users'); // Adjust the endpoint as needed
      console.log(response.data);
      toast({
        title: "Data fetched successfully!",
        description: "Check the console for data.",
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error fetching data:', error);
      toast({
        title: "Error fetching data",
        description: error.response?.data || error.message,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    }
  };



  return (
    <ChakraProvider>
            <Flex
                direction="column"
                minHeight="100vh"
            >
                <Box as="main" flex="1" p={8}>
                    <h1>Welcome to My Website</h1>
                    <Button onClick={handleFetchData} colorScheme="orange">
                    Fetch Data
                    </Button>
                    <p>This is the main content of the page.</p>
                </Box>
            </Flex>
        </ChakraProvider>
  );
}

export default HomePage;
