import React from 'react';
import { Box, Button, Text, Heading, VStack, useBreakpointValue, Fade } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { FaChartLine, FaBrain, FaTrophy } from 'react-icons/fa';
import Footer from "../components/footer"
const AnimatedBox = motion(Box);

const Homepage = () => {
  const isMobile = useBreakpointValue({ base: true, md: false });

  return (
    <Box>
    <VStack spacing={8} align="center" p={8} bg="gray.50" minHeight="100vh">
      <Fade in>
        <Heading as="h1" size="3xl" color="teal.500" textAlign="center">
          Sports Betting Optimizer
        </Heading>
      </Fade>

      <AnimatedBox
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <Text fontSize="xl" textAlign="center" maxW="600px">
          Track your betting performance and optimize your strategies with AI-backed analysis. 
          Our neural network analyzes your betting history to provide intelligent recommendations based on your behavior.
        </Text>
      </AnimatedBox>

      <VStack spacing={6} direction={isMobile ? 'column' : 'row'} justify="center" wrap="wrap">
        <AnimatedBox
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Box p={6} bg="white" boxShadow="md" rounded="md" textAlign="center" width="250px">
            <FaChartLine size={40} color="teal.500" />
            <Heading size="md" color="teal.700" mt={4}>
              Bet Performance Tracking
            </Heading>
            <Text mt={2}>Track whether your bets are successful or not to improve your strategy.</Text>
          </Box>
        </AnimatedBox>

        <AnimatedBox
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Box p={6} bg="white" boxShadow="md" rounded="md" textAlign="center" width="250px">
            <FaBrain size={40} color="teal.500" />
            <Heading size="md" color="teal.700" mt={4}>
              Neural Network Analysis
            </Heading>
            <Text mt={2}>Our neural network analyzes your betting behavior and offers valuable insights.</Text>
          </Box>
        </AnimatedBox>

        <AnimatedBox
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Box p={6} bg="white" boxShadow="md" rounded="md" textAlign="center" width="250px">
            <FaTrophy size={40} color="teal.500" />
            <Heading size="md" color="teal.700" mt={4}>
              Bet Recommendations
            </Heading>
            <Text mt={2}>Get intelligent betting recommendations based on your performance history.</Text>
          </Box>
        </AnimatedBox>
      </VStack>

      <Button
        size="lg"
        colorScheme="teal"
        variant="solid"
        rightIcon={<FaTrophy />}
        mt={8}
        onClick={() => alert('Start Optimizing!')}
      >
        Get Started
      </Button>
    </VStack>
        <Footer />
    </Box>
  );
};

export default Homepage;
