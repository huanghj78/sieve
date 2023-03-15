from flask import Flask, request
from flask import render_template
from handler import lab, target, workflow
router = Flask(__name__, template_folder="./Frontend/dist",
               static_folder="./Frontend/dist", static_url_path="")


@router.route("/")
def index():
    return render_template("index.html")


@router.route("/helloWorld")
def helloWorld():
    return "hello world"


@router.route("/Laboratory",  methods=['GET'])
def get_lab():
    return lab.get_lab()


@router.route("/Laboratory",  methods=['POST'])
def create_lab():
    data = request.get_json()
    return lab.create_lab(data['name'], data['apiserver_cnt'], data['worker_cnt'], data['target'], data['workflow'])

@router.route("/APIServer",  methods=['GET'])
def get_apiserver():
    lab_name = request.args.get('lab_name')
    return lab.get_apiserver(lab_name)

@router.route("/Target",  methods=['GET'])
def get_target():
    return target.get_target()

@router.route("/Workflow/all",  methods=['GET'])
def get_all_workflow():
    return workflow.get_all_workflow()

@router.route("/Workflow",  methods=['GET'])
def get_workflow():
    lab_name = request.args.get('lab_name')
    workflow_name = request.args.get('workflow')
    return workflow.get_workflow(lab_name, workflow_name)

@router.route("/Workflow/new",  methods=['POST'])
def create_workflow():
    data = request.get_json()
    return workflow.create_workflow(data['workflow_form'], data['plan_form'])

@router.route("/Workflow/run",  methods=['POST'])
def run_workflow():
    data = request.get_json()
    return workflow.run_workflow(data['lab_name'], data['workflow'])

@router.route("/Workflow/delete",  methods=['POST'])
def delete_workflow():
    data = request.get_json()
    return workflow.delete_workflow(data['lab_name'], data['workflow'])
