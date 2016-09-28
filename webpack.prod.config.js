var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');

config.plugins.push(new BundleTracker({filename: './webpack-stats.prod.json'}));

config.output.path = path.resolve('./assets/dist/');

config.entry = {
    index: './assets/js/index',
    help: './assets/js/help_index'
};

module.exports = config;
