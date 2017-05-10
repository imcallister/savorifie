var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
const autoprefixer = require('autoprefixer');
const postcssImport = require('postcss-import');

module.exports = {
  context: __dirname,
  devtool: 'eval',
  entry: [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/only-dev-server',
    'jquery',
    'bootstrap-loader',
    './client/index'
  ],
  output: {
    path: path.resolve('./static/'),
    filename: "bundle.js",
    publicPath: 'http://localhost:3000/assets/bundles/',
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoErrorsPlugin(),
    new BundleTracker({filename: './webpack-stats.json'}),
    new webpack.ProvidePlugin({
            '$': 'jquery',
            'jQuery': 'jquery',
            'window.jQuery': 'jquery'
        })
  ],
  resolve: {
    alias: {
      'react': path.join(__dirname, 'node_modules', 'react')
    },
    extensions: ['', '.js', '.jsx']
  },
  resolveLoader: {
    'fallback': path.join(__dirname, 'node_modules')
  },
  
  module: {
    loaders: [
    {
      test: /\.js?$/,
      loaders: ['babel'],
      exclude: /node_modules/,
      include: __dirname
    }, {
      test: /\.js?$/,
      loaders: ['babel'],
      include: path.join(__dirname, '..', '..', 'src')
    },
    {
      test: /\.jsx?$/,
      loaders: ['babel'],
      exclude: /node_modules/,
      include: __dirname
    }, {
      test: /\.jsx?$/,
      loaders: ['babel'],
      include: path.join(__dirname, '..', '..', 'src')
    },
    {
      test: /\.css?$/,
      loaders: ['style', 'raw'],
      include: __dirname
    },
    {
        test: /\.ttf(\?.*)?$/,
        loader: 'url-loader?name=fonts/[name].[ext]&limit=10000&mimetype=application/octet-stream'
    },
            
    {
        test: /\.svg(\?.*)?$/,
        loader: 'url-loader?name=fonts/[name].[ext]&limit=10000&mimetype=image/svg+xml'
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
        test: /\.eot(\?.*)?$/,
        loader: 'file-loader?name=fonts/[name].[ext]'
    },
                  
    {
          test: /\.scss$/,
          loader: 'style!css?localIdentName=[path][name]--[local]!postcss-loader!sass'
    }, {
        test: /\.jpe?g$|\.gif$|\.png$/,
        loader: 'file?name=images/[name].[ext]?[hash]'
    },
    ]
  },

  sassLoader: {
        data: `@import "${__dirname}/client/styles/config/_variables.scss";`
    },

    postcss: (param) => {
        return [
            autoprefixer({
                browsers: ['last 2 versions']
            }),
            postcssImport({
                addDependencyTo: param
            }),
        ];
    },
};
