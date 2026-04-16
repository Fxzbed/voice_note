<template>
  <div class="page">
    <el-card>
      <h2>任务列表</h2>
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="120" />
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="status" label="状态" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";

const tasks = ref([
  { id: 1, name: "test.mp3", status: "uploaded" },
]);
</script>

<style scoped>
.page {
  padding: 40px;
}
</style>