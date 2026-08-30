/**
 * STEP 9.3: DATABASE SERVICES & DATA ACCESS LAYER (Node/Mongoose)
 * Aggregation pipelines, batch ingestion, and time-series queries.
 */

const { RawFare, CleanedFare, APIxIndex, RouteData, ScraperLogs, Cache } = require('./models');

class DatabaseService {
  // ============ 1. RAW FARE OPERATIONS ============

  /**
   * Bulk insert scraped raw fares with deduplication
   */
  static async insertRawFares(faresArray) {
    if (!faresArray || faresArray.length === 0) return { inserted: 0 };
    
    const operations = faresArray.map(fare => ({
      updateOne: {
        filter: {
          date: fare.date,
          source: fare.source,
          departure: fare.departure,
          arrival: fare.arrival,
          airline: fare.airline,
          advancePurchaseWindow: fare.advancePurchaseWindow
        },
        update: { $set: fare },
        upsert: true
      }
    }));

    const result = await RawFare.bulkWrite(operations, { ordered: false });
    return {
      upserted: result.upsertedCount,
      modified: result.modifiedCount
    };
  }

  // ============ 2. AGGREGATION FOR INDEX CALCULATION ============

  /**
   * Aggregate cleaned fares by route and advance window for a given date
   */
  static async getRouteAggregates(targetDate) {
    const startOfDay = new Date(targetDate);
    startOfDay.setUTCHours(0, 0, 0, 0);

    const endOfDay = new Date(targetDate);
    endOfDay.setUTCHours(23, 59, 59, 999);

    return await CleanedFare.aggregate([
      {
        $match: {
          date: { $gte: startOfDay, $lte: endOfDay },
          outlier: false
        }
      },
      {
        $group: {
          _id: {
            route: '$route',
            advanceWindow: '$advanceWindow'
          },
          avgFare: { $avg: '$totalFare' },
          medianFare: { $avg: '$totalFare' }, // Can be replaced with percentile in MongoDB 7.0+
          count: { $sum: 1 },
          minFare: { $min: '$totalFare' },
          maxFare: { $max: '$totalFare' }
        }
      },
      {
        $project: {
          _id: 0,
          route: '$_id.route',
          advanceWindow: '$_id.advanceWindow',
          avgFare: { $round: ['$avgFare', 2] },
          count: 1,
          minFare: 1,
          maxFare: 1
        }
      }
    ]);
  }

  // ============ 3. INDEX RETRIEVAL & HISTORICAL SERIES ============

  /**
   * Fetch daily index time-series for specified day window
   */
  static async getHistoricalIndices(days = 30) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return await APIxIndex.find(
      { date: { $gte: cutoffDate } },
      {
        date: 1,
        'dailyIndex.value': 1,
        'trends.mom': 1,
        'confidenceInterval.lower95': 1,
        'confidenceInterval.upper95': 1,
        'dataQuality.overallScore': 1
      }
    )
      .sort({ date: 1 })
      .lean();
  }

  /**
   * Persist calculated index
   */
  static async saveDailyIndex(indexPayload) {
    return await APIxIndex.findOneAndUpdate(
      { date: indexPayload.date },
      { $set: indexPayload },
      { upsert: true, new: true }
    );
  }

  // ============ 4. CACHE LAYER ============

  static async getCache(key) {
    const entry = await Cache.findOne({ key, expiresAt: { $gt: new Date() } });
    return entry ? entry.data : null;
  }

  static async setCache(key, data, ttlSeconds = 300) {
    const expiresAt = new Date(Date.now() + ttlSeconds * 1000);
    return await Cache.findOneAndUpdate(
      { key },
      { $set: { data, expiresAt } },
      { upsert: true }
    );
  }
}

module.exports = DatabaseService;