var moment = require('moment')

function priceFormatter(cell, row){
          return '<i class="glyphicon glyphicon-usd"></i> ' + cell;
        };

function dateFormatter(cell, row){
          return moment(cell).format('DD MMM YYYY');
        };

function drillFormatter(cell, row) {
        if (cell.text == 0) {
            return '-';
        } else {
            return '<a href=' + cell.link + '>' + Number(Math.round(cell.text)).toLocaleString('us') + '</a>';
        }
    }



var formatters = {price: priceFormatter,
                  date: dateFormatter,
                  drill: drillFormatter
                  };

module.exports = formatters;