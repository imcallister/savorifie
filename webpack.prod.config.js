var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');

config.plugins.push(new BundleTracker({filename: './webpack-stats.prod.json'}));

config.output.path = path.resolve('./assets/dist/');

config.entry = {
    bookkeeping: './assets/js/pages/bookkeeping',
    receivables: './assets/js/pages/receivables',
    highcharts: './assets/js/pages/highcharts',
    inventory: './assets/js/pages/inventory',
    reports: './assets/js/pages/reports',
    cogs: './assets/js/pages/cogs',
    shippingcosts: './assets/js/pages/shippingcosts',
    periodend: './assets/js/pages/periodend',
};

module.exports = config;
