const createApiResponse = (
  success,
  statusCode,
  data = null,
  options = {}
) => {
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  return {
    status: {
      code: statusCode,
      success,
      timestamp: new Date().toISOString(),
    },
    data,
    error: {
      display: options.displayError || !success,
      code: options.errorCode || null,
      text: options.errorMessage || '',
    },
    message: {
      display: options.displayMessage || success,
      type: options.messageType || (success ? 'success' : 'error'),
      text: options.successMessage || options.errorMessage || '',
    },
    meta: {
      requestId,
      ...(options.pagination && { pagination: options.pagination }),
      ...(options.metadata && { metadata: options.metadata }),
    },
  };
};

module.exports = { createApiResponse };