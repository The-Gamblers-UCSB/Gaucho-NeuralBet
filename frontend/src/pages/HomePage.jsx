import React, { useEffect } from 'react';
import { ChakraProvider, Button, useToast, Box, Flex } from '@chakra-ui/react';

import axios from 'axios';

function HomePage() {
  const toast = useToast(); // Initialize the toast

  // Example function to handle button click
  const handleFetchData = async () => {
    let nextCursor = null;
    let eventData = [];
    do {
      try {
        const response = await axios.get('/v1/events', {
          params: {
            leagueID: 'NBA',
            startsAfter: '2025-01-07',
            startsBefore: '2025-01-07',
            limit: 50,
            marketOddsAvailable: true,
            cursor: nextCursor
          }
        });
    
        // response.data will contain the 30 events for this request
        const data = response.data;
    
        eventData = eventData.concat(data.events);
    
        nextCursor = data?.nextCursor;
    
      } catch (error) {
        console.error('Error fetching events:', error);
        break;
      }
    } while (nextCursor);
    
    // Once you have this data, you could feed it to your betting model, display it in your sportsbook application, etc.
    events.forEach((event) => {
      const odds = event.odds;
      Object.values(odds).forEach((oddObject) => {
        console.log(`Odd ID: ${oddObject.oddID}`);
        console.log(`Odd Value: ${oddObject.closeOdds}`);
      });
    });

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
