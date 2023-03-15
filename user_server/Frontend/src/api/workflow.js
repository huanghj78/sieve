import axios from 'axios'

export function getWorkflow() {
    return axios.get('/Workflow/all')
}

export function getDetail(labName, workflow) {
    return axios({
        method: "get",
        url: "/Workflow",
        params: { lab_name: labName, workflow: workflow }
    })
}

export function createWorkflow(workflowForm, planForm) {
    return axios.post("/Workflow/new", {
        workflow_form: workflowForm,
        plan_form: planForm
    })
}

export function deleteWorkflow(labName, workflow) {
    return axios.post("/Workflow/delete", {
        lab_name: labName,
        workflow: workflow
    })
}

export function runWorkflow(labName, workflow) {
    return axios.post("/Workflow/run", {
        lab_name: labName,
        workflow: workflow
    })
}


