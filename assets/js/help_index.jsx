var React = require('react')
var ReactDOM = require('react-dom')
var App = require('./app')
var BHelp = require('./help') 
var CommentBox = require('./tutorial') 
var DataTable = require('./fdatatable')
var BSTable = require('./bstable')

ReactDOM.render(<BHelp/>, document.getElementById('the-help'));
ReactDOM.render(<BSTable/>, document.getElementById('the-help2'));
