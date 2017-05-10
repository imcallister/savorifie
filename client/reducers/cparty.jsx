import { createReducer } from '../utils';
import { RECEIVE_CPARTY_DATA, FETCH_CPARTY_DATA } from '../constants';

const initialState = {
    data: [],
    isFetchingCparty: false
};

export default createReducer(initialState, {
    [RECEIVE_CPARTY_DATA]: (state, payload) => {
        return Object.assign({}, state, {
            data: payload.data,
            isFetchingCparty: false
        });
    },
    [FETCH_CPARTY_DATA]: (state, payload) => {
        return Object.assign({}, state, {
            isFetchingCparty: true
        });
    }
});
