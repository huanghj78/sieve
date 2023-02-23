import axios from 'axios'

export function getLaboratory() {
  return axios.get('/Laboratory')
}
