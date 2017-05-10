import { combineReducers } from 'redux';
import { routerReducer } from 'react-router-redux';
import authReducer from './auth';
import cpartyReducer from './cparty';
import incompleteSalesReducer from './incompletesales';

export default combineReducers({
    auth: authReducer,
    routing: routerReducer,
    cparty: cpartyReducer,
    incompletesales: incompleteSalesReducer
});

