<template>
  <div class="page">
    <el-card class="card">
      <h2>登录</h2>
      <el-form :model="form" @submit.prevent>
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button type="primary" @click="handleLogin">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const handleLogin = async () => {
  try {
    // 这里后面接你的 /api/login
    ElMessage.success("登录页骨架已完成");
    router.push("/upload");
  } catch (err) {
    ElMessage.error("登录失败");
  }
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
.card {
  width: 420px;
}
</style>