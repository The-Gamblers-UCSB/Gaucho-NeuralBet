import { Box, Text, Flex, Stack, Link } from '@chakra-ui/react';
import React from 'react';

const Header = () => {
    return (
        <Box
            as="header"
            role="banner"
            py="4"
            backgroundColor="gray.800"
            color="gray.300"
            width="100%"
        >
            <Flex justify="space-between" align="center" width="100%" px={6}>
                <Link href="/" _hover={{ textDecoration: 'none' }}>
                
                    <Text fontSize="xl" fontWeight="bold" color="teal.200">
                        Gaucho NeuralBet
                    </Text>
                </Link>

                <Stack direction="row" spacing={6}>
                    <Link href="/features" color="teal.200">Features</Link>
                    <Link href="/register" color="teal.200">Register</Link>
                    <Link href="/login" color="teal.200">Login</Link>
                </Stack>
            </Flex>
        </Box>
    );
};

export default Header;
