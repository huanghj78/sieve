import axios from 'axios'

export function getLaboratory() {
  return axios.get('/Laboratory')
}

export function createLaboratory(form) {
  console.log(form.name)
  return axios.post("/Laboratory", {
    'name': form.name,
    'apiserver_cnt': form.apiServerNum,
    'worker_cnt': form.workerNum,
    'target': form.target,
    'workflow': form.workflow
  })
}


export function getAPIServerName(labName) {
  console.log(labName)
  return axios({
    method: "get",
    url: "/APIServer",
    params: { lab_name: labName }
  })
}