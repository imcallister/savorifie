import fetch from 'isomorphic-fetch';
import { push } from 'react-router-redux';

import { SERVER_URL } from '../utils/config';
import { getCookie } from '../utils/cookie'
import { checkHttpStatus, parseJSON } from '../utils';

import { FETCH_CPARTY_DATA, RECEIVE_CPARTY_DATA } from '../constants';
import { authLoginUserFailure } from './auth';


export function receiveCpartyData(data) {
    return {
        type: RECEIVE_CPARTY_DATA,
        payload: {
            data
        }
    };
}

export function fetchCpartyData() {
    return {
        type: FETCH_CPARTY_DATA
    };
}

export function getCounterparties(token) {
    return (dispatch, state) => {

        dispatch(fetchCpartyData());
        return fetch(`${SERVER_URL}/api/gl/counterparty/?raw=true`, {
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
                dispatch(receiveCpartyData(response));
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
