import React from 'react';
import { Box, Heading } from '@chakra-ui/react';

const NotFound = () => {
    return (
        <Box
              bg="gray.800"
              minH="100vh"
              display="flex"
              alignItems="center"
              justifyContent="center"
              p={6}
              
        >
            <Heading as="h2" size="lg" textAlign="center" mb={6} color="teal.200">
                404 - Page Not Found
            </Heading>
        </Box>

    );
};

export default NotFound;
