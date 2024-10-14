import React from "react"; // Ensure React is imported
import { BrowserRouter as Router, Route, Routes } from "react-router-dom"; // Import BrowserRouter
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import Login from './pages/Login'; // Adjust import paths if necessary
import Signup from './pages/Signup'; // Adjust import paths if necessary
import HomePage from './pages/HomePage'; // Adjust import paths if necessary
import { ChakraProvider } from "@chakra-ui/react"; // Import ChakraProvider
import { extendTheme } from "@chakra-ui/react"; // Import extendTheme

// Theme definition
const colors = {
  brand: {
    900: "#1a365d",
    800: "#153e75",
    700: "#2a69ac",
  },
};

const theme = extendTheme({ colors }); // Create theme

function App() {
  console.log("App is rendering"); // Log when App renders
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Routes>
          <Route path='/' element={<HomePage />} />  {/* Default route */}
          <Route path='/register' element={<Signup />} />
          <Route path='/login' element={<Login />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App; // Export App
