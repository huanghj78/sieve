import axios from 'axios'

export function getTarget() {
    return axios.get('/Target')
}

export function createTarget() {
    console.log(form)
    return axios.post("/Target", {
        'username': username,
        'form': form._rawValue,
    })
}
