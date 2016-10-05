var moment = require('moment')

function priceFormatter(cell, row){
          return '<i class="glyphicon glyphicon-usd"></i> ' + cell;
        };

function dateFormatter(cell, row){
          return moment(cell).format('DD MMM YYYY');
        };

var formatters = {price: priceFormatter,
                  date: dateFormatter
                  };

module.exports = formatters;