<template>
  <el-button type="primary" class="button" @click="dialogVisible = true">Create Laboratory</el-button>
  <el-dialog v-model="dialogVisible" title="Laboratory info">
    <el-form :model="form" label-width="120px">
      <el-form-item label="Laboratory Name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="API Server Count">
        <el-input-number v-model="form.apiServerNum" :min="1" :max="10" />
      </el-form-item>
      <el-form-item label="Worker Count">
        <el-input-number v-model="form.workerNum" :min="1" :max="10" />
      </el-form-item>
      <el-form-item label="Target">
        <el-select v-model="form.target" class="m-2" placeholder="Select" size="large">
          <el-option v-for="target in targets"
            :key="target"
           :label="target"
           :value="target"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="Workflow">
        <el-select v-model="form.workflow" class="m-2" placeholder="Select" size="large">
          <el-option v-for="workflow in workflows"
            :key="workflow"
           :label="workflow"
           :value="workflow"
          />
        </el-select>
      </el-form-item>
      <el-row justify="center">
        <el-button class="button" type="primary" @click="onSubmit">Create</el-button>
      </el-row>
    </el-form>
  </el-dialog>
  <div class="markup-tables flex">
    <va-card class="flex mb-4" v-for="lab in labs" :key="lab.name">
      <va-card-title>{{ lab.name }}</va-card-title>
      <va-card-content>
        <div class="table-wrapper">
          <table class="va-table">
            <thead>
              <tr>
                <th>{{ t('node name') }}</th>
                <th>{{ t('create at') }}</th>
                <th>{{ t('status') }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="node in lab.nodes" :key="node.name">
                <td>{{ node.name }}</td>
                <td>{{ node.created_at }}</td>
                <td>
                  <va-badge :text="node.status" :color="getStatusColor()" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </va-card-content>
    </va-card>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import data from '../../../data/lab/data.json'
  import { reactive } from 'vue'
  import {getLaboratory, createLaboratory} from '../../../api/laboratory.js'
  import {getTarget} from '../../../api/target.js'
  import {getWorkflow} from '../../../api/workflow.js'
  const { t } = useI18n()

  const labs = ref(data.slice(0, 8))

  let dialogVisible = ref(false)
  let targets = ''
  let workflows = ''
  const form = reactive({
    name: '',
    apiServerNum: 1,
    workerNum: 1,
    target: '',
    workflow: '',
  })

  onMounted(async () => {
    await getTarget()
      .then(res => {
        targets = res
      })
      .catch(err => {
        console.log(err)
      })

    await getWorkflow()
      .then(res => {
        workflows = res
      })
      .catch(err => {
        console.log(err)
      })
  })

  function getStatusColor() {
    return 'success'
  }

  function onSubmit() {
    createLaboratory(form)
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

  .button {
    margin: 10px;
  }
</style>
