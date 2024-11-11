import express from 'express';
import dotenv from 'dotenv';
import { createClient } from 'redis';
import pkg from 'pg';
const { Pool } = pkg;
import amqp from 'amqplib';
import winston from 'winston';

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const port = process.env.PORT || 3000;

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Database connection
const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: process.env.POSTGRES_PORT
});

// Redis connection
const redis = createClient({
  url: `redis://${process.env.REDIS_HOST}:${process.env.REDIS_PORT}`
});

// Connect to RabbitMQ
async function connectQueue() {
  try {
    const connection = await amqp.connect(
      `amqp://${process.env.RABBITMQ_USER}:${process.env.RABBITMQ_PASS}@${process.env.RABBITMQ_HOST}`
    );
    const channel = await connection.createChannel();
    return channel;
  } catch (error) {
    logger.error('Error connecting to RabbitMQ:', error);
    throw error;
  }
}

// Initialize connections
async function initializeServices() {
  try {
    await redis.connect();
    await connectQueue();
    logger.info('All services connected successfully');
  } catch (error) {
    logger.error('Error initializing services:', error);
    process.exit(1);
  }
}

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Start server
app.listen(port, async () => {
  await initializeServices();
  logger.info(`Server running on port ${port}`);
});