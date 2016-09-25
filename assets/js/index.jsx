var React = require('react')
var ReactDOM = require('react-dom')
var App = require('./app')
var BHelp = require('./help') 

ReactDOM.render(<BHelp/>, document.getElementById('the-help'));
ReactDOM.render(<App/>, document.getElementById('the-help2'));

