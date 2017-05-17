var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const extractCSS = new ExtractTextPlugin('styles/[name].css');


module.exports = {
  context: __dirname,

  entry: ['./assets/js/index', // entry point of our app. assets/js/index.js should require other js modules and dependencies it needs
          'bootstrap-loader'
          ],

  output: {
      filename: "[name]-[hash].js",
  },

  plugins: [extractCSS],

  module: {
    loaders: [
      { test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
      { test: /\.less?$/,
        exclude: /node_modules/,
        loader: 'style-loader!css-loader!less-loader',
      },
      {
        test: /\.css?$/,
        loader: 'style!css'
      },
    
      {
          test: /\.scss$/,
          loader: ExtractTextPlugin.extract("style-loader", "css-loader")
      },
      {
        test: /\.woff(\?.*)?$/,
        loader: 'url-loader?name=fonts/[name].[ext]&limit=10000&mimetype=application/font-woff'
      },
      {
          test: /\.woff2(\?.*)?$/,
          loader: 'url-loader?name=fonts/[name].[ext]&limit=10000&mimetype=application/font-woff2'
      },
      {
          test: /\.eot|ttf(\?.*)?$/,
          loader: 'url-loader?name=fonts/[name].[ext]&limit=10000&mimetype=application/font-woff2'
      },
      {
        test: /\.jpe?g$|\.gif$|\.png$/,
        loader: 'url-loader?limit-1024'
      },
      {
        test: /\.svg(\?.*)?$/,
        loader: 'url-loader?name=fonts/[name].[ext]&limit=10000&mimetype=image/svg+xml'
    },
    
    ],
  },

  
  resolve: {
    modulesDirectories: ['node_modules', 'bower_components'],
    extensions: ['', '.js', '.jsx']
  },
}