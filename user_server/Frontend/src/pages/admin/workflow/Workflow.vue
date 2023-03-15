<template>
  <el-button type="primary" class="button" @click="createDialogVisible=true">Create Workflow</el-button>
  <div class="markup-tables flex">
  <va-card class="flex mb-4" >
    <va-card-title>Workflow</va-card-title>
    <va-card-content>
      <div class="table-wrapper">
        <table class="va-table">
          <thead>
            <tr>
              <th>{{ t('workflow') }}</th>
              <th>{{ t('lab name') }}</th>
              <th>{{ t('create at') }}</th>
              <th>{{ t('actions') }}</th>
              <th>{{ t('detail') }}</th>
              <th>{{ t('operation') }}</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="workflow in workflows.list" :key="workflow['name']">
              <td>{{ workflow['name'] }}</td>
              <td>{{ workflow['lab_name'] }}</td>
              <td>{{ workflow['created_at'] }}</td>
              <td>{{ workflow['actions'] }}</td>
              <td>
                <el-button type="primary" @click="getWorkflowDetail(workflow['lab_name'], workflow['name'])">Detail</el-button>
              </td>
              <td>
                <el-button type="success" @click="_runWorkflow(workflow['lab_name'], workflow['name'])">Run</el-button>
                <el-button type="danger" @click="_deleteWorkflow(workflow['lab_name'], workflow['name'])">Delete</el-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </va-card-content>
  </va-card>
  </div>
  <el-dialog v-model="detailDialogVisible" title="Workflow Detail">
    <pre>
      <code><highlightjs language="json" :autodetect="false" :code="code"></highlightjs></code>
    </pre>
    
  </el-dialog>
  <el-dialog v-model="runDialogVisible" title="Run Workflow">

  </el-dialog>
  <el-dialog v-model="createDialogVisible" title="Create Workflow">
    <el-form :model="form" label-width="100px">
      <el-form-item label="Name">
        <el-input v-model="form.name"></el-input>
      </el-form-item>
      <el-form-item label="Workload">
        <el-input v-model="form.workload"></el-input>
      </el-form-item>
      <el-form-item label="Lab Name">
        <el-select @change="changeAPIServerName()" class="input" v-model="form.labName"  size="large">
            <el-option
            v-for="(item, index) in labs.list"
            :key="item['name']"
            :label="item['name']"
            :value="item['name']"
            />
        </el-select>
      </el-form-item>
      <el-form-item label="Target">
        <el-select class="input" v-model="form.target"  size="large">
              <el-option
              v-for="(item, index) in targets.list"
              :key="item"
              :label="item"
              :value="item"
              />
          </el-select>
      </el-form-item>
      <Plans :apiserver="apiserver.list" :planForm="planForm"></Plans>
      <el-form-item>
        <el-button class="createButton" @click="create">Create</el-button>
      </el-form-item>
    </el-form>
  

  </el-dialog>

</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n'
  import vkbeautify from 'vkbeautify'
  import Triggers from './components/Triggers.vue'
  import Plans from './components/Plans.vue'
  import {getTarget} from '../../../api/target.js'
  import {getWorkflow, getDetail, createWorkflow, deleteWorkflow, runWorkflow} from '../../../api/workflow.js'
  import {getLaboratory, createLaboratory, getAPIServerName} from '../../../api/laboratory.js'
  import {onMounted, ref, reactive} from 'vue'
  
  
  const { t } = useI18n()
  const form = reactive({
    name: '',
    workload: '',
    labName: '' ,
    target: ''
  });

  const planForm = reactive({
      items: [
          { actionType: '' ,
              actionArgs: ['', '', '', ''],
              triggerForm: {
                items: [
                { name: '' ,
                    conditionType: '',
                    resourceKey: '',
                    observedWhen: '',
                    observedBy: ''
                },
                ],
                expression: '',
                immediately: false
            }
          },
      ],
  });

  // const triggerForm = reactive({
  //     items: [
  //     { name: '' ,
  //         conditionType: '',
  //         resourceKey: '',
  //         observedWhen: '',
  //         observedBy: ''
  //     },
  //     ]
  // });

  let createDialogVisible = ref(false)
  let runDialogVisible = ref(false)
  let detailDialogVisible = ref(false)
  let code = ref('')

  let workflows = reactive({
    list: []
  })

  let labs = reactive({
    list: []
  })

  let targets = reactive({
    list: []
  })

  let apiserver = reactive({
    list: []
  })

  onMounted(async () => {
    await getLaboratory()
      .then(res => {
        labs.list = res.data
      })
      .catch(err => {
        console.log(err)
      })

    await getTarget()
      .then(res => {
        targets.list = res.data
      })
      .catch(err => {
        console.log(err)
      })

    await getWorkflow()
    .then(res => {
      workflows.list = res.data
    })
    .catch(err => {
      console.log(err)
    })
  })

  async function getWorkflowDetail(labName: string, name: string) {
    detailDialogVisible.value = true
    await getDetail(labName, name)
    .then(res => {
        console.log(res.data)
        code.value = vkbeautify.json(JSON.stringify(res.data))
    })
    .catch(err => {
      console.log(err)
    })
  }

  async function create() {
    await createWorkflow(form, planForm)
    .then(res => {
      console.log(res)
    })
    .catch(err => {
      console.log(err)
    })

    await getWorkflow()
    .then(res => {
      workflows.list = res.data
    })
    .catch(err => {
      console.log(err)
    })

    createDialogVisible.value = false
  }

  async function changeAPIServerName() {
    await getAPIServerName(form.labName)
    .then(res => {
      apiserver.list = res.data
      console.log(apiserver.list)
    })
    .catch(err => {
      console.log(err)
    })
  }

  async function _runWorkflow(labName: string, workflow: string) {
    await runWorkflow(labName, workflow)
    .then(res => {
      console.log(res.data)
    })
    .catch(err => {
      console.log(err)
    })
  }

  async function _deleteWorkflow(labName: string, workflow: string) {
    await deleteWorkflow(labName, workflow)
    .then(res => {
      console.log(res.data)
    })
    .catch(err => {
      console.log(err)
    })

    await getWorkflow()
    .then(res => {
      workflows.list = res.data
    })
    .catch(err => {
      console.log(err)
    })
    
  }
</script>
<style lang="scss">
.markup-tables {
    .table-wrapper {
      overflow: auto;
    }

    .va-table {
      width: 100%;
    }
  }

.createButton {
  left: 50%;
}
</style>
