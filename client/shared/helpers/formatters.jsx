import React from 'react';
var moment = require('moment')
import { Link } from 'react-router';

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
            var text = Number(Math.round(cell.text)).toLocaleString('us');
            return <Link to={cell.link} > {Number(Math.round(cell.text)).toLocaleString('us')} </Link>;
        }
    }

function numberFormatter(cell, row) {
          return Number(Math.round(cell)).toLocaleString('us');
    }


var formatters = {price: priceFormatter,
                  date: dateFormatter,
                  drill: drillFormatter,
                  number: numberFormatter
                  };

module.exports = formatters;