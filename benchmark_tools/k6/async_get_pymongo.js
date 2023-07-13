import http from 'k6/http';

export let options = {
    vus: 10,
    duration: '5s',
    discardResponseBodies: true, // Discard response bodies to save memory
  };

export default function () {
  http.get('http://0.0.0.0/async/pymongo');
}
