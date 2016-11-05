var React = require('react');
var SwatchPanel = require('./swatchPanel');  



class SwatchRow extends React.Component {

    render() {
      
      var getSwatch = function(cfg) {
          return (
            <div className={"col-md-2"}>
              <SwatchPanel color={cfg.color} bigText={this.props.counts[cfg.item] || 0} smallText={cfg.item}/>
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
