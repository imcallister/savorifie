import fetch from 'isomorphic-fetch';
import { push } from 'react-router-redux';

import { SERVER_URL } from '../utils/config';
import { getCookie } from '../utils/cookie'
import { checkHttpStatus, parseJSON } from '../utils';

import { RECEIVE_INCOMPLETESALE_DATA, FETCH_INCOMPLETESALE_DATA, SEND_INCOMPLETESALE_UPDATE, RECEIVE_INCOMPLETESALE_UPDATE_RESPONSE } from '../constants';
import { authLoginUserFailure } from './auth';


export function receiveIncompleteSaleData(data) {
    return {
        type: RECEIVE_INCOMPLETESALE_DATA,
        payload: {
            data
        }
    };
}

export function fetchIncompleteSaleData() {
    return {
        type: FETCH_INCOMPLETESALE_DATA
    };
}


export function sendIncompleteSaleUpdate(id, data) {
    return {
        type: SEND_INCOMPLETESALE_UPDATE,
        payload: {
            data
        }
    };
}

export function receiveIncompleteSaleUpdateResponse(id) {
    return {
        type: RECEIVE_INCOMPLETESALE_UPDATE_RESPONSE,
        payload: {
            id
        }
    };
}


export function patchIncompleteSales(token, id, data) {
    return (dispatch, state) => {
        dispatch(sendIncompleteSaleUpdate());
        dispatch(receiveIncompleteSaleUpdateResponse(id));        
    };
}


export function getIncompleteSales(token) {
    return (dispatch, state) => {
        dispatch(fetchIncompleteSaleData());
        return fetch(`${SERVER_URL}/api/sales/sale/?raw=true&incomplete=true`, {
            credentials: 'include',
            mode: 'no-cors',
            headers: {
                Accept: 'application/json',
                Authorization: `Token ${token}`
            }
        })
            .then(checkHttpStatus)
            .then(parseJSON)
            .then((response) => {
                dispatch(receiveIncompleteSaleData(response));
            })
            .catch((error) => {
                if (error && typeof error.response !== 'undefined' && error.response.status === 401) {
                    // Invalid authentication credentials
                    return error.response.json().then((data) => {
                        dispatch(authLoginUserFailure(401, data.non_field_errors[0]));
                        dispatch(push('/login'));
                    });
                } else if (error && typeof error.response !== 'undefined' && error.response.status >= 500) {
                    // Server side error
                    dispatch(authLoginUserFailure(500, 'A server error occurred while sending your data!'));
                } else {
                    // Most likely connection issues
                    dispatch(authLoginUserFailure('Connection Error', 'An error occurred while sending your data!'));
                }
                dispatch(push('/login'));
                return Promise.resolve(); // TODO: we need a promise here because of the tests, find a better way
            });
    };
}
