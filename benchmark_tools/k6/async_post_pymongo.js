import http from 'k6/http';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

export let options = {
    vus: 30,
    duration: '10s', // '8min'
    discardResponseBodies: true, // Discard response bodies to save memory
};

export default function () {
  const data = {user_id: randomIntBetween(1, 5000)};
  http.post('http://0.0.0.0/async/pymongo', JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' },
  });
}
