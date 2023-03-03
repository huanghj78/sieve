<template>
  <el-card shadow="hover">
    <template #header>
        <div class="card-header">
            <span class="card-title font-medium font-serif text-xl text-blue-900 text-opacity-85">
                Triggers
            </span>
            <el-button @click="addNewItem">添加Trigger</el-button>
        </div>
    </template>
    <el-form  :model="item" ref="item" :rules="rules" label-width="120px" v-for="(item, index) in form.items" :key="index" :label="`Item ${index + 1}`">
        <el-form-item label="Trigger Name">
          <el-input class="input" v-model="item.name"></el-input>
        </el-form-item>
        <el-form-item label="Condition Type">
            <el-select class="input" v-model="item.conditionType"  size="large">
                <el-option
                v-for="(item, index) in conditionType"
                :key="item"
                :label="item"
                :value="item"
                />
            </el-select>
        </el-form-item>

        <el-form-item label="Resorce Key">
            <el-input class="input" v-model="item.resorceKey"></el-input>
        </el-form-item>

        <el-form-item label="Observed When ">
            <el-select  class="input" v-model="item.observedWhen" size="large">
                <el-option
                v-for="item in observedWhen"
                :key="item"
                :label="item"
                :value="item"
                />
            </el-select>
        </el-form-item>
        
        <el-form-item label="Observed By">
            <el-input class="input" v-model="item.observedBy"></el-input>
        </el-form-item>

        <el-divider />
    </el-form>
    <el-button type="primary" @click="expression = expression + '|'" >或</el-button>
    <el-button type="primary" @click="expression = expression + '&'">与</el-button>
    <el-button type="success" v-for="item in form.items" @click="expression = expression + item.name">{{item.name}}</el-button>
    <el-divider direction="vertical" border-style="dashed" />
    <el-input class="input" v-model="expression"></el-input>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue';

const conditionType = [
    'onObjectCreate',
    'onObjectDelete',
    'onObjectUpdate',
    'onAnyFieldModification',
    'onTimeout',
    'onAnnotatedAPICall',
]

const observedWhen = [
    'beforeAPIServerRecv',
    'afterAPIServerRecv',
    'beforeControllerRecv',
    'afterControllerRecv',
    'beforeControllerWrite',
    'afterControllerWrite',
    'beforeControllerRead',
    'afterControllerRead',
    'beforeAnnotatedAPICall',
    'afterAnnotatedAPICall',
]

const form = reactive({
    items: [
    { name: '' ,
        conditionType: '',
        resorceKey: '',
        observedWhen: '',
        observedBy: ''
    },
    ],
});

const expression = ref('')

const addNewItem = () => {
    console.log("!!!")
    form.items.push({ name: '' ,
        conditionType: '',
        resorceKey: '',
        observedWhen: '',
        observedBy: ''
    });
};

const rules = {
    items: [
    { required: true, type: 'array', min: 1, message: '请至少添加一项' },
    {
        validator: (rule, value, callback) => {
        const isValid = value.every((item) => item.name);
        if (isValid) {
            callback();
        } else {
            callback(new Error('请输入所有项的名称'));
        }
        },
    },
    ],
};

</script>

<style scoped>

.input {
    width: 60%;
}
.paper-list:hover {
    color: #3b82f6;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.el-card :deep(.el-card__header) {
    background-color: #f8fafc;
}

.el-card:hover :deep(.el-card__header) {
    background-color: #f1f5f9;
}

.el-card:hover .card-title {
    --tw-text-opacity: 1;
}

</style>
