const express = require('express');
const cors = require('cors');
const serverless = require('serverless-http');
require('dotenv').config();

const connectDB = require('./config/database');
const errorHandler = require('./middleware/errorHandler');
const { createApiResponse } = require('./utils/apiResponse');

const authRoutes = require('./routes/auth.routes');

const app = express();
app.use(express.json());
app.use(cors());

// Connect to MongoDB
connectDB();

// Routes
app.get('/api/health', (req, res) => {
  res.json(
    createApiResponse(true, 200, { 
      status: 'healthy',
      service: 'Attendance System API',
      timestamp: new Date().toISOString()
    }, {
      successMessage: 'Service is running',
      messageType: 'info',
      displayMessage: false
    })
  );
});

app.use('/api/auth', authRoutes);


// 404 handler
app.use((req, res) => {
  res.status(404).json(
    createApiResponse(false, 404, null, {
      errorMessage: 'Route not found',
      errorCode: 'ROUTE_NOT_FOUND',
      displayError: true
    })
  );
});

app.use(errorHandler);

module.exports = app;
module.exports.handler = serverless(app);
