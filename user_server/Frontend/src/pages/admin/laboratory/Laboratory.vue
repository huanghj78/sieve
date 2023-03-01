<template>
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
  import { ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import data from '../../../data/lab/data.json'

  const { t } = useI18n()

  const labs = ref(data.slice(0, 8))

  function getStatusColor() {
    return 'success'
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
</style>
