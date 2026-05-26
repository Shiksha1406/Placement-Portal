<template>
  <div class="layout">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🎓</span>
        <span class="brand-name">PlaceIt</span>
      </div>
      <div class="sidebar-user">
        <div class="avatar">{{ username.charAt(0).toUpperCase() }}</div>
        <div>
          <div class="uname">{{ username }}</div>
          <div class="urole">Student</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <button :class="['nav-item', { active: tab === 'drives' }]" @click="tab = 'drives'; selectedDrive = null">
          <span class="nav-icon">💼</span> Available Drives
        </button>
        <button :class="['nav-item', { active: tab === 'history' }]" @click="tab = 'history'">
          <span class="nav-icon">📋</span> My Applications
        </button>
        <button :class="['nav-item', { active: tab === 'profile' }]" @click="tab = 'profile'">
          <span class="nav-icon">👤</span> Edit Profile
        </button>
        <button :class="['nav-item', { active: tab === 'viewprofile' }]" @click="tab = 'viewprofile'">
          <span class="nav-icon">🪪</span> View Profile
        </button>
        <button :class="['nav-item', { active: tab === 'suggest' }]" @click="tab = 'suggest'; fetchSuggestions()">
          <span class="nav-icon">🤖</span> AI Job Matches
        </button>
        <button :class="['nav-item', { active: tab === 'report' }]" @click="tab = 'report'">
          <span class="nav-icon">📄</span> My Report
        </button>
      </nav>
      <button class="nav-item notif-nav" @click="toggleNotifs">
        <span class="nav-icon">🔔</span> Notifications
        <span v-if="unreadCount > 0" class="notif-dot">{{ unreadCount }}</span>
      </button>
      <button class="logout-btn" @click="logout">⎋ Logout</button>
      <!-- Notification Dropdown -->
      <div v-if="showNotifDropdown" class="notif-dropdown">
        <div class="notif-header">🔔 Notifications</div>
        <div v-if="notifications.length === 0" class="notif-empty">No notifications yet.</div>
        <div v-for="n in notifications" :key="n.id"
          :class="['notif-item', { 'notif-unread': !n.is_read }]">
          <div class="notif-msg">{{ n.message }}</div>
          <div class="notif-time">{{ n.created_at }}</div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main">

      <!-- Available Drives -->
      <div v-if="tab === 'drives' && !selectedDrive">
        <div class="page-header">
          <h2>Available Drives</h2>
          <span class="count-badge">{{ drives.length }} open</span>
        </div>
        <p v-if="drives.length === 0" class="empty">No drives available right now.</p>
        <div class="drives-grid">
          <div
            v-for="drive in drives"
            :key="drive.id"
            class="drive-card"
            @click="selectedDrive = drive"
          >
            <div class="dc-top">
              <div>
                <div class="dc-title">{{ drive.job_title }}</div>
                <div class="dc-company">{{ drive.company_name }}</div>
              </div>
              <span v-if="appliedDriveIds.includes(drive.id)" class="applied-tag">Applied</span>
            </div>
            <p class="dc-desc">{{ drive.description }}</p>
            <div class="dc-meta">
              <span v-if="drive.salary">💰 {{ drive.salary }}</span>
              <span v-if="drive.location">📍 {{ drive.location }}</span>
              <span v-if="drive.deadline">⏳ {{ drive.deadline }}</span>
            </div>
            <button class="btn-view" @click.stop="selectedDrive = drive">View Details →</button>
          </div>
        </div>
      </div>

      <!-- Drive Detail -->
      <div v-if="tab === 'drives' && selectedDrive">
        <div class="page-header">
          <button class="btn-back" @click="selectedDrive = null; applyMessage = ''; applyError = ''">← Back</button>
        </div>
        <div class="detail-card">
          <div class="detail-head">
            <div>
              <h2>{{ selectedDrive.job_title }}</h2>
              <div class="detail-company">{{ selectedDrive.company_name }}</div>
            </div>
            <span v-if="appliedDriveIds.includes(selectedDrive.id)" class="applied-tag lg">✓ Applied</span>
          </div>
          <div class="detail-grid">
            <div class="detail-item"><span class="dl">Salary</span><span class="dv">{{ selectedDrive.salary || 'N/A' }}</span></div>
            <div class="detail-item"><span class="dl">Location</span><span class="dv">{{ selectedDrive.location || 'N/A' }}</span></div>
            <div class="detail-item"><span class="dl">Eligibility</span><span class="dv">{{ selectedDrive.eligibility || 'N/A' }}</span></div>
            <div class="detail-item"><span class="dl">Deadline</span><span class="dv">{{ selectedDrive.deadline || 'N/A' }}</span></div>
          </div>
          <div class="detail-desc">
            <span class="dl">Job Description</span>
            <p>{{ selectedDrive.description }}</p>
          </div>
          <p v-if="applyMessage" class="msg-success">{{ applyMessage }}</p>
          <p v-if="applyError" class="msg-error">{{ applyError }}</p>
          <button
            class="btn-apply"
            @click="applyToDrive"
            :disabled="appliedDriveIds.includes(selectedDrive.id)"
          >
            {{ appliedDriveIds.includes(selectedDrive.id) ? '✓ Already Applied' : 'Apply Now' }}
          </button>
        </div>
      </div>

      <!-- My Applications -->
      <div v-if="tab === 'history'">
        <div class="page-header"><h2>My Applications</h2></div>
        <p v-if="applications.length === 0" class="empty">No applications yet.</p>
        <div class="table-wrap" v-else>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Job Title</th>
                <th>Company</th>
                <th>Interview</th>
                <th>Result</th>
                <th>Status</th>
                <th>Remark</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(a, i) in applications" :key="i">
                <td>{{ i + 1 }}</td>
                <td><strong>{{ a.job_title }}</strong></td>
                <td>{{ a.company_name }}</td>
                <td>{{ a.interview_type || '—' }}</td>
                <td>{{ a.result || '—' }}</td>
                <td><span :class="['badge', a.status.toLowerCase()]">{{ a.status }}</span></td>
                <td>{{ a.remark || '—' }}</td>
                <td>
                  <button
                    v-if="a.status === 'Applied'"
                    class="btn-withdraw"
                    @click="withdrawApplication(a.drive_id)">
                    Withdraw
                  </button>
                  <span v-else class="no-action">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- AI Job Matches -->
      <div v-if="tab === 'suggest'">
        <div class="page-header"><h2>🤖 AI Job Matches</h2></div>
        <p class="suggest-sub">Personalised drive recommendations based on your profile and department.</p>

        <div v-if="suggestLoading" class="suggest-loading">
          <div class="spinner"></div> Analysing your profile...
        </div>
        <p v-else-if="suggestError" class="msg-error">{{ suggestError }}</p>
        <div v-else-if="suggestions.length === 0" class="empty">No suggestions yet. Make sure your profile (department, location) is filled in.</div>

        <div v-else class="suggest-list">
          <div v-for="s in suggestions" :key="s.drive_id" class="suggest-card">
            <div class="suggest-header">
              <div class="suggest-info">
                <div class="suggest-title">{{ s.job_title }}</div>
                <div class="suggest-company">{{ s.company }}</div>
              </div>
              <div class="suggest-score-wrap">
                <div class="suggest-score" :style="{ background: scoreColor(s.match_score) }">
                  {{ s.match_score }}%
                </div>
                <div class="suggest-score-label">Match</div>
              </div>
            </div>

            <div class="suggest-meta">
              <span v-if="s.salary">💰 {{ s.salary }}</span>
              <span v-if="s.location">📍 {{ s.location }}</span>
              <span v-if="s.deadline">⏳ {{ s.deadline }}</span>
              <span v-if="s.eligibility">🎓 {{ s.eligibility }}</span>
            </div>

            <div class="suggest-reason">💡 {{ s.reason }}</div>

            <button
              class="btn-apply"
              style="margin-top: 12px; width: auto; padding: 9px 22px;"
              :disabled="appliedDriveIds.includes(s.drive_id)"
              @click="applyFromSuggest(s)">
              {{ appliedDriveIds.includes(s.drive_id) ? '✓ Applied' : 'Apply Now' }}
            </button>
          </div>
        </div>
      </div>


      <!-- Edit Profile -->
      <div v-if="tab === 'profile'">
        <div class="page-header"><h2>Edit Profile</h2></div>
        <div class="profile-grid">
          <div class="card">
            <h3>Personal Info</h3>
            <div class="field">
              <label>Full Name</label>
              <input v-model="profileForm.name" placeholder="Enter your name" />
            </div>
            <div class="field">
              <label>Email</label>
              <input v-model="profileForm.email" placeholder="Enter your Email" />
            </div>
            <div class="field">
              <label>Phone number</label>
              <input v-model="profileForm.phone" placeholder="Enter your Phone Number" />
            </div>
            <div class="field">
              <label>Location</label>
              <input v-model="profileForm.location" placeholder="Enter your Location/Address" />
            </div>
            <div class="field">
              <label>Department</label>
              <input v-model="profileForm.department" placeholder="e.g. Computer Science" />
            </div>
            <div class="field">
              <label>CGPA</label>
              <input v-model.number="profileForm.cgpa" type="number" step="0.1" min="0" max="10" placeholder="e.g. 8.5" />
            </div>
            <div class="field">
              <label>Year</label>
              <input v-model.number="profileForm.year" type="number" min="1" max="4" placeholder="e.g. 3" />
            </div>
            <p v-if="profileMsg" class="msg-success">{{ profileMsg }}</p>
            <button class="btn-primary" @click="saveProfile">Save Changes</button>
          </div>
          <div class="card">
            <h3>Resume</h3>
            <div class="resume-zone">
              <span v-if="resumeUploaded">📄 Resume uploaded</span>
              <span v-else>📂 No resume uploaded yet</span>
            </div>
            <input type="file" accept=".pdf" @change="handleResumeFile" class="file-input" />
            <p v-if="resumeMsg" class="msg-success">{{ resumeMsg }}</p>
            <button class="btn-primary" @click="uploadResume">Upload Resume</button>
          </div>
        </div>
      </div>

      <!-- My Placement Report -->
      <div v-if="tab === 'report'">
        <div class="page-header"><h2>📄 My Placement Report</h2></div>
        <p class="suggest-sub">A summary of all your job applications and their outcomes.</p>

        <div v-if="applications.length === 0" class="empty">No applications yet. Apply to some drives first!</div>
        <div v-else>

          <!-- Summary Cards -->
          <div class="rep-cards">
            <div class="rep-card rep-blue">
              <div class="rep-val">{{ reportStats.total }}</div>
              <div class="rep-label">Total Applied</div>
            </div>
            <div class="rep-card rep-yellow">
              <div class="rep-val">{{ reportStats.shortlisted }}</div>
              <div class="rep-label">Shortlisted</div>
            </div>
            <!-- <div class="rep-card rep-sky">
              <div class="rep-val">{{ reportStats.waitlisted }}</div>
              <div class="rep-label">Waitlisted</div>
            </div> -->
            <div class="rep-card rep-green">
              <div class="rep-val">{{ reportStats.selected }}</div>
              <div class="rep-label">Passed</div>
            </div>
            <div class="rep-card rep-red">
              <div class="rep-val">{{ reportStats.rejected }}</div>
              <div class="rep-label">Rejected</div>
            </div>
            <div class="rep-card rep-grey">
              <div class="rep-val">{{ reportStats.rate }}%</div>
              <div class="rep-label">Selection Rate</div>
            </div>
          </div>

          <!-- Application Breakdown Table -->
          <div class="section-label" style="margin-top: 28px; margin-bottom: 14px;">Application Breakdown</div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Interview Details</th>
                  <th>Result</th>
                  <th>Remark</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(a, i) in applications" :key="i">
                  <td>{{ i + 1 }}</td>
                  <td><strong>{{ a.job_title }}</strong></td>
                  <td>{{ a.company_name }}</td>
                  <!-- <td>{{ a.interview_type || '—' }}</td> -->
                   <td>
                    <div v-if="a.interview_type">
                      <div><strong>{{ a.interview_type }}</strong></div>
                      <div v-if="a.interview_date" style="font-size:12px; color:#64748b; margin-top:3px;">
                        📅 {{ a.interview_date }}
                      </div>
                      <div v-if="a.interview_link" style="font-size:12px; color:#0ea5e9; margin-top:2px;">
                        🔗 {{ a.interview_link }}
                      </div>
                      <div v-if="a.interview_notes" style="font-size:12px; color:#475569; margin-top:2px;">
                        📝 {{ a.interview_notes }}
                      </div>
                    </div>
                    <span v-else>—</span>
                  </td>
                  <td>{{ a.result || '—' }}</td>
                  <td>{{ a.remark || '—' }}</td>
                  <td><span :class="['badge', a.status.toLowerCase()]">{{ a.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Export CSV button -->
          <button class="btn-rep-export" @click="exportMyReport" style="margin-top: 18px;">
            ⬇ Download CSV
          </button>
        </div>
      </div>

      <!-- View Profile -->
      <div v-if="tab === 'viewprofile'">
        <div class="page-header"><h2>My Profile</h2></div>
        <div class="profile-grid">
          <div class="card">
            <h3>Personal Info</h3>
            <div class="view-field">
              <span class="vf-label">Username</span>
              <span class="vf-value">{{ username }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Full Name</span>
              <span class="vf-value">{{ profileData.name || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Email</span>
              <span class="vf-value">{{ profileData.email || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Phone Number</span>
              <span class="vf-value">{{ profileData.phone || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Location</span>
              <span class="vf-value">{{ profileData.location || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Department</span>
              <span class="vf-value">{{ profileData.department || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">CGPA</span>
              <span class="vf-value">{{ profileData.cgpa || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Year</span>
              <span class="vf-value">{{ profileData.year || '—' }}</span>
            </div>
            <div class="view-field">
              <span class="vf-label">Role</span>
              <span class="vf-value">Student</span>
            </div>
          </div>
          <div class="card">
            <h3>Resume</h3>
            <div class="resume-zone">
              <span v-if="resumeUploaded">📄 Resume uploaded</span>
              <span v-else>📂 No resume uploaded yet</span>
            </div>
            <a
              v-if="resumeUploaded"
              :href="`http://127.0.0.1:5000/students/resume/view/${userId}`"
              target="_blank"
              class="btn-primary"
              style="display:inline-block; margin-bottom:12px; text-decoration:none;"
            >
              View Resume
            </a>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script>
import api from "../api.js"
export default {
  name: "StudentDashboard",
  data() {
    return {
      tab: localStorage.getItem("studentTab") || "drives",  
      username: "",
      userId: null,
      drives: [],
      applications: [],
      appliedDriveIds: [],
      profileData: { name: "", department: "", email: "", phone: "", location: "" ,cgpa: 0, year: 0},
      profileForm: { name: "", department: "", email: "", phone: "", location: "",cgpa: 0, year: 0 },
      profileMsg: "",
      error: "",
      resumeFile: null,
      resumeMsg: "",
      resumeUploaded: false,
      selectedDrive: null,
      applyMessage: "",
      applyError: "",
      suggestions:[],
      suggestLoading:false,
      suggestError:"",
      notifications: [],
      showNotifDropdown: false
    }
  },
  watch: {
    tab(newVal) {
      localStorage.setItem("studentTab", newVal)  
    }
  },
  computed:{
    unreadCount() {
      return this.notifications.filter(n => !n.is_read).length
    },
    reportStats() {
      const total       = this.applications.length
      const shortlisted = this.applications.filter(a => a.status === 'Shortlisted').length
      // const selected    = this.applications.filter(a => a.result === 'Selected').length
      const selected = this.applications.filter(a => a.result === 'Passed').length
      const rejected    = this.applications.filter(a => a.status === 'Rejected').length
      const waitlisted  = this.applications.filter(a => a.status === 'Waitlisted').length
      const pending     = this.applications.filter(a => a.status === 'Applied').length
      const rate        = total > 0 ? Math.round((selected / total) * 100) : 0
      return { total, shortlisted, selected, rejected, waitlisted, pending, rate }
    },
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user"))
    this.username = user?.username || "Student"
    this.userId = user?.id

    this.fetchDrives()
    this.fetchApplications()
    this.fetchProfile()
    this.fetchNotifications()
  },
  methods: {
    handleResumeFile(e) { this.resumeFile = e.target.files[0] },
    async applyToDrive() {
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        await api.post('/students/apply', { drive_id: this.selectedDrive.id, student_id: user.id })
        this.applyMessage = "Application submitted successfully!"
        this.applyError = ""
        this.fetchApplications()
      } catch (err) { this.applyError = err.response?.data?.message || "Failed to apply" }
    },
    async uploadResume() {
      if (!this.resumeFile) { this.resumeMsg = "Please select a PDF file first"; return }
      const user = JSON.parse(localStorage.getItem("user"))
      const formData = new FormData()
      formData.append("resume", this.resumeFile)
      try {
        await api.post(`/students/resume/upload/${user.id}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.resumeMsg = "Resume uploaded!"
        this.resumeUploaded = true
        setTimeout(() => this.resumeMsg = '', 2000)
      } catch (err) { this.resumeMsg = err.response?.data?.message || "Upload failed" }
    },
    async fetchDrives() {
      try { const res = await api.get("/students/drives"); this.drives = res.data }
      catch (err) { this.error = "Failed to load drives" }
    },
    async fetchApplications() {
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        const res = await api.get(`/students/${user.id}/applications`)
        this.applications = res.data
        this.appliedDriveIds = res.data.map(a => a.drive_id)
      } catch (err) {}
    },
    async fetchProfile() {
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        const res = await api.get(`/students/profile/${user.id}`)
        this.profileData = res.data
        this.profileForm = { ...res.data }
        this.resumeUploaded = res.data.resume_uploaded
      } catch (err) {
        console.error("fetchProfile error:", err)
      }
    },
    async saveProfile() {
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        await api.put(`/students/profile/${user.id}`, this.profileForm)
        this.profileMsg = "Profile updated successfully!"
        this.profileData = { ...this.profileForm }
        this.profileForm = { name: "", department: "", email: "", phone: "", location: "",cgpa: 0, year: 0 }
        setTimeout(() => this.profileMsg = '', 2000)
      } catch (err) {
        this.profileMsg = "Failed to update profile"
      }
    },
    async withdrawApplication(driveId) {
      if (!confirm('Withdraw this application?')) return
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        await api.delete('/students/withdraw', { data: { student_id: user.id, drive_id: driveId } })
        this.fetchApplications()
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to withdraw')
      }
    },
    async fetchNotifications() {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        const res = await api.get(`/students/notifications/${user.id}`)
        this.notifications = res.data
      } catch (err) {}
    },
    async toggleNotifs() {
      this.showNotifDropdown = !this.showNotifDropdown
      if (this.showNotifDropdown && this.unreadCount > 0) {
        const user = JSON.parse(localStorage.getItem('user'))
        await api.post('/students/notifications/read', { user_id: user.id })
        this.notifications = this.notifications.map(n => ({ ...n, is_read: true }))
      }
    },
    async fetchSuggestions() {
      this.suggestLoading = true
      this.suggestError = ''
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        const res = await api.get(`/students/suggestions/${user.id}`)
        this.suggestions = res.data
      } catch (err) {
        this.suggestError = err.response?.data?.message || 'Failed to load suggestions'
      } finally {
        this.suggestLoading = false
      }
    },
    async applyFromSuggest(s) {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        await api.post('/students/apply', { drive_id: s.drive_id, student_id: user.id })
        this.appliedDriveIds.push(s.drive_id)
        this.fetchApplications()
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to apply')
      }
    },
    scoreColor(score) {
      if (score >= 75) return '#dcfce7'
      if (score >= 50) return '#fefce8'
      return '#fff1f2'
    },
    exportMyReport() {
      const user = JSON.parse(localStorage.getItem('user'))
      const rows = [
        ['#', 'Job Title', 'Company', 'Interview Type', 'Result', 'Remark', 'Status'],
        ...this.applications.map((a, i) => [
          i + 1, a.job_title, a.company_name,
          a.interview_type || '', a.result || '', a.remark || '', a.status
        ])
      ]
      const csv = rows.map(r => r.map(v => `"${v}"`).join(',')).join('\n')
      const blob = new Blob([csv], { type: 'text/csv' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `${user.username}_placement_report.csv`
      a.click()
      URL.revokeObjectURL(url)
    },
    logout() {
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      localStorage.removeItem("studentTab")  
      this.$router.push("/")
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }

.layout { display: flex; min-height: 100vh; font-family: 'Sora', sans-serif; background: #f1f5f9; }
.sidebar {
  width: 240px; min-height: 100vh; background: linear-gradient(135deg, #63fe4f, #00f2fe);
  display: flex; flex-direction: column; padding: 24px 16px; position: fixed; top: 0; left: 0;
}
.sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 0 8px; margin-bottom: 28px; }
.brand-icon { font-size: 22px; }
.brand-name { font-size: 20px; font-weight: 700; color: #0f172a; }
.sidebar-user { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.08); border-radius: 12px; padding: 12px; margin-bottom: 28px; }
.avatar { width: 36px; height: 36px; background: #0ea5e9; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; font-size: 15px; flex-shrink: 0; }
.uname { font-size: 13px; font-weight: 600; color: #0f172a; }
.urole { font-size: 11px; color: rgba(0,0,0,0.45); text-transform: uppercase; letter-spacing: 0.5px; }
.sidebar-nav { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 11px 14px; border: none; border-radius: 10px; background: transparent; color: rgba(0,0,0,0.75); font-size: 14px; font-family: 'Sora', sans-serif; font-weight: 500; cursor: pointer; text-align: left; transition: all 0.2s; }
.nav-item:hover { background: rgba(0,0,0,0.08); color: #0f172a; }
.nav-item.active { background: white; color: #0ea5e9; }
.nav-icon { font-size: 16px; }
.logout-btn { display: flex; align-items: center; gap: 8px; padding: 11px 14px; border: none; border-radius: 10px; background: rgba(239,68,68,0.2); color: #dc2626; font-size: 14px; font-family: 'Sora', sans-serif; font-weight: 600; cursor: pointer; margin-top: 12px; transition: background 0.2s; }
.logout-btn:hover { background: rgba(239,68,68,0.35); }

.main { margin-left: 240px; flex: 1; padding: 36px; }
.page-header { display: flex; align-items: center; gap: 14px; margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #0f172a; }
.count-badge { background: #e0f2fe; color: #0284c7; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }
.empty { color: #94a3b8; font-size: 14px; margin-top: 16px; }

.drives-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }
.drive-card { background: white; border-radius: 16px; padding: 22px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; gap: 10px; }
.drive-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.dc-top { display: flex; justify-content: space-between; align-items: flex-start; }
.dc-title { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.dc-company { font-size: 13px; color: #0ea5e9; font-weight: 600; }
.dc-desc { font-size: 13px; color: #64748b; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.dc-meta { display: flex; flex-wrap: wrap; gap: 6px; }
.dc-meta span { font-size: 12px; background: #f1f5f9; color: #475569; padding: 3px 9px; border-radius: 20px; }
.applied-tag { background: #dcfce7; color: #16a34a; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px; white-space: nowrap; }
.applied-tag.lg { font-size: 13px; padding: 6px 14px; }
.btn-view { align-self: flex-start; padding: 7px 14px; background: #f0f9ff; color: #0ea5e9; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; margin-top: 4px; }
.btn-view:hover { background: #e0f2fe; }

.detail-card { background: white; border-radius: 20px; padding: 32px; box-shadow: 0 2px 16px rgba(0,0,0,0.07); }
.detail-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.detail-head h2 { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
.detail-company { font-size: 15px; color: #0ea5e9; font-weight: 600; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.detail-item { background: #f8fafc; border-radius: 10px; padding: 12px 16px; }
.dl { display: block; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600; }
.dv { font-size: 14px; color: #1e293b; font-weight: 600; }
.detail-desc { margin-bottom: 24px; }
.detail-desc p { font-size: 14px; color: #475569; line-height: 1.7; margin-top: 6px; }
.btn-apply { padding: 12px 28px; background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: opacity 0.2s; }
.btn-apply:hover { opacity: 0.9; }
.btn-apply:disabled { background: #94a3b8; cursor: not-allowed; }
.btn-back { padding: 8px 16px; background: #f1f5f9; color: #475569; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; }
.btn-back:hover { background: #e2e8f0; }

.table-wrap { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
table { width: 100%; border-collapse: collapse; }
thead tr { background: #f8fafc; }
th { padding: 13px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 13px 16px; font-size: 13px; color: #334155; border-top: 1px solid #f1f5f9; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge.applied { background: #e0f2fe; color: #0284c7; }
.badge.shortlisted { background: #dcfce7; color: #16a34a; }
.badge.waitlisted { background: #fef9c3; color: #ca8a04; }
.badge.rejected { background: #fee2e2; color: #dc2626; }

.profile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.card h3 { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 20px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 12px; font-weight: 600; color: #64748b; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.4px; }
.field input { width: 100%; padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-family: 'Sora', sans-serif; outline: none; transition: border 0.2s; }
.field input:focus { border-color: #0ea5e9; }
.resume-zone { background: #f8fafc; border: 2px dashed #e2e8f0; border-radius: 10px; padding: 20px; text-align: center; font-size: 14px; color: #94a3b8; margin-bottom: 14px; }
.file-input { width: 100%; font-size: 13px; margin-bottom: 12px; }
.btn-primary { padding: 10px 20px; background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: opacity 0.2s; }
.btn-primary:hover { opacity: 0.9; }

.msg-success { color: #16a34a; font-size: 13px; margin-bottom: 12px; }
.msg-error { color: #dc2626; font-size: 13px; margin-bottom: 12px; }
.view-field { display: flex; flex-direction: column; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
.view-field:last-child { border-bottom: none; }
.vf-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px; }
.vf-value { font-size: 15px; font-weight: 600; color: #0f172a; }

.btn-withdraw { padding: 5px 12px; background: #fff1f2; color: #e11d48; border: 1.5px solid #fecaca; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; white-space: nowrap; }
.btn-withdraw:hover { background: #ffe4e6; }
.no-action { font-size: 13px; color: #cbd5e1; }

/* ── Notifications ── */
.notif-nav {position: relative;margin-top: 4px;}
.notif-dot {margin-left: auto;background: #ef4444;color: white;font-size: 10px;font-weight: 700;padding: 1px 6px;border-radius: 20px;position: static;   }
.notif-bell:hover { background: rgba(0,0,0,0.15); }
/* .notif-dot { position: absolute; top: 6px; right: 10px; background: #ef4444; color: white; font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 20px; } */
.notif-dropdown { position: absolute; left: 248px; top: 0; width: 300px; background: white; border-radius: 14px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); z-index: 999; max-height: 400px; overflow-y: auto; }
.notif-header { padding: 14px 16px; font-size: 13px; font-weight: 700; color: red; border-bottom: 1px solid #f1f5f9; }
.notif-empty { padding: 20px 16px; color: #94a3b8; font-size: 13px; text-align: center; }
.notif-item { padding: 12px 16px; border-bottom: 1px solid #f8fafc; transition: background 0.15s; }
.notif-item:last-child { border-bottom: none; }
.notif-unread { background: #f0f9ff; }
.notif-msg { font-size: 13px; color: #0f172a; line-height: 1.5; }
.notif-time { font-size: 11px; color: #94a3b8; margin-top: 4px; }

/* ── AI Suggestions ── */
.suggest-sub { font-size: 13px; color: #94a3b8; margin-bottom: 22px; margin-top: -12px; }
.suggest-loading { display: flex; align-items: center; gap: 12px; color: #64748b; font-size: 14px; padding: 40px 0; }
.spinner { width: 22px; height: 22px; border: 3px solid #e2e8f0; border-top-color: #0ea5e9; border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0; }
@keyframes spin { to { transform: rotate(360deg); } }
.suggest-list { display: flex; flex-direction: column; gap: 16px; }
.suggest-card { background: white; border-radius: 16px; padding: 22px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.suggest-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.suggest-title { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 3px; }
.suggest-company { font-size: 13px; color: #64748b; }
.suggest-score-wrap { text-align: center; flex-shrink: 0; }
.suggest-score { font-size: 18px; font-weight: 700; color: #0f172a; padding: 8px 14px; border-radius: 10px; }
.suggest-score-label { font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; margin-top: 3px; }
.suggest-meta { display: flex; gap: 12px; flex-wrap: wrap; font-size: 12px; color: #64748b; margin-bottom: 12px; }
.suggest-reason { font-size: 13px; color: #475569; background: #f8fafc; border-left: 3px solid #0ea5e9; padding: 10px 14px; border-radius: 0 8px 8px 0; line-height: 1.6; }

/* ── Student Report ── */
.rep-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 14px; margin-bottom: 8px; }
.rep-card { border-radius: 14px; padding: 18px 16px; text-align: center; }
.rep-val { font-size: 30px; font-weight: 700; margin-bottom: 4px; }
.rep-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.72; }
.rep-blue   { background: #eff6ff; color: #1d4ed8; }
.rep-yellow { background: #fefce8; color: #a16207; }
.rep-sky    { background: #e0f2fe; color: #0369a1; }
.rep-green  { background: #f0fdf4; color: #15803d; }
.rep-red    { background: #fff1f2; color: #be123c; }
.rep-grey   { background: #f8fafc; color: #475569; }
.section-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; }
.btn-rep-export { padding: 10px 22px; background: #f0fdf4; color: #15803d; border: 1.5px solid #bbf7d0; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-rep-export:hover { background: #dcfce7; }


@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { margin-left: 0; padding: 20px; }
  .profile-grid { grid-template-columns: 1fr; }
  .detail-grid { grid-template-columns: 1fr; }
}
</style>