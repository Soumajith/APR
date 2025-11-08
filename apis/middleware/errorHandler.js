const { createApiResponse } = require('../utils/apiResponse');

const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  let statusCode = err.statusCode || 500;
  let errorMessage = err.message || 'Internal server error';
  let errorCode = err.code || 'INTERNAL_ERROR';

  // MongoDB duplicate key error
  if (err.code === 11000) {
    statusCode = 400;
    const field = Object.keys(err.keyPattern)[0];
    errorMessage = `${field} already exists`;
    errorCode = 'DUPLICATE_ENTRY';
  }

  // MongoDB validation error
  if (err.name === 'ValidationError') {
    statusCode = 400;
    errorMessage = Object.values(err.errors).map(e => e.message).join(', ');
    errorCode = 'VALIDATION_ERROR';
  }

  // MongoDB cast error
  if (err.name === 'CastError') {
    statusCode = 400;
    errorMessage = 'Invalid ID format';
    errorCode = 'INVALID_ID';
  }

  res.status(statusCode).json(
    createApiResponse(false, statusCode, null, {
      errorMessage,
      errorCode,
      displayError: true
    })
  );
};

module.exports = errorHandler;