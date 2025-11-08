const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { createApiResponse } = require('../utils/apiResponse');

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
      return res.status(401).json(
        createApiResponse(false, 401, null, {
          errorMessage: 'No token provided. Please authenticate.',
          errorCode: 'NO_TOKEN',
          displayError: true
        })
      );
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    const user = await User.findById(decoded.id).select('-password');
    
    if (!user) {
      return res.status(401).json(
        createApiResponse(false, 401, null, {
          errorMessage: 'User not found. Invalid token.',
          errorCode: 'USER_NOT_FOUND',
          displayError: true
        })
      );
    }
    
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json(
        createApiResponse(false, 401, null, {
          errorMessage: 'Invalid token. Please login again.',
          errorCode: 'INVALID_TOKEN',
          displayError: true
        })
      );
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json(
        createApiResponse(false, 401, null, {
          errorMessage: 'Token expired. Please login again.',
          errorCode: 'TOKEN_EXPIRED',
          displayError: true
        })
      );
    }
    
    return res.status(500).json(
      createApiResponse(false, 500, null, {
        errorMessage: 'Authentication failed',
        errorCode: 'AUTH_ERROR',
        displayError: true
      })
    );
  }
};

const adminMiddleware = (req, res, next) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json(
      createApiResponse(false, 403, null, {
        errorMessage: 'Access denied. Admin privileges required.',
        errorCode: 'ADMIN_ACCESS_REQUIRED',
        displayError: true
      })
    );
  }
  next();
};

module.exports = { authMiddleware, adminMiddleware, JWT_SECRET };