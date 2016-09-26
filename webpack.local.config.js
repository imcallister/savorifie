var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');

config.plugins.concat([
    new BundleTracker({filename: './webpack-stats.json'})
]);

config.output.path = path.resolve('./assets/bundles/');

module.exports = config;
