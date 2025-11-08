const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { createApiResponse } = require('../utils/apiResponse');
const { JWT_SECRET } = require('../middleware/auth');

exports.register = async (req, res, next) => {
  try {
    const { name, email, password, role, department } = req.body;

    // Validation
    if (!name || !email || !password) {
      return res.status(400).json(
        createApiResponse(false, 400, null, {
          errorMessage: 'Name, email, and password are required',
          errorCode: 'MISSING_FIELDS',
          displayError: true
        })
      );
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json(
        createApiResponse(false, 400, null, {
          errorMessage: 'Email already registered',
          errorCode: 'EMAIL_EXISTS',
          displayError: true
        })
      );
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = new User({
      name,
      email,
      password: hashedPassword,
      role: role || 'employee',
      department
    });

    await user.save();

    const token = jwt.sign({ id: user._id }, JWT_SECRET, { expiresIn: '7d' });
    
    const userData = {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      department: user.department,
      token
    };

    res.status(201).json(
      createApiResponse(true, 201, userData, {
        successMessage: 'User registered successfully',
        messageType: 'success',
        displayMessage: true
      })
    );
  } catch (error) {
    next(error);
  }
};

exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json(
        createApiResponse(false, 400, null, {
          errorMessage: 'Email and password are required',
          errorCode: 'MISSING_CREDENTIALS',
          displayError: true
        })
      );
    }

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json(
        createApiResponse(false, 401, null, {
          errorMessage: 'Invalid email or password',
          errorCode: 'INVALID_CREDENTIALS',
          displayError: true
        })
      );
    }

    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json(
        createApiResponse(false, 401, null, {
          errorMessage: 'Invalid email or password',
          errorCode: 'INVALID_CREDENTIALS',
          displayError: true
        })
      );
    }

    const token = jwt.sign({ id: user._id }, JWT_SECRET, { expiresIn: '7d' });

    const userData = {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      department: user.department,
      token
    };

    res.json(
      createApiResponse(true, 200, userData, {
        successMessage: 'Login successful',
        messageType: 'success',
        displayMessage: true
      })
    );
  } catch (error) {
    next(error);
  }
};