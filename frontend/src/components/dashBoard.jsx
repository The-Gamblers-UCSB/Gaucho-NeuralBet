import React from 'react';
import { Box, Heading, Text, VStack, SimpleGrid, Stat, StatLabel, StatNumber, Button } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { FaChartBar, FaBrain, FaLightbulb } from 'react-icons/fa';

const AnimatedBox = motion(Box);

const Dashboard = () => {
  const user = { name: 'John Doe' }; // Eventually pull from auth

  return (
    <Box bg="gray.50" minH="100vh" p={8}>
      <VStack spacing={6} align="center">
        <Heading as="h2" size="2xl" color="teal.600">
          Welcome, {user.name}
        </Heading>

        <Text fontSize="lg" color="gray.600">
          Here's how you're doing so far.
        </Text>

        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full" maxW="1000px" mt={4}>
          <AnimatedBox
            as={Stat}
            bg="white"
            p={6}
            boxShadow="md"
            rounded="md"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <StatLabel>Success Rate</StatLabel>
            <StatNumber color="teal.500">65%</StatNumber>
            <FaChartBar size={30} style={{ marginTop: 10 }} />
          </AnimatedBox>

          <AnimatedBox
            as={Stat}
            bg="white"
            p={6}
            boxShadow="md"
            rounded="md"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <StatLabel>Neural Insights</StatLabel>
            <StatNumber color="teal.500">5 Alerts</StatNumber>
            <FaBrain size={30} style={{ marginTop: 10 }} />
          </AnimatedBox>

          <AnimatedBox
            as={Stat}
            bg="white"
            p={6}
            boxShadow="md"
            rounded="md"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <StatLabel>Recommendations</StatLabel>
            <StatNumber color="teal.500">3 Bets</StatNumber>
            <FaLightbulb size={30} style={{ marginTop: 10 }} />
          </AnimatedBox>
        </SimpleGrid>

        <Button mt={6} colorScheme="teal" size="lg">
          Analyze My Bets
        </Button>
      </VStack>
    </Box>
  );
};

export default Dashboard;
