import { createReducer } from '../utils';
import { RECEIVE_INCOMPLETESALE_DATA, FETCH_INCOMPLETESALE_DATA, SEND_INCOMPLETESALE_UPDATE, RECEIVE_INCOMPLETESALE_UPDATE_RESPONSE } from '../constants';

const initialState = {
    data: [],
    isFetchingIncompleteSales: false,
    isFetchingIncompleteSales: false
};

export default createReducer(initialState, {
    [RECEIVE_INCOMPLETESALE_DATA]: (state, payload) => {
        return Object.assign({}, state, {
            data: payload.data,
            isFetchingIncompleteSales: false
        });
    },
    [FETCH_INCOMPLETESALE_DATA]: (state, payload) => {
        return Object.assign({}, state, {
            isFetchingIncompleteSales: true
        });
    },
    [SEND_INCOMPLETESALE_UPDATE]: (state, payload) => {
        return Object.assign({}, state, {
            isPatchingIncompleteSales: true
        });
    },
    [RECEIVE_INCOMPLETESALE_UPDATE_RESPONSE]: (state, payload) => {
        return Object.assign({}, state, {
            data: state.data.filter(s => s.id != payload.id),
            isPatchingIncompleteSales: false
        });
    }
});
