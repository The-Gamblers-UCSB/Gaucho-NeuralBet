import React, { useEffect } from 'react';
import { Button, useToast } from '@chakra-ui/react';
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
    <div>
      <h1>Welcome to the Home Page</h1>
      <Button onClick={handleFetchData} colorScheme="blue">
        Fetch Data
      </Button>
    </div>
  );
}

export default HomePage;
