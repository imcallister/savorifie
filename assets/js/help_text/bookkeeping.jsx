var React = require('react')

module.exports = React.createClass({
    render: function(){
       return <div>
        <h3>Payables and Receivables YO</h3>
        <p>
            Payables and receivables shows net money owed to or from a counterparty.
             There may be a combination of money due to and from ... e.g. for Shopify there are monthly charges for which expenses must be created and receivables which correspond to the proceeds from sales (after Shopify fees).
        </p>
        <h3>Payables</h3>
        <p>
            Bank payments are loaded first and so most often we have an outgoing cash payment without the matching expense. This will show up as a negative amount here. When there are no more payables showing here then it is a sign that all necessary expenses have been created.
            
            Choosing checkbox and clicking bulk create will create expenses for that counterparty. It will not create duplicates. But we do not create expenses for all counterparties. Positive amounts show that we have net receivables. This should be the minority. The difficult ones normally require some accounting expertise so contact Ian for any that are unclear.
        </p>

        <h3>Receivables</h3>
        <p>
            This will mostly show money due from channels. Clicking on the link will show the history with that channel.
            
            There are no book-keeping entries required -- this report is for help in tracking outstanding amounts owed to Shopify. Bank activity needs to be up to date in order to track this.

        </p>
      </div>
   }
})