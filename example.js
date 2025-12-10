/**
 * Custom Algorithm Examples for Hypixel Skyblock Bazaar Tracker
 * These functions demonstrate how to create technical indicators and trading algorithms
 * using the system's custom algorithm feature.
 */

/**
 * Simple Moving Average (SMA) Indicator
 * Calculates the average price over a specified period
 * @param {Array} data - Array of {time, value} objects
 * @returns {Object} - Chart-ready indicator data
 */
function simpleMovingAverage(data) {
    const period = 20;
    const result = [];

    for (let i = period - 1; i < data.length; i++) {
        const slice = data.slice(i - period + 1, i + 1);
        const sum = slice.reduce((a, b) => a + b.value, 0);
        const average = sum / period;

        result.push({
            time: data[i].time,
            value: average
        });
    }

    return {
        data: result,
        color: '#2962ff',
        lineWidth: 2,
        title: `SMA (${period})`
    };
}

/**
 * Exponential Moving Average (EMA) Indicator
 * Gives more weight to recent prices
 * @param {Array} data - Array of {time, value} objects
 * @returns {Object} - Chart-ready indicator data
 */
function exponentialMovingAverage(data) {
    const period = 20;
    const result = [];
    const multiplier = 2 / (period + 1);

    // Calculate initial SMA for first EMA value
    let sum = 0;
    for (let i = 0; i < period; i++) {
        sum += data[i].value;
    }
    let ema = sum / period;

    result.push({
        time: data[period - 1].time,
        value: ema
    });

    // Calculate subsequent EMA values
    for (let i = period; i < data.length; i++) {
        ema = (data[i].value - ema) * multiplier + ema;
        result.push({
            time: data[i].time,
            value: ema
        });
    }

    return {
        data: result,
        color: '#ff6b35',
        lineWidth: 2,
        title: `EMA (${period})`
    };
}

/**
 * Bollinger Bands Indicator
 * Shows volatility bands around a moving average
 * @param {Array} data - Array of {time, value} objects
 * @returns {Object} - Multiple chart series for bands
 */
function bollingerBands(data) {
    const period = 20;
    const standardDeviations = 2;

    const sma = [];
    const upperBand = [];
    const lowerBand = [];

    for (let i = period - 1; i < data.length; i++) {
        const slice = data.slice(i - period + 1, i + 1);
        const values = slice.map(d => d.value);

        // Calculate SMA
        const sum = values.reduce((a, b) => a + b, 0);
        const mean = sum / period;

        // Calculate standard deviation
        const squaredDiffs = values.map(value => Math.pow(value - mean, 2));
        const variance = squaredDiffs.reduce((a, b) => a + b, 0) / period;
        const stdDev = Math.sqrt(variance);

        const timestamp = data[i].time;

        sma.push({ time: timestamp, value: mean });
        upperBand.push({ time: timestamp, value: mean + (stdDev * standardDeviations) });
        lowerBand.push({ time: timestamp, value: mean - (stdDev * standardDeviations) });
    }

    return {
        lines: [
            {
                data: sma,
                color: '#f39c12',
                lineWidth: 1.5,
                title: 'SMA'
            },
            {
                data: upperBand,
                color: '#95a5a6',
                lineWidth: 1,
                lineStyle: 2, // Dashed line
                title: 'Upper Band'
            },
            {
                data: lowerBand,
                color: '#95a5a6',
                lineWidth: 1,
                lineStyle: 2, // Dashed line
                title: 'Lower Band'
            }
        ],
        title: `Bollinger Bands (${period}, ${standardDeviations}σ)`
    };
}

/**
 * Relative Strength Index (RSI) Indicator
 * Measures price momentum on a scale of 0-100
 * @param {Array} data - Array of {time, value} objects
 * @returns {Object} - Chart-ready indicator data
 */
function relativeStrengthIndex(data) {
    const period = 14;
    const result = [];
    const gains = [];
    const losses = [];

    // Calculate price changes
    for (let i = 1; i < data.length; i++) {
        const change = data[i].value - data[i - 1].value;
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
    }

    // Calculate initial averages
    let avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
    let avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;

    // Calculate RSI for subsequent periods
    for (let i = period; i < data.length; i++) {
        if (i > period) {
            // Smoothed averages
            avgGain = (avgGain * (period - 1) + gains[i - 1]) / period;
            avgLoss = (avgLoss * (period - 1) + losses[i - 1]) / period;
        }

        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));

        result.push({
            time: data[i].time,
            value: rsi
        });
    }

    return {
        data: result,
        color: '#9b59b6',
        lineWidth: 2,
        title: `RSI (${period})`,
        // Add overbought/oversold reference lines
        referenceLines: [
            { value: 70, color: '#e74c3c', label: 'Overbought' },
            { value: 30, color: '#27ae60', label: 'Oversold' }
        ]
    };
}

/**
 * Volume Weighted Average Price (VWAP) Indicator
 * Calculates the average price weighted by volume
 * @param {Array} data - Array of {time, value, volume} objects
 * @returns {Object} - Chart-ready indicator data
 */
function volumeWeightedAveragePrice(data) {
    const result = [];
    let cumulativeVolume = 0;
    let cumulativeVolumePrice = 0;

    for (const point of data) {
        // Note: This example assumes volume data is available
        // In a real implementation, you'd need to get volume from the candle data
        const volume = point.volume || 1; // Fallback if no volume data

        cumulativeVolume += volume;
        cumulativeVolumePrice += point.value * volume;

        const vwap = cumulativeVolumePrice / cumulativeVolume;

        result.push({
            time: point.time,
            value: vwap
        });
    }

    return {
        data: result,
        color: '#e67e22',
        lineWidth: 2,
        title: 'VWAP'
    };
}

/**
 * MACD (Moving Average Convergence Divergence) Indicator
 * Shows relationship between two moving averages
 * @param {Array} data - Array of {time, value} objects
 * @returns {Object} - Multiple chart series (MACD line and signal)
 */
function macdIndicator(data) {
    const fastPeriod = 12;
    const slowPeriod = 26;
    const signalPeriod = 9;

    // Calculate EMAs
    const fastEMA = calculateEMA(data, fastPeriod);
    const slowEMA = calculateEMA(data, slowPeriod);

    // Calculate MACD line
    const macdLine = [];
    const minLength = Math.min(fastEMA.length, slowEMA.length);

    for (let i = 0; i < minLength; i++) {
        macdLine.push({
            time: fastEMA[i].time,
            value: fastEMA[i].value - slowEMA[i].value
        });
    }

    // Calculate signal line (EMA of MACD)
    const signalLine = calculateEMA(macdLine.map(point => ({
        time: point.time,
        value: point.value
    })), signalPeriod);

    // Calculate histogram
    const histogram = [];
    const signalMinLength = Math.min(macdLine.length, signalLine.length);

    for (let i = 0; i < signalMinLength; i++) {
        const macdValue = macdLine[i + (macdLine.length - signalMinLength)].value;
        const signalValue = signalLine[i].value;

        histogram.push({
            time: signalLine[i].time,
            value: macdValue - signalValue,
            color: macdValue > signalValue ? '#27ae60' : '#e74c3c'
        });
    }

    return {
        lines: [
            {
                data: macdLine.slice(-signalMinLength),
                color: '#3498db',
                lineWidth: 1,
                title: 'MACD'
            },
            {
                data: signalLine,
                color: '#e74c3c',
                lineWidth: 1,
                title: 'Signal'
            }
        ],
        histogram: {
            data: histogram,
            title: 'MACD Histogram'
        },
        title: `MACD (${fastPeriod}, ${slowPeriod}, ${signalPeriod})`
    };
}

/**
 * Helper function to calculate EMA (used by MACD)
 * @param {Array} data - Array of {time, value} objects
 * @param {number} period - Period for EMA calculation
 * @returns {Array} - EMA data points
 */
function calculateEMA(data, period) {
    const result = [];
    const multiplier = 2 / (period + 1);

    let ema = data.slice(0, period).reduce((sum, point) => sum + point.value, 0) / period;
    result.push({ time: data[period - 1].time, value: ema });

    for (let i = period; i < data.length; i++) {
        ema = (data[i].value - ema) * multiplier + ema;
        result.push({ time: data[i].time, value: ema });
    }

    return result;
}

/**
 * Example of a custom trading strategy
 * Combines multiple indicators to generate buy/sell signals
 * @param {Array} data - Array of {time, value} objects
 * @returns {Object} - Trading signals
 */
function customTradingStrategy(data) {
    const sma20 = simpleMovingAverage(data);
    const rsi = relativeStrengthIndex(data);

    const signals = [];

    // Simple strategy: Buy when RSI < 30 and price > SMA, Sell when RSI > 70
    for (let i = Math.max(20, 14); i < data.length; i++) {
        const currentPrice = data[i].value;
        const currentSMA = sma20.data.find(point => point.time === data[i].time)?.value;
        const currentRSI = rsi.data.find(point => point.time === data[i].time)?.value;

        if (currentSMA && currentRSI) {
            let signal = null;
            let color = '#95a5a6';

            if (currentRSI < 30 && currentPrice > currentSMA) {
                signal = 'BUY';
                color = '#27ae60';
            } else if (currentRSI > 70) {
                signal = 'SELL';
                color = '#e74c3c';
            }

            if (signal) {
                signals.push({
                    time: data[i].time,
                    value: currentPrice,
                    signal: signal,
                    color: color,
                    rsi: currentRSI,
                    sma: currentSMA
                });
            }
        }
    }

    return {
        data: signals,
        title: 'Custom Strategy Signals',
        signalBased: true,
        description: 'Buy when RSI < 30 and price > SMA20, Sell when RSI > 70'
    };
}

// Export functions for use in the main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        simpleMovingAverage,
        exponentialMovingAverage,
        bollingerBands,
        relativeStrengthIndex,
        volumeWeightedAveragePrice,
        macdIndicator,
        customTradingStrategy
    };
}