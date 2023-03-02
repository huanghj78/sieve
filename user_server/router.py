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

@router.route("/Target",  methods=['GET'])
def get_target():
    return target.get_target()

@router.route("/Workflow",  methods=['GET'])
def get_workflow():
    return workflow.get_workflow()

