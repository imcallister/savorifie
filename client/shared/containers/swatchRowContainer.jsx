var React = require('react');
var SwatchRow = require('../components/swatchRow');  

const getSwatch = (sw, config) => {
    sw.color = config[sw.fld];

    return sw;
    };


class SwatchRowContainer extends React.Component {

    constructor() {
      super();
      this.state = {loaded: false, counts: {}};
    }


    componentDidMount() {
      this.serverRequest = $.get(this.props.source, function (result) {
        this.setState({
          swatches: result.map(s => getSwatch(s, this.props.config)),
          loaded: true
        });
      }.bind(this));
    }


    render() {
      return (
          <SwatchRow loaded={this.state.loaded} 
                     swatches={this.state.swatches}
                     />
      );
    }
}

module.exports = SwatchRowContainer;
