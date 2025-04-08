import React from 'react';
import { Route, Redirect } from 'react-router-dom';
import PropTypes from 'prop-types';  // Import PropTypes

const ProtectedRoute = ({ component: Component, ...rest }) => {
  const user = { name: 'John Doe' }; // Replace with actual authentication logic

  return (
    <Route
      {...rest}
      render={(props) =>
        user ? (
          <Component {...props} />
        ) : (
          <Redirect to="/login" />
        )
      }
    />
  );
};

// Add prop validation
ProtectedRoute.propTypes = {
  component: PropTypes.elementType.isRequired, // Validate that `component` is a React component type
};

export default ProtectedRoute;
