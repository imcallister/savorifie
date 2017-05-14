var React = require('react');
var SwatchPanel = require('./swatchPanel');  



class SwatchRow extends React.Component {

    render() {
      var getSwatch = function(sw) {
          return (
            <div className={"col-md-4"}>
              <SwatchPanel color={sw.color} bigText={sw.label || 0} smallText={sw.amount}/>
            </div>
            )
      }.bind(this);

      if (this.props.loaded) {
        return (
            <div className={"row"}>
              {this.props.swatches.map(getSwatch)}
            </div>
        )
      }
      else {
        return null;
      }
    }
}

module.exports = SwatchRow;
