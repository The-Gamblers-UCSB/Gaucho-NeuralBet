import { Box, Text, Flex, Stack, Link } from '@chakra-ui/react';
import React from 'react';

const Footer = () => {
    return (
        <Box
            as="footer"
            role="contentinfo"
            mt="auto" /* To make the footer stick to the bottom if there's enough content */
            py="4"
            backgroundColor="gray.800"
            color="gray.300"
            textAlign="center"
            width="100%"
        >
            <Flex justify="center" align="center" direction="column">
                <Stack direction="row" spacing={6} mb={3}>
                    <Link href="/about" color="teal.200">About Us</Link>
                    <Link href="/services" color="teal.200">Services</Link>
                    <Link href="/contact" color="teal.200">Contact</Link>
                </Stack>
                <Text fontSize="sm">
                    © 2025 Gaucho NeuralBet. All Rights Reserved.
                </Text>
            </Flex>
        </Box>
    );
};

export default Footer;