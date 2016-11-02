var React = require('react');

var HighChart = require('../components/highchartCmpnt');  


class HChartContainer extends React.Component {

    constructor() {
      super();
      this.state = { data: [28, 12.2, 11.4, 8.4, 6.9, 5.8, 5.2, 3.0, 2.6, 2.2, 1.9, 1.8, 1.6, 1.5, 1.4, 1.2, 0.1, 0.1],
                     occupation: ["Full-Stack Web Developer", "Back-End Web Developer", "Student", "Mobile Developer (Android, iOS, WP, and MultiPlatform)", "Desktop Develop", "Front-End Web Developer", "Other", "Enterprise Level Services Developer", "Embedded Application Developer", "DevOps", "Developer with a Statistics or Mathematics Background", "Executive (VP of Engineering, CTO, CIO, etc.)", "Data Scientist", "System Administrator", "Engineering Manager", "Analyst", "Business Intelligence or Data WWarehousing Expert", "Maching Learning Developer"]};
    }

    
    reverseOrder(event) {
      event.preventDefault();
      this.setState({data: this.state.data.reverse(), occupation: this.state.occupation.reverse()});
    }

    
    render() {
      return (
          <HighChart data={this.state.data} occupation={this.state.occupation} />
      )
    }
}

module.exports = HChartContainer;
