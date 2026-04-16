<template>
  <div class="page">
    <el-card class="card">
      <h2>上传音频</h2>

      <el-upload
        :auto-upload="false"
        :limit="1"
        :on-change="handleChange"
        :show-file-list="true"
      >
        <el-button type="primary">选择文件</el-button>
      </el-upload>

      <div style="margin-top: 16px">
        <el-button type="success" @click="handleUpload">上传</el-button>
      </div>

      <div v-if="taskId" style="margin-top: 16px">
        <p>Go任务ID：{{ taskId }}</p>
        <el-button type="warning" @click="handleCreatePythonTask">
          创建 Python 任务
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";

const selectedFile = ref(null);
const taskId = ref(null);

const handleChange = (file) => {
  selectedFile.value = file.raw;
};

const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning("请先选择文件");
    return;
  }

  // 这里后面接你的 /api/upload
  taskId.value = 1;
  ElMessage.success("上传页骨架已完成");
};

const handleCreatePythonTask = async () => {
  if (!taskId.value) {
    ElMessage.warning("请先上传文件");
    return;
  }

  // 这里后面接你的 /api/python/tasks
  ElMessage.success("Python任务创建按钮已完成");
};
</script>

<style scoped>
.page {
  padding: 40px;
}
.card {
  max-width: 720px;
  margin: 0 auto;
}
</style>