<template>
  <div class="page">
    <div class="card">
      <div class="brand">
        <span class="brand-icon">🎓</span>
        <span class="brand-name">PlaceIt</span>
      </div>
      <h2>Create account</h2>
      <p class="sub">Fill in your details to get started</p>

      <div class="field">
        <label>Username</label>
        <input v-model="username" type="text" placeholder="Enter username" />
      </div>
      <div class="field">
        <label>Password</label>
        <input v-model="password" type="password" placeholder="Enter password" />
      </div>
      <div class="field">
        <label>Role</label>
        <select v-model="role">
          <option value="student">Student</option>
          <option value="company">Company</option>
        </select>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <p v-if="success" class="success-msg">{{ success }}</p>

      <button class="btn-primary" @click="register" :disabled="loading">
        {{ loading ? 'Registering...' : 'Create Account' }}
      </button>

      <p class="footer-text">
        Already have an account? <span @click="$router.push('/')">Sign In</span>
      </p>
    </div>
  </div>
</template>

<script>
import api from "../api.js"
export default {
  name: "Register",
  data() { return { username: "", password: "", role: "student", error: "", success: "", loading: false } },
  methods: {
    async register() {
      this.error = ""; this.success = ""
      if (!this.username || !this.password) { this.error = "Please fill all fields"; return }
      this.loading = true
      try {
        const res = await api.post("/auth/register", {
          username: this.username, password: this.password, role: this.role,
          ...(this.role === 'admin' && { admin_secret_key: this.secretKey })
        })
        this.success = res.data.message || "Registered successfully!"
        setTimeout(() => this.$router.push("/"), 1500)
      } catch (err) {
        this.error = err.response?.data?.message || "Server error"
      } finally { this.loading = false }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #63fe4f, #00f2fe);
  font-family: 'Sora', sans-serif;
  padding: 20px;
}

.card {
  background: white;
  border-radius: 24px;
  padding: 44px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 28px;
}
.brand-icon { font-size: 26px; }
.brand-name { font-size: 22px; font-weight: 700; color: #0f172a; }

h2 { font-size: 24px; font-weight: 700; color: #0f172a; text-align: center; margin-bottom: 6px; }
.sub { font-size: 14px; color: #94a3b8; text-align: center; margin-bottom: 28px; }

.field { margin-bottom: 18px; }
.field label { display: block; font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 7px; }
.field input, .field select {
  width: 100%; padding: 12px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  font-family: 'Sora', sans-serif;
  outline: none;
  transition: border 0.2s;
  color: #0f172a;
  background: white;
}
.field input:focus, .field select:focus { border-color: #00c6a7; box-shadow: 0 0 0 3px rgba(0,242,254,0.15); }

.btn-primary {
  width: 100%; padding: 13px;
  background: linear-gradient(135deg, #63fe4f, #00f2fe);
  color: #0f172a;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  font-family: 'Sora', sans-serif;
  margin-top: 6px;
  transition: opacity 0.2s, transform 0.1s;
  box-shadow: 0 4px 15px rgba(0,242,254,0.4);
}
.btn-primary:hover { opacity: 0.92; transform: translateY(-1px); }
.btn-primary:active { transform: translateY(0); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.error-msg { color: #ef4444; font-size: 13px; margin-bottom: 12px; text-align: center; }
.success-msg { color: #16a34a; font-size: 13px; margin-bottom: 12px; text-align: center; }

.footer-text { text-align: center; margin-top: 22px; font-size: 13px; color: #94a3b8; }
.footer-text span { color: #00a896; cursor: pointer; font-weight: 700; }
.footer-text span:hover { text-decoration: underline; }
</style>