var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');

config.plugins.push(new BundleTracker({filename: './webpack-stats.local.json'}));

config.entry = {
    bookkeeping: './assets/js/pages/bookkeeping',
    fulfillment: './assets/js/pages/fulfillment',
    receivables: './assets/js/pages/receivables',
    highcharts: './assets/js/pages/highcharts',
    inventory: './assets/js/pages/inventory',
    reports: './assets/js/pages/reports',
    cogs: './assets/js/pages/cogs',
    shippingcosts: './assets/js/pages/shippingcosts',
    periodend: './assets/js/pages/periodend',
  };

config.output.path = path.resolve('./assets/bundles/');

module.exports = config;
