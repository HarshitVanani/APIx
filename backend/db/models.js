/**
 * STEP 9.2: MONGODB SCHEMAS & DATA MODELS
 * Comprehensive database models for APIx
 * SIH 2026 - Professional Grade
 */

const mongoose = require('mongoose');

// ============ RAW FARE SCHEMA ============

const RawFareSchema = new mongoose.Schema({
  date: {
    type: Date,
    required: true,
    index: true,
    description: 'Date of fare record'
  },
  source: {
    type: String,
    enum: ['indigo', 'air-india', 'air-india-express', 'akasa', 'spicejet', 'makemytrip', 'yatra', 'easemytrip', 'cleartrip', 'ixigo', 'goibibo'],
    required: true,
    index: true,
  },
  departure: {
    type: String,
    required: true,
    uppercase: true,
    index: true,
  },
  arrival: {
    type: String,
    required: true,
    uppercase: true,
    index: true,
  },
  airline: {
    type: String,
    enum: ['indigo', 'air-india', 'air-india-express', 'akasa', 'spicejet'],
    required: true,
    index: true,
  },
  baseFare: {
    type: Number,
    required: true,
    min: 0,
    description: 'Base fare in INR'
  },
  tax: {
    type: Number,
    required: true,
    min: 0,
  },
  surcharges: {
    type: Number,
    default: 0,
    min: 0,
  },
  totalFare: {
    type: Number,
    required: true,
    min: 0,
  },
  advancePurchaseWindow: {
    type: String,
    enum: ['T+1', 'T+7', 'T+15', 'T+30', 'T+45'],
    required: true,
    index: true,
  },
  departureTime: Date,
  arrivalTime: Date,
  duration: Number, // in minutes
  stopPages: Number,
  currency: {
    type: String,
    default: 'INR',
  },
  scrapedAt: {
    type: Date,
    default: Date.now,
    index: true,
  },
  valid: {
    type: Boolean,
    default: true,
  },
}, {
  timestamps: true,
  collection: 'raw_fares'
});

// ============ CLEANED FARE SCHEMA ============

const CleanedFareSchema = new mongoose.Schema({
  rawFareId: mongoose.Schema.Types.ObjectId,
  route: {
    type: String,
    required: true,
    index: true,
    description: 'Route code: DEL-BOM'
  },
  baseFare: {
    type: Number,
    required: true,
  },
  tax: {
    type: Number,
    required: true,
  },
  totalFare: {
    type: Number,
    required: true,
  },
  advanceWindow: {
    type: String,
    enum: ['T+1', 'T+7', 'T+15', 'T+30', 'T+45'],
    required: true,
    index: true,
  },
  airline: String,
  source: String,
  date: {
    type: Date,
    required: true,
    index: true,
  },
  cleanedAt: {
    type: Date,
    default: Date.now,
  },
  qualityScore: {
    type: Number,
    min: 0,
    max: 100,
  },
  outlier: {
    type: Boolean,
    default: false,
  },
}, {
  timestamps: true,
  collection: 'cleaned_fares',
});

// ============ APIX INDEX SCHEMA ============

const APIxIndexSchema = new mongoose.Schema({
  date: {
    type: Date,
    required: true,
    unique: true,
    index: true,
  },
  dailyIndex: {
    value: {
      type: Number,
      required: true,
      description: 'Daily index value'
    },
    baseValue: {
      type: Number,
      default: 100,
      description: 'Baseline = 100'
    },
  },
  weeklyIndex: {
    value: Number,
    weekStartDate: Date,
  },
  monthlyIndex: {
    value: Number,
    month: String,
    year: Number,
  },
  routes: [{
    route: String,
    weight: Number,
    avgFare: Number,
    indexContribution: Number,
  }],
  trends: {
    mom: Number,
    yoy: Number,
    volatility90d: Number,
    trendDirection: {
      type: String,
      enum: ['up', 'down', 'stable'],
    },
    trendStrength: {
      type: Number,
      min: 0,
      max: 100,
    }
  },
  confidenceInterval: {
    lower95: Number,
    upper95: Number,
    confidence: {
      type: Number,
      default: 95,
    }
  },
  dataQuality: {
    volumeScore: Number,
    routeDiversityScore: Number,
    consistencyScore: Number,
    completenessScore: Number,
    overallScore: {
      type: Number,
      min: 0,
      max: 100,
    }
  },
  faresIncluded: Number,
  routesIncluded: Number,
  airlinesIncluded: Number,
  advanceWindowDistribution: {
    'T+1': Number,
    'T+7': Number,
    'T+15': Number,
    'T+30': Number,
    'T+45': Number,
  },
  calculatedAt: {
    type: Date,
    default: Date.now,
  },
  calculationMethod: {
    type: String,
    default: 'weighted-average-with-quality-adjustment',
  },
  nsoSubmitted: {
    type: Boolean,
    default: false,
  },
  nsoSubmissionId: String,
  nsoSubmissionDate: Date,
}, {
  timestamps: true,
  collection: 'apix_index',
});

// ============ ROUTE DATA SCHEMA ============

const RouteDataSchema = new mongoose.Schema({
  route: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  dgcaTrafficVolume: Number,
  dgcaTrafficWeight: {
    type: Number,
    min: 0,
    max: 1,
  },
  departure: {
    code: String,
    city: String,
    country: String,
  },
  arrival: {
    code: String,
    city: String,
    country: String,
  },
  distance: Number,
  airlinesOperating: [String],
  currentAvgFare: Number,
  currentIndex: Number,
  lastUpdated: Date,
  historical90dAvg: Number,
  historical30dAvg: Number,
}, {
  timestamps: true,
  collection: 'routes_data',
});

// ============ SCRAPER LOGS SCHEMA ============

const ScraperLogsSchema = new mongoose.Schema({
  date: {
    type: Date,
    default: Date.now,
    index: true,
  },
  source: {
    type: String,
    required: true,
  },
  route: {
    type: String,
    index: true,
  },
  status: {
    type: String,
    enum: ['success', 'partial', 'failed', 'timeout'],
    required: true,
  },
  faresScraped: Number,
  errorMessage: String,
  executionTime: Number,
  metadata: {
    userAgent: String,
    ipAddress: String,
    proxy: String,
  }
}, {
  timestamps: true,
  collection: 'scraper_logs',
  expireAfterSeconds: 2592000, // TTL 30 days
});

// ============ DATA CACHE SCHEMA ============

const CacheSchema = new mongoose.Schema({
  key: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  data: mongoose.Schema.Types.Mixed,
  expiresAt: {
    type: Date,
    index: { expireAfterSeconds: 0 },
  },
  createdAt: {
    type: Date,
    default: Date.now,
  }
}, {
  collection: 'cache',
});

// ============ INDEXES ============
RawFareSchema.index({ date: 1, source: 1, departure: 1, arrival: 1 });
RawFareSchema.index({ departure: 1, arrival: 1, advancePurchaseWindow: 1 });
RawFareSchema.index({ airline: 1, date: 1 });
CleanedFareSchema.index({ date: 1, route: 1, advanceWindow: 1 });
APIxIndexSchema.index({ date: -1 });

// ============ CREATE & EXPORT MODELS ============

const RawFare = mongoose.model('RawFare', RawFareSchema);
const CleanedFare = mongoose.model('CleanedFare', CleanedFareSchema);
const APIxIndex = mongoose.model('APIxIndex', APIxIndexSchema);
const RouteData = mongoose.model('RouteData', RouteDataSchema);
const ScraperLogs = mongoose.model('ScraperLogs', ScraperLogsSchema);
const Cache = mongoose.model('Cache', CacheSchema);

module.exports = {
  RawFare,
  CleanedFare,
  APIxIndex,
  RouteData,
  ScraperLogs,
  Cache,
  RawFareSchema,
  CleanedFareSchema,
  APIxIndexSchema,
  RouteDataSchema,
  ScraperLogsSchema,
  CacheSchema,
};