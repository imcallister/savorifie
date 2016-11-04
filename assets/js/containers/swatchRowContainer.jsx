var React = require('react');
var SwatchRow = require('../components/swatchRow');  



class SwatchRowContainer extends React.Component {

    constructor() {
      super();
      this.state = {loaded: false, counts: {}};
    }


    componentDidMount() {
      this.serverRequest = $.get(this.props.source, function (result) {
        this.setState({
          counts: result,
          loaded: true
        });
      }.bind(this));
    }


    render() {
      return (
          <SwatchRow loaded={this.state.loaded} counts={this.state.counts} swatches={this.props.swatches}/>
      );
    }
}

module.exports = SwatchRowContainer;
