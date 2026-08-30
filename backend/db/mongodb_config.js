/**
 * STEP 9.1: MONGODB CONNECTION & CONFIGURATION
 * Production-Grade Database Setup
 * SIH 2026 - APIx Project
 */

const mongoose = require('mongoose');
require('dotenv').config();

// ============ MONGODB CONNECTION CONFIG ============

const MONGODB_CONFIG = {
  // Development
  development: {
    uri: process.env.MONGODB_DEV_URI || 'mongodb://localhost:27017/apix-dev',
    options: {
      retryWrites: true,
      w: 'majority',
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    }
  },

  // Production
  production: {
    uri: process.env.MONGODB_PROD_URI || 'mongodb+srv://user:pass@cluster.mongodb.net/apix-prod',
    options: {
      retryWrites: true,
      w: 'majority',
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    }
  },

  // Testing
  testing: {
    uri: process.env.MONGODB_TEST_URI || 'mongodb://localhost:27017/apix-test',
    options: {
      retryWrites: true,
      w: 'majority',
    }
  }
};

// ============ CONNECTION CLASS ============

class MongoDBConnection {
  constructor() {
    this.connection = null;
    this.isConnected = false;
    this.env = process.env.NODE_ENV || 'development';
  }

  /**
   * Connect to MongoDB
   */
  async connect() {
    if (this.isConnected) {
      console.log('✅ MongoDB already connected');
      return this.connection;
    }

    try {
      const config = MONGODB_CONFIG[this.env];
      console.log(`🔗 Connecting to MongoDB [${this.env}]...`);

      this.connection = await mongoose.connect(config.uri, config.options);
      this.isConnected = true;

      // Event listeners
      mongoose.connection.on('connected', () => {
        console.log('✅ MongoDB connected successfully');
      });

      mongoose.connection.on('error', (error) => {
        console.error('❌ MongoDB connection error:', error);
        this.isConnected = false;
      });

      mongoose.connection.on('disconnected', () => {
        console.warn('⚠️ MongoDB disconnected');
        this.isConnected = false;
      });

      return this.connection;
    } catch (error) {
      console.error('❌ Failed to connect to MongoDB:', error.message);
      throw error;
    }
  }

  /**
   * Disconnect from MongoDB
   */
  async disconnect() {
    if (!this.isConnected) {
      console.log('ℹ️ MongoDB not connected');
      return;
    }

    try {
      await mongoose.disconnect();
      this.isConnected = false;
      console.log('✅ MongoDB disconnected');
    } catch (error) {
      console.error('❌ Error disconnecting from MongoDB:', error);
      throw error;
    }
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      connected: this.isConnected,
      env: this.env,
      uri: MONGODB_CONFIG[this.env].uri,
      readyState: mongoose.connection.readyState,
    };
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      if (!this.isConnected) {
        return { status: 'disconnected', message: 'MongoDB not connected' };
      }

      const db = mongoose.connection.getClient().db('admin');
      const result = await db.command({ ping: 1 });

      return {
        status: 'healthy',
        ping: result.ok === 1,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  }

  /**
   * Get database stats
   */
  async getDbStats() {
    try {
      if (!this.isConnected) {
        throw new Error('MongoDB not connected');
      }

      const db = mongoose.connection.db;
      const stats = await db.stats();

      return {
        collections: stats.collections,
        dataSize: stats.dataSize,
        indexes: stats.indexes,
        avgObjSize: stats.avgObjSize,
        storageSize: stats.storageSize,
      };
    } catch (error) {
      console.error('Error getting DB stats:', error);
      return null;
    }
  }
}

// ============ SINGLETON INSTANCE ============

let mongodbInstance = null;

function getMongoDBConnection() {
  if (!mongodbInstance) {
    mongodbInstance = new MongoDBConnection();
  }
  return mongodbInstance;
}

// ============ EXPORT ============

module.exports = {
  MongoDBConnection,
  getMongoDBConnection,
  MONGODB_CONFIG,
};