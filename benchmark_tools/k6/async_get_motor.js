import http from 'k6/http';

export let options = {
    vus: 30,
    duration: '10s', // '8min'
    discardResponseBodies: true, // Discard response bodies to save memory
  };

export default function () {
  http.get('http://0.0.0.0/async/motor');
}
