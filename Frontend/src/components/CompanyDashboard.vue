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
          <div class="urole">Company</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <button :class="['nav-item', { active: tab === 'create' }]" @click="tab = 'create'">
          <span class="nav-icon">➕</span> Post a Drive
        </button>
        <button :class="['nav-item', { active: tab === 'drives' }]" @click="tab = 'drives'">
          <span class="nav-icon">📁</span> My Drives
        </button>
        <button :class="['nav-item', { active: tab === 'overview' }]" @click="tab = 'overview'">
          <span class="nav-icon">🏢</span> Company Overview
        </button>
        <button :class="['nav-item', { active: tab === 'report' }]" @click="tab = 'report'; fetchReport()">
          <span class="nav-icon">📊</span> Placement Report
        </button>
      </nav>
      <button class="logout-btn" @click="logout">⎋ Logout</button>
    </aside>

    <!-- Main -->
    <main class="main">

      <!-- Post a Drive -->
      <div v-if="tab === 'create'">
        <div class="page-header">
          <h2>Post a New Drive</h2>
        </div>
        <div class="card">
          <div class="form-grid">
            <div class="field">
              <label>Job Title</label>
              <input v-model="form.job_title" placeholder="e.g. Software Engineer" />
            </div>
            <div class="field">
              <label>Drive Name</label>
              <input v-model="form.drive_name" placeholder="e.g. Campus Drive 2025" />
            </div>
            <div class="field">
              <label>Salary</label>
              <input v-model="form.salary" placeholder="e.g. 6,00,000 LPA" />
            </div>
            <div class="field">
              <label>Location</label>
              <input v-model="form.location" placeholder="e.g. Chennai" />
            </div>
            <div class="field">
              <label>Eligibility</label>
              <input v-model="form.eligibility" placeholder="e.g. 7.0 CGPA" />
            </div>
            <div class="field">
              <label>Deadline</label>
              <input v-model="form.deadline" type="date" />
            </div>
            <div class="field full">
              <label>Job Description</label>
              <textarea v-model="form.description" placeholder="Describe the role, responsibilities..."></textarea>
            </div>
          </div>
          <p v-if="formError" class="msg-error">{{ formError }}</p>
          <p v-if="formSuccess" class="msg-success">{{ formSuccess }}</p>
          <button class="btn-primary" @click="createDrive">Post Drive</button>
        </div>
      </div>

      <!-- My Drives -->
      <div v-if="tab === 'drives'">
        <div class="page-header">
          <h2>My Drives</h2>
        </div>

        <!-- Open Drives -->
        <div class="section-label">
          Open Drives <span class="count-badge">{{ openDrives.length }}</span>
        </div>
        <p v-if="openDrives.length === 0" class="empty">No open drives yet.</p>

        <div class="drives-list" v-else>
          <div v-for="d in openDrives" :key="d.id" class="drive-card">
            <div class="drive-header">
              <div class="dr-info">
                <div class="dr-title">{{ d.drive_name || d.job_title }}</div>
                <div class="dr-sub">{{ d.job_title }} &nbsp;·&nbsp; Deadline: {{ d.deadline || 'N/A' }}</div>
              </div>
              <div class="dr-actions">
                <button class="btn-outline" @click="viewApplications(d)">
                  {{ selectedDrive && selectedDrive.id === d.id ? 'Hide' : 'View' }} Applications
                </button>
                <button class="btn-edit" @click="openEditModal(d)">✏️ Edit</button>
                <button class="btn-danger-soft" @click="closeDrive(d.id)">Mark Complete</button>
              </div>
            </div>

            <!-- Applications Panel -->
            <div v-if="selectedDrive && selectedDrive.id === d.id" class="apps-panel">
              <div class="apps-divider"></div>
              <div class="apps-inner">
                <div class="apps-header-row">
                  <span class="apps-label">Applications for: {{ selectedDrive.job_title }}</span>
                  <span class="count-badge">{{ driveApplications.length }}</span>
                </div>
                <p v-if="driveApplications.length === 0" class="empty">No applications yet.</p>
                <div v-for="app in driveApplications" :key="app.id" class="student-row">
                  <div class="student-avatar">{{ app.student_name?.charAt(0)?.toUpperCase() }}</div>
                  <div class="student-info">
                    <div class="student-name">{{ app.student_name }}</div>
                    <div class="student-dept">{{ app.department }}</div>
                  </div>
                  <div class="app-controls">
                    <span v-if="!app.resume_uploaded" class="no-resume">No resume</span>
                    <template v-else>
                      <button class="btn-resume" @click="viewResume(app.student_user_id)">👁 View</button>
                      <button class="btn-download" @click="downloadResume(app.student_user_id)">⬇ Download</button>
                    </template>
                    <!-- <div class="sel-wrap">
                      <select v-model="app.interview_type" @change="updateStatus(app)">
                        <option value="">Interview Type</option>
                        <option value="In-person">In-person</option>
                        <option value="Online">Online</option>
                        <option value="Telephonic">Telephonic</option>
                      </select>
                    </div> -->
                    <!-- <button class="btn-schedule" @click="openSchedule(app)">📅 Interview</button>
                    <button class="btn-result" @click="openResult(app)">🏁 Result</button> -->
                    <!-- <input
                      v-model="app.remark"
                      placeholder="Add remark..."
                      class="remark-input"
                      @blur="updateStatus(app)"
                    /> -->
                    <!-- <div class="sel-wrap">
                      <select v-model="app.status" @change="updateStatus(app)">
                        <option value="Applied">Applied</option>
                        <option value="Waitlisted">Waitlisted</option>
                        <option value="Shortlisted">Shortlisted</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </div> -->
                    <button class="btn-schedule" @click="openSchedule(app)">📅 Interview</button>
                    <button class="btn-result" @click="openResult(app)">🏁 Result</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Closed Drives -->
        <div class="section-label" style="margin-top: 36px;">
          Closed Drives <span class="count-badge grey">{{ closedDrives.length }}</span>
        </div>
        <p v-if="closedDrives.length === 0" class="empty">No closed drives.</p>
        <div class="table-wrap" v-else>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Job Title</th>
                <th>Drive Name</th>
                <th>Deadline</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(d, i) in closedDrives" :key="d.id">
                <td>{{ i + 1 }}</td>
                <td><strong>{{ d.job_title }}</strong></td>
                <td>{{ d.drive_name || '—' }}</td>
                <td>{{ d.deadline || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Company Overview -->
      <div v-if="tab === 'overview'">
        <div class="page-header"><h2>Company Profile</h2></div>
        <div class="card">
          <div v-if="!editingOverview">
            <div style="display:grid; gap:10px; margin-bottom:16px;">
              <div><span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;">Company Name</span><p style="margin:4px 0 0;font-size:15px;color:#1e293b;font-weight:600;">{{ profile.company_name || 'Not set' }}</p></div>
              <div><span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;">HR Contact</span><p style="margin:4px 0 0;font-size:14px;color:#475569;">{{ profile.hr_contact || 'Not set' }}</p></div>
              <div><span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;">Website</span><p style="margin:4px 0 0;font-size:14px;color:#475569;">{{ profile.website || 'Not set' }}</p></div>
              <div><span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;">Overview</span><p class="overview-text" style="margin:4px 0 0;">{{ profile.overview || 'No overview added yet.' }}</p></div>
            </div>
            <button class="btn-outline" @click="editingOverview = true">Edit Profile</button>
          </div>
          <div v-else>
            <div class="field">
              <label>Company Name</label>
              <input v-model="profile.company_name" type="text" placeholder="e.g. Acme Corp" />
            </div>
            <div class="field">
              <label>HR Contact (email or phone)</label>
              <input v-model="profile.hr_contact" type="text" placeholder="e.g. hr@acme.com or +91-9876543210" />
            </div>
            <div class="field">
              <label>Website</label>
              <input v-model="profile.website" type="text" placeholder="e.g. https://acme.com" />
            </div>
            <div class="field">
              <label>Overview</label>
              <textarea v-model="profile.overview" rows="5" placeholder="Describe your company, culture, and what you look for in candidates..."></textarea>
            </div>
            <div style="display:flex; gap:10px; margin-top:16px;">
              <button class="btn-primary" @click="saveOverview">Save Changes</button>
              <button class="btn-back" @click="editingOverview = false">Cancel</button>
            </div>
          </div>
          <p v-if="overviewMsg" class="msg-success" style="margin-top:12px;">{{ overviewMsg }}</p>
        </div>
      </div>


      <!-- Placement Report -->
      <div v-if="tab === 'report'">
        <div class="page-header"><h2>Placement Report</h2></div>

        <div v-if="reportLoading" style="color:#94a3b8; font-size:14px;">Loading report...</div>

        <div v-else-if="!report" style="color:#94a3b8; font-size:14px;">
          No report data available.
        </div>

        <div v-else>
          <!-- KPI Summary Cards -->
          <div class="report-cards" style="margin-bottom: 28px;">
            <div class="rcard blue">
              <div class="rcard-val">{{ report.total_drives ?? 0 }}</div>
              <div class="rcard-label">Total Drives</div>
            </div>
            <div class="rcard sky">
              <div class="rcard-val">{{ report.total_applications ?? 0 }}</div>
              <div class="rcard-label">Applications</div>
            </div>
            <div class="rcard yellow">
              <div class="rcard-val">{{ report.total_shortlisted ?? 0 }}</div>
              <div class="rcard-label">Shortlisted</div>
            </div>
            <div class="rcard emerald">
              <div class="rcard-val">{{ report.total_selected ?? 0 }}</div>
              <div class="rcard-label">Passed</div>
            </div>
            <div class="rcard red">
              <div class="rcard-val">{{ report.total_rejected ?? 0 }}</div>
              <div class="rcard-label">Rejected</div>
            </div>
            <!-- <div class="rcard grey2">
              <div class="rcard-val">{{ report.total_waitlisted ?? 0 }}</div>
              <div class="rcard-label">Waitlisted</div>
            </div> -->
          </div>

          <!-- Per-Drive Breakdown -->
          <div class="section-label" style="margin-bottom: 14px;">
            Drive Breakdown <span class="count-badge">{{ report.drives?.length ?? 0 }}</span>
          </div>

          <p v-if="!report.drives || report.drives.length === 0" class="empty">No drives found.</p>

          <div class="report-drives">
            <div v-for="d in report.drives" :key="d.drive_id" class="report-drive-card">
              <div class="rdc-header">
                <div>
                  <div class="rdc-title">{{ d.job_title }}</div>
                  <div class="rdc-sub">
                    {{ d.drive_name || '—' }}
                    <span v-if="d.deadline">· Deadline: {{ d.deadline }}</span>
                    <span :class="['status-chip', d.is_closed ? 'chip-closed' : 'chip-open']">
                      {{ d.is_closed ? 'Closed' : 'Open' }}
                    </span>
                  </div>
                </div>
                <div class="rdc-total-badge">{{ d.total ?? 0 }} Applicants</div>
              </div>

              <div class="stat-row">
                <span class="stat-pill pill-applied"><strong>{{ d.applied ?? 0 }}</strong> Applied</span>
                <span class="stat-pill pill-short"><strong>{{ d.shortlisted ?? 0 }}</strong> Shortlisted</span>
                <span class="stat-pill pill-wait"><strong>{{ d.waitlisted ?? 0 }}</strong> Waitlisted</span>
                <span class="stat-pill pill-sel"><strong>{{ d.selected ?? 0 }}</strong> Passed</span>
                <span class="stat-pill pill-rej"><strong>{{ d.rejected ?? 0 }}</strong> Rejected</span>
              </div>

              <div v-if="d.departments && d.departments.length" class="dept-row">
                <span class="dept-label">Departments:</span>
                <span v-for="dept in d.departments" :key="dept" class="dept-chip">{{ dept }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>



      <!-- Edit Drive Modal -->
      <div v-if="editModal.show" class="modal-overlay" @click.self="editModal.show = false">
        <div class="modal-box">
          <div class="modal-header">
            <span class="modal-title">Edit Drive</span>
            <button class="modal-close" @click="editModal.show = false">✕</button>
          </div>
          <div class="form-grid">
            <div class="field"><label>Job Title</label><input v-model="editModal.form.job_title" /></div>
            <div class="field"><label>Drive Name</label><input v-model="editModal.form.drive_name" /></div>
            <div class="field"><label>Salary</label><input v-model="editModal.form.salary" /></div>
            <div class="field"><label>Location</label><input v-model="editModal.form.location" /></div>
            <div class="field"><label>Eligibility</label><input v-model="editModal.form.eligibility" /></div>
            <div class="field"><label>Deadline</label><input v-model="editModal.form.deadline" type="date" /></div>
            <div class="field full"><label>Description</label><textarea v-model="editModal.form.description"></textarea></div>
          </div>
          <p v-if="editModal.error" class="msg-error">{{ editModal.error }}</p>
          <p v-if="editModal.success" class="msg-success">{{ editModal.success }}</p>
          <div style="display:flex; gap:10px; margin-top:4px;">
            <button class="btn-primary" @click="saveEditDrive">Save Changes</button>
            <button class="btn-back" @click="editModal.show = false">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Schedule Interview Modal -->
      <div v-if="scheduleModal" class="modal-overlay" @click.self="scheduleModal = null">
        <div class="modal-box">
          <div class="modal-header">
            <span class="modal-title">📅 Schedule Interview</span>
            <button class="modal-close" @click="scheduleModal = null">✕</button>
          </div>
          <p style="font-size:13px; color:#94a3b8; margin-bottom:20px;">
            {{ scheduleModal.student_name }} — {{ scheduleModal.job_title || selectedDrive?.job_title }}
          </p>
          <div class="form-grid" style="grid-template-columns:1fr;">
            <div class="field">
              <label>Interview Type</label>
              <select v-model="scheduleForm.interview_type">
                <option value="">— Select —</option>
                <option value="Online">Online</option>
                <option value="Onsite">Onsite</option>
                <option value="Telephonic">Telephonic</option>
              </select>
            </div>
            <div class="field">
              <label>Date & Time</label>
              <input v-model="scheduleForm.interview_date" type="datetime-local" />
            </div>
            <div class="field">
              <label>Link / Venue</label>
              <input v-model="scheduleForm.interview_link" placeholder="Meet link or office address..." />
            </div>
            <div class="field">
              <label>Notes / Instructions</label>
              <textarea v-model="scheduleForm.interview_notes" rows="3"
                placeholder="Bring your resume, dress formally..."></textarea>
            </div>
          </div>
          <p v-if="scheduleError" class="msg-error">{{ scheduleError }}</p>
          <div style="display:flex; gap:10px; margin-top:20px;">
            <button class="btn-primary" @click="saveSchedule" :disabled="scheduleSaving">
              {{ scheduleSaving ? 'Saving...' : '📅 Schedule' }}
            </button>
            <button class="btn-back" @click="scheduleModal = null">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Final Result Modal -->
      <div v-if="resultModal" class="modal-overlay" @click.self="resultModal = null">
        <div class="modal-box">
          <div class="modal-header">
            <span class="modal-title">🏁 Final Result</span>
            <button class="modal-close" @click="resultModal = null">✕</button>
          </div>
          <p style="font-size:13px; color:#94a3b8; margin-bottom:20px;">
            {{ resultModal.student_name }} — {{ resultModal.job_title || selectedDrive?.job_title }}
          </p>
          <div class="form-grid" style="grid-template-columns:1fr;">
            <div class="field">
              <label>Result</label>
              <select v-model="resultForm.result">
                <option value="">— Select —</option>
                <option value="Passed">✅ Passed</option>
                <option value="Failed">❌ Failed</option>
                <option value="Pending">⏳ Pending</option>
              </select>
            </div>
            <div class="field">
              <label>Remark</label>
              <input v-model="resultForm.remark" placeholder="Optional feedback..." />
            </div>
          </div>
          <p v-if="resultError" class="msg-error">{{ resultError }}</p>
          <div style="display:flex; gap:10px; margin-top:20px;">
            <button class="btn-primary" @click="saveResult" :disabled="resultSaving">
              {{ resultSaving ? 'Saving...' : '✓ Save Result' }}
            </button>
            <button class="btn-back" @click="resultModal = null">Cancel</button>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script>
import api from "../api.js"
export default {
  name: "CompanyDashboard",
  data() {
    return {
      tab: localStorage.getItem("companyTab") || "create",
      username: "",
      drives: [],
      driveApplications: [],
      selectedDrive: null,
      form: { drive_name: "", job_title: "", description: "", salary: "", location: "", eligibility: "", deadline: "" },
      formError: "", formSuccess: "",
      editingOverview: false,
      profile: { overview: "" , company_name: '', hr_contact: '', website: '', approved: false },
      overviewMsg: "",
      editModal: { show: false, driveId: null, form: {}, error: "", success: "" },
      report: null,
      reportLoading: false,
      scheduleModal: null,
      scheduleForm: { interview_type: '', interview_date: '', interview_link: '', interview_notes: '' },
      scheduleSaving: false,
      scheduleError: '',
      resultModal: null,
      resultForm: { result: '', remark: '' },
      resultSaving: false,
      resultError: ''
    }
  },
  computed: {
    openDrives() { return this.drives.filter(d => !d.is_closed) },
    closedDrives() { return this.drives.filter(d => d.is_closed) }
  },
  watch: {
    tab(newVal) { localStorage.setItem("companyTab", newVal) }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user"))
    this.username = user?.username || "Company"
    this.fetchDrives()
    this.fetchProfile()
  },
  methods: {
    async fetchDrives() {
      const user = JSON.parse(localStorage.getItem("user"))
      const res = await api.get(`/companies/${user.id}/drives`)
      this.drives = res.data
    },
    async createDrive() {
      this.formError = ""; this.formSuccess = ""
      if (!this.form.job_title || !this.form.description) {
        this.formError = "Job title and description are required"; return
      }
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        await api.post("/companies/drives", { company_id: user.id, ...this.form })
        this.formSuccess = "Drive posted successfully!"
        this.form = { drive_name: "", job_title: "", description: "", salary: "", location: "", eligibility: "", deadline: "" }
        this.fetchDrives()
        setTimeout(() => this.formSuccess = '', 2500)
      } catch (err) {
        this.formError = err.response?.data?.message || "Failed to create drive"
      }
    },
    async viewApplications(drive) {
      if (this.selectedDrive?.id === drive.id) { this.selectedDrive = null; return }
      this.selectedDrive = drive
      const res = await api.get(`/companies/drives/${drive.id}/applications`)
      this.driveApplications = res.data
    },
    async closeDrive(driveId) {
      if (!confirm("Mark this drive as complete?")) return
      await api.post(`/companies/drives/${driveId}/close`)
      this.fetchDrives()
      this.selectedDrive = null
    },
    async updateStatus(app) {
      await api.put(`/companies/applications/${app.id}/status`, {
        status: app.status,
        interview_type: app.interview_type || '',
        result: app.status === 'Shortlisted' ? 'Passed' : app.status === 'Rejected' ? 'Failed' : '',
        remark: app.remark || ''

      })
    },
    viewResume(studentUserId) {
      window.open(`http://127.0.0.1:5000/students/resume/view/${studentUserId}`, '_blank')
    },
    downloadResume(studentUserId) {
      window.open(`http://127.0.0.1:5000/students/resume/download/${studentUserId}`, '_blank')
    },
    async fetchProfile() {
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        const res = await api.get(`/companies/profile/${user.id}`)
        this.profile = res.data
      } catch (err) {}
    },
    async saveOverview() {
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        await api.put(`/companies/profile/${user.id}`, { overview: this.profile.overview , company_name: this.profile.company_name, hr_contact: this.profile.hr_contact, website: this.profile.website,})
        this.overviewMsg = "Overview updated!"
        this.editingOverview = false
        setTimeout(() => this.overviewMsg = '', 2500)
      } catch (err) { this.overviewMsg = "Failed to update" }
    },
    openEditModal(drive) {
      this.editModal = {
        show: true,
        driveId: drive.id,
        form: { drive_name: drive.drive_name, job_title: drive.job_title, description: drive.description, salary: drive.salary, location: drive.location, eligibility: drive.eligibility, deadline: drive.deadline },
        error: "", success: ""
      }
    },
    async saveEditDrive() {
      this.editModal.error = ""; this.editModal.success = ""
      if (!this.editModal.form.job_title || !this.editModal.form.description) {
        this.editModal.error = "Job title and description are required"; return
      }
      try {
        await api.put(`/companies/drives/${this.editModal.driveId}`, this.editModal.form)
        this.editModal.success = "Drive updated successfully!"
        this.fetchDrives()
        setTimeout(() => { this.editModal.show = false }, 1200)
      } catch (err) {
        this.editModal.error = err.response?.data?.message || "Failed to update drive"
      }
    },
    async fetchReport() {
      this.reportLoading = true
      try {
        const user = JSON.parse(localStorage.getItem("user"))
        const res = await api.get(`/companies/report/${user.id}`)
        this.report = res.data
      } catch (err) {
        this.report = null
      } finally {
        this.reportLoading = false
      }
    },
    openSchedule(app) {
      this.scheduleModal = app
      this.scheduleForm = {
        interview_type:  app.interview_type  || '',
        interview_date:  app.interview_date  || '',
        interview_link:  app.interview_link  || '',
        interview_notes: app.interview_notes || ''
      }
      this.scheduleError = ''
    },
    async saveSchedule() {
      this.scheduleSaving = true
      this.scheduleError = ''
      try {
        await api.put(`/companies/applications/${this.scheduleModal.id}/schedule-interview`, this.scheduleForm)
        const idx = this.driveApplications.findIndex(a => a.id === this.scheduleModal.id)
        if (idx !== -1) this.driveApplications[idx] = { ...this.driveApplications[idx], ...this.scheduleForm, status: 'Shortlisted' }
        this.scheduleModal = null
      } catch (err) {
        this.scheduleError = err.response?.data?.message || 'Failed to schedule interview'
      } finally {
        this.scheduleSaving = false
      }
    },
    openResult(app) {
      this.resultModal = app
      this.resultForm = {
        result: app.result || '',
        remark: app.remark || ''
      }
      this.resultError = ''
    },
    async saveResult() {
      this.resultSaving = true
      this.resultError = ''
      try {
        await api.put(`/companies/applications/${this.resultModal.id}/final-result`, this.resultForm)
        const idx = this.driveApplications.findIndex(a => a.id === this.resultModal.id)
        if (idx !== -1) this.driveApplications[idx] = { ...this.driveApplications[idx], ...this.resultForm }
        this.resultModal = null
      } catch (err) {
        this.resultError = err.response?.data?.message || 'Failed to save result'
      } finally {
        this.resultSaving = false
      }
    },
    logout() {
      localStorage.removeItem("token"); localStorage.removeItem("user")
      this.$router.push("/")
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }

.layout { display: flex; min-height: 100vh; font-family: 'Sora', sans-serif; background: #f1f5f9; }
.sidebar {width: 240px; min-height: 100vh;background: linear-gradient(135deg, #63fe4f, #00f2fe);display: flex; flex-direction: column;padding: 24px 16px; position: fixed; top: 0; left: 0;}
.sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 0 8px; margin-bottom: 28px; }
.brand-icon { font-size: 22px; }
.brand-name { font-size: 20px; font-weight: 700; color: #0f172a; }
.sidebar-user {display: flex; align-items: center; gap: 10px;background: rgba(0,0,0,0.08); border-radius: 12px;padding: 12px; margin-bottom: 28px;}
.avatar {width: 36px; height: 36px; background: #0ea5e9; border-radius: 50%;display: flex; align-items: center; justify-content: center;font-weight: 700; color: white; font-size: 15px; flex-shrink: 0;}
.uname { font-size: 13px; font-weight: 600; color: #0f172a; }
.urole { font-size: 11px; color: rgba(0,0,0,0.45); text-transform: uppercase; letter-spacing: 0.5px; }
.sidebar-nav { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.nav-item {display: flex; align-items: center; gap: 10px;padding: 11px 14px; border: none; border-radius: 10px;background: transparent; color: rgba(0,0,0,0.75);font-size: 14px; font-family: 'Sora', sans-serif; font-weight: 500;cursor: pointer; text-align: left; transition: all 0.2s;}
.nav-item:hover { background: rgba(0,0,0,0.08); color: #0f172a; }
.nav-item.active { background: white; color: #0ea5e9; }
.nav-icon { font-size: 16px; }
.logout-btn {display: flex; align-items: center; gap: 8px;padding: 11px 14px; border: none; border-radius: 10px;background: rgba(239,68,68,0.2); color: #dc2626;font-size: 14px; font-family: 'Sora', sans-serif; font-weight: 600;cursor: pointer; margin-top: 12px; transition: background 0.2s;}
.logout-btn:hover { background: rgba(239,68,68,0.35); }
.main { margin-left: 240px; flex: 1; padding: 36px; }
.page-header { display: flex; align-items: center; gap: 14px; margin-bottom: 24px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #0f172a; }
.section-label {font-size: 11px; font-weight: 600; color: #94a3b8;text-transform: uppercase; letter-spacing: 0.5px;margin-bottom: 14px; display: flex; align-items: center; gap: 8px;}
.count-badge {background: #e0f2fe; color: #0284c7;font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px;}
.count-badge.grey { background: #f1f5f9; color: #94a3b8; }
.empty { color: #94a3b8; font-size: 14px; margin-bottom: 16px; }
.card {background: white; border-radius: 16px; padding: 28px;box-shadow: 0 2px 12px rgba(0,0,0,0.06);}
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 22px; }
.form-grid .full { grid-column: span 2; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label {font-size: 12px; font-weight: 600; color: #64748b;text-transform: uppercase; letter-spacing: 0.4px;}
.field input,.field select,.field textarea {width: 100%; padding: 10px 14px;border: 1.5px solid #e2e8f0; border-radius: 10px;font-size: 14px; font-family: 'Sora', sans-serif;outline: none; background: #fff; color: #0f172a;transition: border-color 0.2s;}
.field input::placeholder,.field textarea::placeholder { color: #cbd5e1; }
.field input:focus,.field select:focus,.field textarea:focus { border-color: #0ea5e9; }
.field textarea { height: 110px; resize: vertical; }
.drives-list { display: flex; flex-direction: column; gap: 14px; }
.drive-card {background: white; border-radius: 16px;box-shadow: 0 2px 12px rgba(0,0,0,0.06);overflow: hidden; transition: box-shadow 0.2s;}
.drive-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.09); }
.drive-header {display: flex; justify-content: space-between;align-items: center; padding: 20px 24px;gap: 14px; flex-wrap: wrap;}
.dr-info { flex: 1; min-width: 0; }
.dr-title { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.dr-sub { font-size: 12px; color: #94a3b8; font-weight: 500; }
.dr-actions { display: flex; gap: 8px; flex-shrink: 0; }
.apps-divider { height: 1px; background: #f1f5f9; margin: 0 24px; }
.apps-inner { padding: 18px 24px 22px; }
.apps-header-row {display: flex; align-items: center; gap: 10px; margin-bottom: 16px;}
.apps-label {font-size: 11px; font-weight: 600; color: #94a3b8;text-transform: uppercase; letter-spacing: 0.5px;}
.student-row {display: flex; align-items: center; gap: 12px;padding: 12px 0; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap;}
.student-row:last-child { border-bottom: none; padding-bottom: 0; }
.student-avatar {width: 36px; height: 36px; border-radius: 50%;background: #0ea5e9;display: flex; align-items: center; justify-content: center;font-size: 13px; font-weight: 700; color: #fff; flex-shrink: 0;}
.student-info { min-width: 100px; }
.student-name { font-size: 14px; font-weight: 600; color: #0f172a; }
.student-dept { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.app-controls { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-left: auto; }
.btn-resume {font-family: 'Sora', sans-serif; font-size: 12px; font-weight: 600;background: #f0f9ff; color: #0ea5e9;border: none; padding: 7px 13px; border-radius: 8px;cursor: pointer; transition: background 0.2s; white-space: nowrap;}
.btn-resume:hover { background: #e0f2fe; }
.sel-wrap { position: relative; }
.sel-wrap select {appearance: none; font-family: 'Sora', sans-serif;font-size: 12px; font-weight: 500;background: #f8fafc; border: 1.5px solid #e2e8f0;color: #475569; padding: 7px 26px 7px 11px;border-radius: 8px; cursor: pointer; outline: none;transition: border-color 0.2s;}
.sel-wrap select:focus,.sel-wrap select:hover { border-color: #0ea5e9; color: #0f172a; }
.sel-wrap::after {content: '▾'; position: absolute; right: 9px; top: 50%;transform: translateY(-50%); color: #94a3b8; font-size: 10px; pointer-events: none;}
.remark-input {font-family: 'Sora', sans-serif; font-size: 12px;background: #f8fafc; border: 1.5px solid #e2e8f0;color: #475569; padding: 7px 11px;border-radius: 8px; outline: none; width: 110px;transition: border-color 0.2s;}
.remark-input::placeholder { color: #cbd5e1; }
.remark-input:focus { border-color: #0ea5e9; color: #0f172a; }
.table-wrap { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
table { width: 100%; border-collapse: collapse; }
thead tr { background: #f8fafc; }
th {padding: 13px 16px; text-align: left;font-size: 12px; font-weight: 600; color: #94a3b8;text-transform: uppercase; letter-spacing: 0.5px;}
td { padding: 13px 16px; font-size: 13px; color: #334155; border-top: 1px solid #f1f5f9; }
td strong { color: #0f172a; }
.overview-text { font-size: 14px; color: #475569; line-height: 1.8; }
.btn-primary {padding: 10px 22px;background: linear-gradient(135deg, #0ea5e9, #0284c7);color: white; border: none; border-radius: 10px;font-size: 14px; font-weight: 600; cursor: pointer;font-family: 'Sora', sans-serif; transition: opacity 0.2s;}
.btn-primary:hover { opacity: 0.9; }
.btn-outline {padding: 8px 16px; background: #f0f9ff;color: #0ea5e9; border: none;border-radius: 8px; font-size: 13px; font-weight: 600;cursor: pointer; font-family: 'Sora', sans-serif;transition: background 0.2s; white-space: nowrap;}
.btn-outline:hover { background: #e0f2fe; }
.btn-danger-soft {padding: 8px 16px; background: #fff1f2;color: #e11d48; border: none;border-radius: 8px; font-size: 13px; font-weight: 600;cursor: pointer; font-family: 'Sora', sans-serif;transition: background 0.15s; white-space: nowrap;}
.btn-danger-soft:hover { background: #ffe4e6; }
.btn-back {padding: 8px 16px; background: #f1f5f9; color: #475569; border: none; border-radius: 8px; font-size: 13px; font-weight: 600;cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s;}
.btn-back:hover { background: #e2e8f0; }
.msg-success { color: #16a34a; font-size: 13px; margin-bottom: 12px; }
.msg-error { color: #dc2626; font-size: 13px; margin-bottom: 12px; }
.btn-edit {padding: 8px 16px; background: #fefce8; color: #ca8a04; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.15s; white-space: nowrap;}
.btn-edit:hover { background: #fef9c3; }
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.55); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 24px; }
.modal-box { background: white; border-radius: 20px; padding: 28px; width: 100%; max-width: 620px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.18); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; }
.modal-title { font-size: 17px; font-weight: 700; color: #0f172a; }
.modal-close { background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px; font-size: 14px; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; }
.modal-close:hover { background: #e2e8f0; }
.report-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 14px; margin-bottom: 8px; }
.rcard { border-radius: 14px; padding: 18px 16px; text-align: center; }
.rcard-val { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.rcard-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.75; }
.rcard.blue { background: #eff6ff; color: #1d4ed8; }
.rcard.green { background: #f0fdf4; color: #15803d; }
.rcard.grey2 { background: #f8fafc; color: #475569; }
.rcard.sky { background: #e0f2fe; color: #0369a1; }
.rcard.yellow { background: #fefce8; color: #a16207; }
.rcard.emerald { background: #ecfdf5; color: #065f46; }
.rcard.red { background: #fff1f2; color: #be123c; }
.report-drives { display: flex; flex-direction: column; gap: 14px; }
.report-drive-card { background: white; border-radius: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 20px 24px; }
.rdc-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
.rdc-title { font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.rdc-sub { font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.rdc-total-badge { background: #f1f5f9; color: #475569; font-size: 12px; font-weight: 700; padding: 6px 14px; border-radius: 20px; white-space: nowrap; flex-shrink: 0; }
.status-chip { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.chip-open { background: #dcfce7; color: #15803d; }
.chip-closed { background: #f1f5f9; color: #64748b; }
.stat-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.stat-pill { padding: 5px 12px; border-radius: 8px; font-size: 12px; font-weight: 500; display: flex; gap: 5px; align-items: center; }
.stat-pill strong { font-weight: 700; }
.pill-applied { background: #f1f5f9; color: #475569; }
.pill-short { background: #fefce8; color: #a16207; }
.pill-wait { background: #eff6ff; color: #1d4ed8; }
.pill-sel { background: #ecfdf5; color: #065f46; }
.pill-rej { background: #fff1f2; color: #be123c; }
.dept-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
.dept-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.4px; }
.dept-chip { background: #f0f9ff; color: #0369a1; font-size: 12px; font-weight: 500; padding: 3px 10px; border-radius: 8px; }
.no-resume { font-size: 11px; color: #cbd5e1; font-style: italic; white-space: nowrap; }
.btn-schedule { font-family: 'Sora', sans-serif; font-size: 12px; font-weight: 600; background: #e0f2fe; color: #0284c7; border: none; padding: 7px 13px; border-radius: 8px; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
.btn-schedule:hover { background: #bae6fd; }
.btn-result { font-family: 'Sora', sans-serif; font-size: 12px; font-weight: 600; background: #f0fdf4; color: #15803d; border: none; padding: 7px 13px; border-radius: 8px; cursor: pointer; transition: background 0.2s; white-space: nowrap; }
.btn-result:hover { background: #bbf7d0; }
.btn-download {font-family: 'Sora', sans-serif; font-size: 12px; font-weight: 600;background: #f0fdf4; color: #15803d;border: none; padding: 7px 13px; border-radius: 8px;cursor: pointer; transition: background 0.2s; white-space: nowrap;}
.btn-download:hover { background: #dcfce7; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { margin-left: 0; padding: 20px; }
  .form-grid { grid-template-columns: 1fr; }
  .form-grid .full { grid-column: span 1; }
  .app-controls { margin-left: 0; }
}
</style>