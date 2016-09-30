var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');

config.plugins.push(new BundleTracker({filename: './webpack-stats.local.json'}));

config.entry = {
    bookkeeping: './assets/js/pages/bookkeeping',
  };

config.output.path = path.resolve('./assets/bundles/');

module.exports = config;
