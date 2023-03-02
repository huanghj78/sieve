import axios from 'axios'

export function getWorkflow() {
    return axios.get('/Workflow')
}

export function createTarget(form) {
    console.log(form)
    return axios.post("/Workflow", {
        'username': username,
        'form': form._rawValue,
    })
}
