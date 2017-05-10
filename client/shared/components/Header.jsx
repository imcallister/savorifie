import React, { PropTypes, Component } from 'react';
import { connect } from 'react-redux';
import TodoTextInput from './TodoTextInput';

class Header extends Component {
  static propTypes = {
    addTodo: PropTypes.func.isRequired
  };

  handleSave(text) {
    if (text.length !== 0) {
      const token = this.props.token;
      this.props.addTodo(token, text);
    }
  }

  render() {
    return (
      <header className='header'>
          <h1>todos</h1>
          <TodoTextInput newTodo={true}
                         onSave={::this.handleSave}
                         placeholder='HEY What needs to be done?' />
      </header>
    );
  }
}

const mapStateToProps = (state) => {
    return {
        todos: state.data.data,
        isFetching: state.data.isFetching,
        token: state.auth.token
    };
};

export default connect(mapStateToProps)(Header);
export { Header as HeaderNotConnected };

