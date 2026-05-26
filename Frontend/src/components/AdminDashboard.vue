<template>
  <div class="layout">

    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">🎓</span>
        <span class="brand-name">PlaceIt</span>
      </div>
      <div class="sidebar-user">
        <div class="avatar">A</div>
        <div>
          <div class="uname">Admin</div>
          <div class="urole">Administrator</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <button :class="['nav-item', { active: tab === 'stats' }]" @click="tab = 'stats'">
          <span class="nav-icon">📊</span> Dashboard
        </button>
        <button :class="['nav-item', { active: tab === 'approvals' }]" @click="tab = 'approvals'">
          <span class="nav-icon">✅</span> Pending Approvals
          <span v-if="pendingCompanies.length" class="notif">{{ pendingCompanies.length }}</span>
        </button>
        <button :class="['nav-item', { active: tab === 'companies' }]" @click="tab = 'companies'">
          <span class="nav-icon">🏢</span> Companies
        </button>
        <button :class="['nav-item', { active: tab === 'students' }]" @click="tab = 'students'">
          <span class="nav-icon">🎓</span> Students
        </button>
        <button :class="['nav-item', { active: tab === 'drives' }]" @click="tab = 'drives'">
          <span class="nav-icon">💼</span> All Drives
        </button>
        <button :class="['nav-item', { active: tab === 'applications' }]" @click="tab = 'applications'">
          <span class="nav-icon">📋</span> Applications
        </button>
      </nav>
      <button class="logout-btn" @click="logout">⎋ Logout</button>
    </aside>

    <!-- Main -->
    <main class="main">

      <!-- Search bar (global) -->
      <div class="search-wrap">
        <input v-model="search" placeholder="🔍  Search by name, department, status..." class="search-input" />
      </div>

      <!-- Stats Dashboard -->
      <div v-if="tab === 'stats'">
        <div class="page-header"><h2>Dashboard Overview</h2></div>

        <!-- Row 1: Entity counts -->
        <div class="stats-section-label">Platform Summary</div>
        <div class="stats-grid">
          <div class="stat-card indigo">
            <div class="stat-icon">🎓</div>
            <div class="stat-val">{{ students.length }}</div>
            <div class="stat-label">Total Students</div>
          </div>
          <div class="stat-card sky">
            <div class="stat-icon">🏢</div>
            <div class="stat-val">{{ companies.length }}</div>
            <div class="stat-label">Total Companies</div>
          </div>
          <div class="stat-card emerald">
            <div class="stat-icon">💼</div>
            <div class="stat-val">{{ drives.length }}</div>
            <div class="stat-label">Total Drives</div>
          </div>
          <div class="stat-card amber">
            <div class="stat-icon">📋</div>
            <div class="stat-val">{{ applications.length }}</div>
            <div class="stat-label">Total Applications</div>
          </div>
        </div>

        <!-- Row 2: Status breakdown -->
        <div class="stats-section-label" style="margin-top:28px;">Status Breakdown</div>
        <div class="stats-grid">
          <div class="stat-card green">
            <div class="stat-icon">✅</div>
            <div class="stat-val">{{ stats.approvedCos }}</div>
            <div class="stat-label">Approved Companies</div>
          </div>
          <div class="stat-card yellow">
            <div class="stat-icon">⏳</div>
            <div class="stat-val">{{ pendingCompanies.length }}</div>
            <div class="stat-label">Pending Approvals</div>
          </div>
          <div class="stat-card teal">
            <div class="stat-icon">📂</div>
            <div class="stat-val">{{ stats.openDrives }}</div>
            <div class="stat-label">Open Drives</div>
          </div>
          <div class="stat-card red">
            <div class="stat-icon">🚫</div>
            <div class="stat-val">{{ stats.blacklisted }}</div>
            <div class="stat-label">Blacklisted Users</div>
          </div>
        </div>

        <!-- Row 3: Application funnel -->
        <div class="stats-section-label" style="margin-top:28px;">Application Funnel</div>
        <div class="stats-grid">
          <div class="stat-card blue">
            <div class="stat-icon">📨</div>
            <div class="stat-val">{{ stats.totalApps }}</div>
            <div class="stat-label">Total Applications</div>
          </div>
          <div class="stat-card orange">
            <div class="stat-icon">📌</div>
            <div class="stat-val">{{ stats.shortlisted }}</div>
            <div class="stat-label">Shortlisted</div>
          </div>
          <div class="stat-card lime">
            <div class="stat-icon">🎉</div>
            <div class="stat-val">{{ stats.selected }}</div>
            <div class="stat-label">Selected</div>
          </div>
          <div class="stat-card rose">
            <div class="stat-icon">❌</div>
            <div class="stat-val">{{ stats.rejected }}</div>
            <div class="stat-label">Rejected</div>
          </div>
        </div>

        <!-- Quick links -->
        <div class="stats-section-label" style="margin-top:28px;">Quick Actions</div>
        <div class="quick-links">
          <button class="quick-btn" @click="tab = 'approvals'">
            ✅ Pending Approvals
            <span v-if="pendingCompanies.length" class="ql-badge">{{ pendingCompanies.length }}</span>
          </button>
          <button class="quick-btn" @click="tab = 'companies'">🏢 Manage Companies</button>
          <button class="quick-btn" @click="tab = 'students'">🎓 Manage Students</button>
          <button class="quick-btn" @click="tab = 'drives'">💼 View All Drives</button>
          <button class="quick-btn" @click="tab = 'applications'">📋 View Applications</button>
        </div>
      </div>

      <!-- Pending Approvals -->
      <div v-if="tab === 'approvals'">
        <div class="page-header"><h2>Pending Company Approvals</h2></div>
        <p v-if="pendingCompanies.length === 0" class="empty">No pending approvals.</p>
        <div class="list-stack">
          <div v-for="c in pendingCompanies" :key="c.id" class="list-row">
            <div class="row-info">
              <div class="avatar-sm">{{ c.username.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="row-name">{{ c.username }}</div>
                <div class="row-sub">Awaiting approval</div>
              </div>
            </div>
            <div class="row-actions">
              <button class="btn-success" @click="approveCompany(c.id)">Approve</button>
              <button class="btn-danger" @click="blacklist(c.user_id, 'company')">Blacklist</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Companies -->
      <div v-if="tab === 'companies'">
        <div class="page-header">
          <h2>Registered Companies</h2><span class="count-badge">{{ companies.length }}</span>
          <div class="export-btns">
            <button class="btn-export-csv" @click="exportCSV('companies')">⬇ CSV</button>
            <button class="btn-export-pdf" @click="exportPDF('companies')">⬇ PDF</button>
          </div>
        </div>
        <div class="app-filters" style="margin-bottom:16px;">
          <input v-model="companyFilter.search" class="filter-input" placeholder="🔍 Search by name..." />
          <select v-model="companyFilter.approved" class="filter-select">
            <option value="">All Companies</option>
            <option value="true">Approved Only</option>
            <option value="false">Pending Only</option>
          </select>
          <select v-model="companyFilter.blacklisted" class="filter-select">
            <option value="">Any Status</option>
            <option value="false">Active Only</option>
            <option value="true">Blacklisted Only</option>
          </select>
          <button v-if="companyFilter.search || companyFilter.approved || companyFilter.blacklisted"
            class="filter-clear" @click="companyFilter = { search: '', approved: '', blacklisted: '' }">
            ✕ Clear
          </button>
        </div>
        <p v-if="filteredCompanies.length === 0" class="empty">No companies found.</p>
        <div class="list-stack">
          <div v-for="c in filteredCompanies" :key="c.id" class="list-row">
            <div class="row-info" style="cursor:pointer;" @click="viewCompanyProfile(c.user_id)">
              <div class="avatar-sm" :class="{ 'av-red': c.is_blacklisted }">{{ c.username.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="row-name" :class="{ 'txt-red': c.is_blacklisted }">{{ c.username }}</div>
                <div class="row-sub">
                  <span v-if="c.is_blacklisted" class="badge rejected">Blacklisted</span>
                  <span v-else-if="c.approved" class="badge approved">Approved</span>
                  <span v-else class="badge pending">Pending</span>
                </div>
              </div>
            </div>
            <div class="row-actions">
              <button class="btn-view" @click="viewCompanyProfile(c.user_id)">View Profile</button>
              <button v-if="!c.is_blacklisted" class="btn-danger" @click="blacklist(c.user_id, 'company')">Blacklist</button>
              <button v-else class="btn-success" @click="unblacklist(c.user_id)">Unblacklist</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Students -->
      <div v-if="tab === 'students'">
        <div class="page-header">
          <h2>Registered Students</h2>
          <div class="export-btns">
            <button class="btn-export-csv" @click="exportCSV('students')">⬇ CSV</button>
            <button class="btn-export-pdf" @click="exportPDF('students')">⬇ PDF</button>
          </div>
        </div>
        <div class="app-filters" style="margin-bottom:16px;">
          <input v-model="studentFilter.search" class="filter-input" placeholder="🔍 Search by name..." />
          <input v-model="studentFilter.department" class="filter-input" placeholder="🎓 Department..." />
          <select v-model="studentFilter.blacklisted" class="filter-select">
            <option value="">All Students</option>
            <option value="false">Active Only</option>
            <option value="true">Blacklisted Only</option>
          </select>
          <button v-if="studentFilter.search || studentFilter.department || studentFilter.blacklisted"
            class="filter-clear" @click="studentFilter = { search: '', department: '', blacklisted: '' }">
            ✕ Clear
          </button>
        </div>
        <p v-if="filteredStudents.length === 0" class="empty">No students found.</p>
        <div class="list-stack">
          <div v-for="s in filteredStudents" :key="s.id" class="list-row">
            <div class="row-info" style="cursor:pointer;" @click="viewStudentProfile(s.user_id)">
              <div class="avatar-sm" :class="{ 'av-red': s.is_blacklisted }">{{ s.username.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="row-name" :class="{ 'txt-red': s.is_blacklisted }">{{ s.username }}</div>
                <div class="row-sub">
                  {{ s.department || 'No department' }}
                  <span v-if="s.is_blacklisted" class="badge rejected" style="margin-left:8px;">Blacklisted</span>
                </div>
              </div>
            </div>
            <div class="row-actions">
              <button class="btn-view" @click="viewStudentProfile(s.user_id)">View Profile</button>
              <button v-if="!s.is_blacklisted" class="btn-danger" @click="blacklist(s.user_id, 'student')">Blacklist</button>
              <button v-else class="btn-success" @click="unblacklist(s.user_id)">Unblacklist</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Profile Modal -->
      <div v-if="studentModal" class="sp-overlay" @click.self="closeStudentModal">
        <div class="sp-card">
          <button class="sp-close" @click="closeStudentModal">✕</button>

          <div v-if="profileLoading" class="sp-loading">
            <div class="sp-spinner"></div>
            <p>Loading profile...</p>
          </div>

          <div v-else-if="studentModal.username">
            <!-- ── Header ── -->
            <div class="sp-head">
              <div class="sp-avatar">{{ studentModal.username.charAt(0).toUpperCase() }}</div>
              <div class="sp-head-text">
                <div class="sp-name">{{ studentModal.username }}</div>
                <div class="sp-sub">{{ studentModal.department || 'No department' }}</div>
                <span :class="['sp-badge', studentModal.is_blacklisted ? 'sp-badge-red' : 'sp-badge-green']">
                  {{ studentModal.is_blacklisted ? 'Blacklisted' : 'Active' }}
                </span>
              </div>
            </div>

            <!-- ── Info rows ── -->
            <div class="sp-rows">
              <div class="sp-row">
                <span class="sp-row-icon sp-icon-blue">✉</span>
                <span class="sp-row-label">Email</span>
                <span class="sp-row-val">{{ studentModal.email || '—' }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-row-icon sp-icon-red">✆</span>
                <span class="sp-row-label">Phone</span>
                <span class="sp-row-val">{{ studentModal.phone || '—' }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-row-icon sp-icon-pink">⚲</span>
                <span class="sp-row-label">Location</span>
                <span class="sp-row-val">{{ studentModal.location || '—' }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-row-icon sp-icon-teal">🎓</span>
                <span class="sp-row-label">Department</span>
                <span class="sp-row-val">{{ studentModal.department || '—' }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-row-icon sp-icon-yellow">★</span>
                <span class="sp-row-label">Resume</span>
                <span class="sp-row-val" style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                  <span v-if="studentModal.resume_uploaded" class="sp-chip sp-chip-green">Uploaded</span>
                  <span v-else class="sp-chip sp-chip-gray">Not Uploaded</span>
                  <button v-if="studentModal.resume_uploaded" class="sp-resume-btn"
                    @click="downloadStudentResume(studentModal.user_id)">
                    ⬇ Download
                  </button>
                </span>
              </div>
            </div>

            <!-- ── Applications section ── -->
            <div class="sp-skills-section">
              <div class="sp-skills-title">APPLICATIONS</div>
              <div v-if="studentModal.applications && studentModal.applications.length" class="sp-chips-wrap">
                <span v-for="(a, i) in studentModal.applications" :key="i"
                  :class="['sp-chip', 'sp-chip-blue']">
                  {{ a.job_title }} @ {{ a.company_name }}
                </span>
              </div>
              <div v-else class="sp-no-apps">No applications yet.</div>
            </div>

            <!-- ── Footer buttons ── -->
            <div class="sp-footer">
              <button class="sp-btn-close" @click="closeStudentModal">Close</button>
              <button v-if="!studentModal.is_blacklisted" class="sp-btn-blacklist"
                @click="blacklistFromModal(studentModal.user_id, 'student')">Blacklist Student</button>
              <button v-else class="sp-btn-unblacklist"
                @click="unblacklistFromModal(studentModal.user_id)">Unblacklist Student</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Company Profile Modal -->
      <div v-if="companyModal" class="modal-overlay" @click.self="closeCompanyModal">
        <div class="modal-box">
          <button class="modal-close" @click="closeCompanyModal">✕</button>
          <div v-if="profileLoading" class="modal-loading">
            <div class="spinner"></div>
            <p>Loading profile...</p>
          </div>
          <div v-else-if="companyModal.username">
            <!-- Header -->
            <div class="pm-header">
              <div class="pm-avatar pm-avatar-blue">{{ (companyModal.username || 'C').charAt(0).toUpperCase() }}</div>
              <div class="pm-header-info">
                <div class="pm-name">{{ companyModal.company_name || companyModal.username }}</div>
                <div class="pm-dept">{{ companyModal.username }} &middot; Company</div>
                <span :class="['pm-status-badge', companyModal.is_blacklisted ? 'status-blacklisted' : companyModal.approved ? 'status-active' : 'status-pending']">
                  {{ companyModal.is_blacklisted ? '⛔ Blacklisted' : companyModal.approved ? '✓ Approved' : '⏳ Pending' }}
                </span>
              </div>
            </div>

            <!-- Info rows -->
            <div class="pm-info-list">
              <div class="pm-info-row">
                <span class="pm-info-icon">🏢</span>
                <span class="pm-info-label">Company Name</span>
                <span class="pm-info-value">{{ companyModal.company_name || '—' }}</span>
              </div>
              <div class="pm-info-row">
                <span class="pm-info-icon">📞</span>
                <span class="pm-info-label">HR Contact</span>
                <span class="pm-info-value">{{ companyModal.hr_contact || '—' }}</span>
              </div>
              <div class="pm-info-row">
                <span class="pm-info-icon">🌐</span>
                <span class="pm-info-label">Website</span>
                <span class="pm-info-value">{{ companyModal.website || '—' }}</span>
              </div>
              <div class="pm-info-row">
                <span class="pm-info-icon">📝</span>
                <span class="pm-info-label">Overview</span>
                <span class="pm-info-value">{{ companyModal.overview || '—' }}</span>
              </div>
              <div class="pm-info-row">
                <span class="pm-info-icon">💼</span>
                <span class="pm-info-label">Total Drives</span>
                <span class="pm-info-value">{{ (companyModal.drives || []).length }}</span>
              </div>
              <div class="pm-info-row">
                <span class="pm-info-icon">✅</span>
                <span class="pm-info-label">Open Drives</span>
                <span class="pm-info-value">{{ (companyModal.drives || []).filter(d => !d.is_closed).length }}</span>
              </div>
            </div>

            <!-- Drives table -->
            <div v-if="companyModal.drives && companyModal.drives.length" class="pm-section">
              <div class="pm-section-title">DRIVES</div>
              <table class="pm-table">
                <thead><tr><th>Job Title</th><th>Location</th><th>Apps</th><th>Status</th></tr></thead>
                <tbody>
                  <tr v-for="(d, i) in companyModal.drives" :key="i">
                    <td><strong>{{ d.job_title }}</strong></td>
                    <td>{{ d.location || '—' }}</td>
                    <td>{{ d.application_count }}</td>
                    <td><span :class="['pill', d.is_closed ? 'pill-rejected' : 'pill-shortlisted']">{{ d.is_closed ? 'Closed' : 'Open' }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="pm-empty">No drives posted yet.</div>

            <!-- Footer actions -->
            <div class="pm-footer">
              <button class="pm-btn-close" @click="closeCompanyModal">Close</button>
              <button v-if="!companyModal.is_blacklisted" class="pm-btn-blacklist"
                @click="blacklistFromModal(companyModal.user_id, 'company')">Blacklist Company</button>
              <button v-else class="pm-btn-unblacklist"
                @click="unblacklistFromModal(companyModal.user_id)">Unblacklist Company</button>
            </div>
          </div>
        </div>
      </div>

      <!-- All Drives -->
      <div v-if="tab === 'drives'">

        <!-- Pending Drive Approvals -->
        <div class="page-header">
          <h2>Pending Drive Approvals</h2>
          <span class="count-badge">{{ pendingDrives.length }}</span>
        </div>
        <p v-if="pendingDrives.length === 0" class="empty" style="margin-bottom:28px;">No drives awaiting approval.</p>
        <div class="list-stack" style="margin-bottom:36px;">
          <div v-for="d in pendingDrives" :key="d.id" class="list-row">
            <div class="row-info">
              <div class="avatar-sm">{{ d.company_name.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="row-name">{{ d.job_title }}</div>
                <div class="row-sub">{{ d.company_name }} &nbsp;·&nbsp; Deadline: {{ d.deadline || 'N/A' }}</div>
                <div class="row-sub" style="margin-top:2px;">{{ d.eligibility || 'No eligibility criteria' }}</div>
              </div>
            </div>
            <div class="row-actions">
              <button class="btn-success" @click="approveDrive(d.id)">Approve</button>
              <button class="btn-danger" @click="rejectDrive(d.id)">Reject</button>
            </div>
          </div>
        </div>

        <!-- All Drives Table -->
        <div class="page-header">
          <h2>All Drives</h2>
          <div class="export-btns">
            <button class="btn-export-csv" @click="exportCSV('drives')">⬇ CSV</button>
            <button class="btn-export-pdf" @click="exportPDF('drives')">⬇ PDF</button>
          </div>
        </div>
        <div class="table-wrap">
          <p v-if="drives.length === 0" class="empty" style="padding:20px;">No drives.</p>
          <table v-else>
            <thead><tr><th>#</th><th>Job Title</th><th>Company</th><th>Approval</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="(d, i) in drives" :key="d.id">
                <td>{{ i + 1 }}</td>
                <td><strong>{{ d.job_title }}</strong></td>
                <td>{{ d.company_name }}</td>
                <td>
                  <span :class="['badge', d.admin_status === 'Approved' ? 'approved' : d.admin_status === 'Rejected' ? 'rejected' : 'pending']">
                    {{ d.admin_status || 'Pending' }}
                  </span>
                </td>
                <td><span :class="['badge', d.is_closed ? 'rejected' : 'approved']">{{ d.is_closed ? 'Closed' : 'Open' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
            

      <!-- Applications -->
      <div v-if="tab === 'applications'">
        <div class="page-header">
          <h2>All Applications</h2><span class="count-badge">{{ filteredApplications.length }}</span>
          <div class="export-btns">
            <button class="btn-export-csv" @click="exportCSV('applications')">⬇ CSV</button>
            <button class="btn-export-pdf" @click="exportPDF('applications')">⬇ PDF</button>
          </div>
        </div>

        <!-- Filter bar -->
        <div class="app-filters">
          <input v-model="appFilter.student" class="filter-input" placeholder="🔍 Student name..." />
          <input v-model="appFilter.company" class="filter-input" placeholder="🏢 Company name..." />
          <select v-model="appFilter.status" class="filter-select">
            <option value="">All Statuses</option>
            <option value="Applied">Applied</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Waitlisted">Waitlisted</option>
            <option value="Rejected">Rejected</option>
          </select>
          <button v-if="appFilter.student || appFilter.company || appFilter.status"
            class="filter-clear" @click="appFilter = { student: '', company: '', status: '' }">
            ✕ Clear
          </button>
        </div>

        <div class="table-wrap">
          <p v-if="filteredApplications.length === 0" class="empty" style="padding:20px;">No applications found.</p>
          <table v-else>
            <thead><tr><th>Student</th><th>Drive</th><th>Company</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              <tr v-for="a in filteredApplications" :key="a.id">
                <td><strong>{{ a.student_name }}</strong></td>
                <td>{{ a.drive_name }}</td>
                <td>{{ a.company_name }}</td>
                <td><span :class="['badge', a.status.toLowerCase()]">{{ a.status }}</span></td>
                <td><button class="btn-edit" @click="openAppEdit(a)">✏ Edit</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <p v-if="error" class="msg-error">{{ error }}</p>

      <!-- Edit Application Modal -->
      <div v-if="appEditModal" class="modal-overlay" @click.self="closeAppEdit">
        <div class="modal-box">
          <button class="modal-close" @click="closeAppEdit">✕</button>
          <div style="padding: 28px;">
            <h3 style="font-size:17px; font-weight:700; color:#0f172a; margin-bottom:4px;">Edit Application</h3>
            <p style="font-size:13px; color:#94a3b8; margin-bottom:22px;">
              {{ appEditModal.student_name }} → {{ appEditModal.drive_name }}
            </p>
            <div class="ae-field">
              <label class="ae-label">Status</label>
              <select v-model="appEditForm.status" class="ae-select">
                <option value="Applied">Applied</option>
                <option value="Shortlisted">Shortlisted</option>
                <option value="Waitlisted">Waitlisted</option>
                <option value="Rejected">Rejected</option>
                <option value="Selected">Selected</option>
              </select>
            </div>
            <div class="ae-field">
              <label class="ae-label">Interview Type</label>
              <select v-model="appEditForm.interview_type" class="ae-select">
                <option value="">— None —</option>
                <option value="Online">Online</option>
                <option value="Onsite">Onsite</option>
                <option value="Telephonic">Telephonic</option>
              </select>
            </div>
            <div class="ae-field">
              <label class="ae-label">Result</label>
              <select v-model="appEditForm.result" class="ae-select">
                <option value="">— None —</option>
                <option value="Pending">Pending</option>
                <option value="Passed">Passed</option>
                <option value="Failed">Failed</option>
              </select>
            </div>
            <div class="ae-field">
              <label class="ae-label">Remark</label>
              <input v-model="appEditForm.remark" class="ae-input" placeholder="Optional feedback or note..." />
            </div>
            <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:24px;">
              <button class="ae-btn-cancel" @click="closeAppEdit">Cancel</button>
              <button class="ae-btn-save" @click="updateApplication" :disabled="appEditSaving">
                {{ appEditSaving ? 'Saving...' : '✓ Save Changes' }}
              </button>
            </div>
            <p v-if="appEditError" style="color:#dc2626; font-size:13px; margin-top:10px;">{{ appEditError }}</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import api from "../api.js"
export default {
  name: "AdminDashboard",
  data() {
    return {
      tab: localStorage.getItem("adminTab") || "stats", 
      pendingCompanies: [], pendingDrives: [], companies: [], students: [], drives: [], applications: [],
      search: "", error: "",
      studentFilter: { search: '', department: '', blacklisted: '' },
      companyFilter: { search: '', approved: '', blacklisted: '' },
      appFilter: { student: '', company: '', status: '' },
      studentModal: null, companyModal: null, profileLoading: false,
      appEditModal: null,
      appEditForm: { status: '', interview_type: '', result: '', remark: '' },
      appEditSaving: false,
      appEditError: ''
    }
  },
  computed: {
    filteredCompanies() {
      return this.companies.filter(c => {
        const globalQ = this.search.toLowerCase()
        const matchGlobal = !this.search ||
          c.username.toLowerCase().includes(globalQ)

        const matchSearch = !this.companyFilter.search ||
          c.username.toLowerCase().includes(this.companyFilter.search.toLowerCase())
        const matchApproved = !this.companyFilter.approved ||
          String(c.approved) === this.companyFilter.approved
        const matchBlacklisted = !this.companyFilter.blacklisted ||
          String(c.is_blacklisted) === this.companyFilter.blacklisted

        return matchGlobal && matchSearch && matchApproved && matchBlacklisted
      })
    },
    filteredStudents() {
      return this.students.filter(s => {
        const globalQ = this.search.toLowerCase()
        const matchGlobal = !this.search ||
          s.username.toLowerCase().includes(globalQ) ||
          (s.department || '').toLowerCase().includes(globalQ)

        const matchSearch = !this.studentFilter.search ||
          s.username.toLowerCase().includes(this.studentFilter.search.toLowerCase())
        const matchDept = !this.studentFilter.department ||
          (s.department || '').toLowerCase().includes(this.studentFilter.department.toLowerCase())
        const matchBlacklisted = !this.studentFilter.blacklisted ||
          String(s.is_blacklisted) === this.studentFilter.blacklisted

        return matchGlobal && matchSearch && matchDept && matchBlacklisted
      })
    },
    filteredApplications() {
      const q = this.search.toLowerCase()
      return this.applications.filter(a => {
        const matchGlobal = !this.search ||
          a.student_name.toLowerCase().includes(q) ||
          a.drive_name.toLowerCase().includes(q) ||
          a.company_name.toLowerCase().includes(q)

        const matchStudent = !this.appFilter.student ||
          a.student_name.toLowerCase().includes(this.appFilter.student.toLowerCase())
        const matchCompany = !this.appFilter.company ||
          a.company_name.toLowerCase().includes(this.appFilter.company.toLowerCase())
        const matchStatus = !this.appFilter.status || a.status === this.appFilter.status
        
        return matchGlobal && matchStudent && matchCompany && matchStatus
      })
    },
    stats() {
      const totalApps = this.applications.length
      const shortlisted = this.applications.filter(a => a.status === 'Shortlisted').length
      const selected    = this.applications.filter(a => a.status === 'Selected').length
      const rejected    = this.applications.filter(a => a.status === 'Rejected').length
      const openDrives  = this.drives.filter(d => !d.is_closed).length
      const approvedCos = this.companies.filter(c => c.approved && !c.is_blacklisted).length
      const blacklisted = this.companies.filter(c => c.is_blacklisted).length
                        + this.students.filter(s => s.is_blacklisted).length
      return { totalApps, shortlisted, selected, rejected, openDrives, approvedCos, blacklisted }
    }
  },
  watch: {
    tab(newVal) {
      localStorage.setItem("adminTab", newVal)
    }
  },
  mounted() { this.fetchAll() },
  methods: {
    async fetchAll() {
      try {
        const [pending, companies, students, drives, apps, pendingDrives] = await Promise.all([
        api.get("/admin/pending-companies"), api.get("/admin/companies"),
        api.get("/admin/students"), api.get("/admin/drives"), api.get("/admin/applications"), api.get("/admin/drives/pending")
      ])
      this.pendingCompanies = pending.data; this.companies = companies.data
      this.students = students.data; this.drives = drives.data; this.applications = apps.data
      this.pendingDrives = pendingDrives.data
      } catch (err) { this.error = "Failed to load data" }
    },
    async viewStudentProfile(userId) {
      this.profileLoading = true
      this.studentModal = {}
      this.companyModal = null
      try {
        const res = await api.get(`/admin/student-profile/${userId}`)
        this.studentModal = res.data
      } catch { this.studentModal = null; this.error = "Failed to load student profile" }
      this.profileLoading = false
    },
    async viewCompanyProfile(userId) {
      this.profileLoading = true
      this.companyModal = {}
      this.studentModal = null
      try {
        const res = await api.get(`/admin/company-profile/${userId}`)
        this.companyModal = res.data
      } catch { this.companyModal = null; this.error = "Failed to load company profile" }
      this.profileLoading = false
    },
    closeStudentModal() { this.studentModal = null },
    closeCompanyModal() { this.companyModal = null },
    async blacklistFromModal(userId, role) {
      if (!confirm(`Blacklist this ${role}?`)) return
      await api.post(`/admin/blacklist/${userId}`)
      this.fetchAll()
      if (role === 'student') { this.studentModal = { ...this.studentModal, is_blacklisted: true } }
      else { this.companyModal = { ...this.companyModal, is_blacklisted: true } }
    },
    async unblacklistFromModal(userId) {
      await api.post(`/admin/unblacklist/${userId}`)
      this.fetchAll()
      if (this.studentModal) { this.studentModal = { ...this.studentModal, is_blacklisted: false } }
      else if (this.companyModal) { this.companyModal = { ...this.companyModal, is_blacklisted: false } }
    },
    async approveCompany(id) { await api.post(`/admin/approve-company/${id}`); this.fetchAll() },
    async approveDrive(driveId) { await api.post(`/admin/drives/${driveId}/approve`); this.fetchAll() },
    async rejectDrive(driveId) { await api.post(`/admin/drives/${driveId}/reject`); this.fetchAll() },
    async blacklist(userId, role) {
      if (!confirm(`Blacklist this ${role}?`)) return
      await api.post(`/admin/blacklist/${userId}`); this.fetchAll()
    },
    async unblacklist(userId) { await api.post(`/admin/unblacklist/${userId}`); this.fetchAll() },
    exportCSV(type) {
      const token = localStorage.getItem('token')
      window.open(`http://127.0.0.1:5000/admin/export/csv?type=${type}&token=${token}`, '_blank')
    },
    downloadStudentResume(userId) {
      const token = localStorage.getItem('token')
      window.open(`http://127.0.0.1:5000/students/resume/download/${userId}?token=${token}`, '_blank')
    },
    exportPDF(type) {
      const token = localStorage.getItem('token')
      window.open(`http://127.0.0.1:5000/admin/export/pdf?type=${type}&token=${token}`, '_blank')
    },
    logout() { localStorage.removeItem("token"); localStorage.removeItem("user"); this.$router.push("/") },
    openAppEdit(app) {
      this.appEditModal = app
      this.appEditForm = {
        status:         app.status         || 'Applied',
        interview_type: app.interview_type || '',
        result:         app.result         || '',
        remark:         app.remark         || ''
      }
      this.appEditError = ''
    },
    closeAppEdit() { this.appEditModal = null; this.appEditError = '' },
    async updateApplication() {
      this.appEditSaving = true
      this.appEditError = ''
      try {
        await api.put(`/admin/applications/${this.appEditModal.id}`, this.appEditForm)
        const idx = this.applications.findIndex(a => a.id === this.appEditModal.id)
        if (idx !== -1) this.applications[idx] = { ...this.applications[idx], ...this.appEditForm }
        this.closeAppEdit()
      } catch (err) {
        this.appEditError = err.response?.data?.message || 'Failed to update application'
      } finally {
        this.appEditSaving = false
      }
    }
  }
}

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
.layout { display: flex; min-height: 100vh; font-family: 'Sora', sans-serif; background: #f1f5f9; }
.sidebar { width: 240px; min-height: 100vh; background: linear-gradient(135deg, #63fe4f, #00f2fe); display: flex; flex-direction: column; padding: 24px 16px; position: fixed; top: 0; left: 0; }
.sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 0 8px; margin-bottom: 28px; }
.brand-icon { font-size: 22px; }
.brand-name { font-size: 20px; font-weight: 700; color: #0f172a; }
.sidebar-user { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.08); border-radius: 12px; padding: 12px; margin-bottom: 28px; }
.avatar { width: 36px; height: 36px; background: #7c3aed; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; font-size: 15px; flex-shrink: 0; }
.uname { font-size: 13px; font-weight: 600; color: #0f172a; }
.urole { font-size: 11px; color: rgba(0,0,0,0.45); text-transform: uppercase; letter-spacing: 0.5px; }
.sidebar-nav { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 11px 14px; border: none; border-radius: 10px; background: transparent; color: rgba(0,0,0,0.75); font-size: 14px; font-family: 'Sora', sans-serif; font-weight: 500; cursor: pointer; text-align: left; transition: all 0.2s; position: relative; }
.nav-item:hover { background: rgba(0,0,0,0.08); color: #0f172a; }
.nav-item.active { background: white; color: #0ea5e9; }
.nav-icon { font-size: 16px; }
.notif { margin-left: auto; background: #ef4444; color: white; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 20px; }
.logout-btn { display: flex; align-items: center; gap: 8px; padding: 11px 14px; border: none; border-radius: 10px; background: rgba(239,68,68,0.2); color: #dc2626; font-size: 14px; font-family: 'Sora', sans-serif; font-weight: 600; cursor: pointer; margin-top: 12px; transition: background 0.2s; }
.logout-btn:hover { background: rgba(239,68,68,0.35); }

.main { margin-left: 240px; flex: 1; padding: 36px; }
.search-wrap { margin-bottom: 28px; }
.search-input { width: 100%; max-width: 480px; padding: 11px 16px; border: 1.5px solid #e2e8f0; border-radius: 12px; font-size: 14px; font-family: 'Sora', sans-serif; outline: none; background: white; transition: border 0.2s; }
.search-input:focus { border-color: #0ea5e9; }
.page-header { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; color: #0f172a; }
.count-badge { background: #e0f2fe; color: #0284c7; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
.empty { color: #94a3b8; font-size: 14px; }

.list-stack { display: flex; flex-direction: column; gap: 10px; }
.list-row { display: flex; justify-content: space-between; align-items: center; background: white; border-radius: 12px; padding: 14px 20px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); gap: 12px; flex-wrap: wrap; }
.row-info { display: flex; align-items: center; gap: 12px; }
.avatar-sm { width: 38px; height: 38px; background: #0ea5e9; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; font-size: 14px; flex-shrink: 0; }
.avatar-sm.av-red { background: #fee2e2; color: #dc2626; }
.row-name { font-size: 14px; font-weight: 600; color: #0f172a; }
.row-name.txt-red { color: #dc2626; text-decoration: line-through; }
.row-sub { font-size: 12px; color: #94a3b8; margin-top: 2px; display: flex; align-items: center; }
.row-actions { display: flex; gap: 8px; }

.table-wrap { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
table { width: 100%; border-collapse: collapse; }
thead tr { background: #f8fafc; }
th { padding: 13px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 13px 16px; font-size: 13px; color: #334155; border-top: 1px solid #f1f5f9; }

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge.approved { background: #dcfce7; color: #16a34a; }
.badge.rejected { background: #fee2e2; color: #dc2626; }
.badge.pending { background: #fef9c3; color: #ca8a04; }
.badge.applied { background: #e0f2fe; color: #0284c7; }
.badge.shortlisted { background: #dcfce7; color: #16a34a; }
.badge.waitlisted { background: #fef9c3; color: #ca8a04; }

.btn-success { padding: 7px 14px; background: #dcfce7; color: #16a34a; border: 1.5px solid #bbf7d0; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-success:hover { background: #bbf7d0; }
.btn-danger { padding: 7px 14px; background: #fee2e2; color: #dc2626; border: 1.5px solid #fecaca; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-danger:hover { background: #fecaca; }

.btn-view { padding: 7px 14px; background: #e0f2fe; color: #0284c7; border: 1.5px solid #bae6fd; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-view:hover { background: #bae6fd; }

/* ── Modal overlay ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.55); backdrop-filter: blur(3px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 24px; }
.modal-box { background: #fff; border-radius: 20px; width: 100%; max-width: 480px; max-height: 88vh; overflow-y: auto; position: relative; box-shadow: 0 24px 80px rgba(0,0,0,0.22); }
.modal-close { position: absolute; top: 14px; right: 14px; background: #f1f5f9; border: none; border-radius: 50%; width: 28px; height: 28px; font-size: 13px; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; z-index: 10; transition: background 0.15s; }
.modal-close:hover { background: #e2e8f0; color: #0f172a; }

/* ── Loading ── */
.modal-loading { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 56px 0; color: #94a3b8; font-size: 14px; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #0ea5e9; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Profile modal header ── */
.pm-header { display: flex; align-items: flex-start; gap: 16px; padding: 28px 28px 20px; }
.pm-avatar { width: 62px; height: 62px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; color: white; flex-shrink: 0; }
.pm-avatar-purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); }
.pm-avatar-blue   { background: linear-gradient(135deg, #0ea5e9, #38bdf8); }
.pm-header-info { display: flex; flex-direction: column; gap: 4px; padding-top: 4px; }
.pm-name { font-size: 20px; font-weight: 700; color: #0f172a; }
.pm-dept { font-size: 13px; color: #64748b; }
.pm-status-badge { display: inline-block; margin-top: 4px; padding: 3px 11px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-active      { background: #dcfce7; color: #16a34a; }
.status-blacklisted { background: #fee2e2; color: #dc2626; }
.status-pending     { background: #fef9c3; color: #ca8a04; }

/* ── Info list ── */
.pm-info-list { padding: 0 28px; border-top: 1px solid #f1f5f9; }
.pm-info-row { display: flex; align-items: center; gap: 12px; padding: 13px 0; border-bottom: 1px solid #f8fafc; font-size: 14px; }
.pm-info-icon { font-size: 16px; width: 22px; text-align: center; flex-shrink: 0; }
.pm-info-label { color: #94a3b8; font-size: 13px; width: 110px; flex-shrink: 0; }
.pm-info-value { color: #0f172a; font-weight: 500; flex: 1; }

/* ── Section (table area) ── */
.pm-section { padding: 20px 28px 0; }
.pm-section-title { font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 10px; }
.pm-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 4px; }
.pm-table th { text-align: left; padding: 8px 10px; background: #f8fafc; color: #94a3b8; font-size: 11px; font-weight: 600; text-transform: uppercase; border-radius: 6px; }
.pm-table td { padding: 10px 10px; color: #334155; border-bottom: 1px solid #f1f5f9; }
.pm-empty { padding: 20px 28px; color: #94a3b8; font-size: 14px; text-align: center; }

/* ── Pills ── */
.pill { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.pill-green       { background: #dcfce7; color: #16a34a; }
.pill-gray        { background: #f1f5f9; color: #64748b; }
.pill-applied     { background: #e0f2fe; color: #0284c7; }
.pill-shortlisted { background: #dcfce7; color: #16a34a; }
.pill-rejected    { background: #fee2e2; color: #dc2626; }
.pill-waitlisted  { background: #fef9c3; color: #ca8a04; }

/* ── Footer ── */
.pm-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 20px 28px 24px; border-top: 1px solid #f1f5f9; margin-top: 20px; }
.pm-btn-close { padding: 9px 22px; background: white; color: #475569; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.15s; }
.pm-btn-close:hover { background: #f8fafc; }
.pm-btn-blacklist { padding: 9px 22px; background: #fee2e2; color: #dc2626; border: 1.5px solid #fecaca; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.15s; }
.pm-btn-blacklist:hover { background: #fecaca; }
.pm-btn-unblacklist { padding: 9px 22px; background: #dcfce7; color: #16a34a; border: 1.5px solid #bbf7d0; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.15s; }
.pm-btn-unblacklist:hover { background: #bbf7d0; }

.msg-error { color: #dc2626; font-size: 13px; margin-top: 16px; }

.sp-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.5); backdrop-filter: blur(4px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.sp-card { background: #fff; border-radius: 20px; width: 100%; max-width: 420px; max-height: 90vh; overflow-y: auto; position: relative; box-shadow: 0 32px 80px rgba(0,0,0,0.22); font-family: 'Sora', sans-serif; }

/* close button */
.sp-close { position: absolute; top: 14px; right: 14px; width: 28px; height: 28px; border-radius: 50%; border: none; background: #f1f5f9; color: #64748b; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; }
.sp-close:hover { background: #e2e8f0; }

/* loading */
.sp-loading { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 60px 0; color: #94a3b8; font-size: 14px; }
.sp-spinner { width: 30px; height: 30px; border: 3px solid #e2e8f0; border-top-color: #0ea5e9; border-radius: 50%; animation: sp-spin 0.7s linear infinite; }
@keyframes sp-spin { to { transform: rotate(360deg); } }

/* header */
.sp-head { display: flex; align-items: flex-start; gap: 16px; padding: 28px 24px 20px; }
.sp-avatar { width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #38bdf8); color: #fff; font-size: 26px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sp-head-text { display: flex; flex-direction: column; gap: 3px; padding-top: 4px; }
.sp-name { font-size: 20px; font-weight: 700; color: #0f172a; }
.sp-sub  { font-size: 13px; color: #64748b; }
.sp-badge { display: inline-block; margin-top: 6px; padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.sp-badge-green { background: #dcfce7; color: #16a34a; }
.sp-badge-red   { background: #fee2e2; color: #dc2626; }

/* info rows */
.sp-rows { padding: 0 24px; }
.sp-row { display: flex; align-items: center; gap: 14px; padding: 13px 0; border-bottom: 1px solid #f1f5f9; }
.sp-row:last-child { border-bottom: none; }
.sp-row-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 15px; flex-shrink: 0; }
.sp-icon-blue   { background: #e0f2fe; color: #0284c7; }
.sp-icon-red    { background: #fee2e2; color: #dc2626; }
.sp-icon-pink   { background: #fce7f3; color: #db2777; }
.sp-icon-purple { background: #ede9fe; color: #7c3aed; }
.sp-icon-teal   { background: #ccfbf1; color: #0d9488; }
.sp-icon-yellow { background: #fef9c3; color: #ca8a04; }
.sp-row-label { font-size: 13px; color: #94a3b8; width: 80px; flex-shrink: 0; }
.sp-row-val   { font-size: 14px; color: #0f172a; font-weight: 500; }

/* chips / skills section */
.sp-skills-section { padding: 18px 24px 4px; }
.sp-skills-title { font-size: 11px; font-weight: 700; letter-spacing: 0.8px; color: #94a3b8; margin-bottom: 10px; }
.sp-chips-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.sp-chip { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.sp-chip-blue  { background: #e0f2fe; color: #0284c7; }
.sp-chip-green { background: #dcfce7; color: #16a34a; }
.sp-chip-gray  { background: #f1f5f9; color: #64748b; }
.sp-no-apps { font-size: 13px; color: #94a3b8; }

/* footer */
.sp-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 20px 24px 24px; border-top: 1px solid #f1f5f9; margin-top: 20px; }
.sp-btn-close { padding: 9px 20px; background: #fff; color: #475569; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; }
.sp-btn-close:hover { background: #f8fafc; }
.sp-btn-blacklist { padding: 9px 20px; background: #fee2e2; color: #dc2626; border: 1.5px solid #fecaca; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; font-family: 'Sora', sans-serif; }
.sp-btn-blacklist:hover { background: #fecaca; }
.sp-btn-unblacklist { padding: 9px 20px; background: #dcfce7; color: #16a34a; border: 1.5px solid #bbf7d0; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; font-family: 'Sora', sans-serif; }
.sp-btn-unblacklist:hover { background: #bbf7d0; }

/* Stats Dashboard */
.stats-section-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 14px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
.stat-card { border-radius: 16px; padding: 22px 20px; display: flex; flex-direction: column; gap: 6px; }
.stat-icon { font-size: 22px; }
.stat-val { font-size: 32px; font-weight: 700; line-height: 1; }
.stat-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; opacity: 0.7; }
.stat-card.indigo { background: #eef2ff; color: #4338ca; }
.stat-card.sky    { background: #e0f2fe; color: #0369a1; }
.stat-card.emerald{ background: #ecfdf5; color: #065f46; }
.stat-card.amber  { background: #fffbeb; color: #92400e; }
.stat-card.green  { background: #f0fdf4; color: #15803d; }
.stat-card.yellow { background: #fefce8; color: #a16207; }
.stat-card.teal   { background: #f0fdfa; color: #0f766e; }
.stat-card.red    { background: #fff1f2; color: #be123c; }
.stat-card.blue   { background: #eff6ff; color: #1d4ed8; }
.stat-card.orange { background: #fff7ed; color: #c2410c; }
.stat-card.lime   { background: #f7fee7; color: #3f6212; }
.stat-card.rose   { background: #fff1f2; color: #9f1239; }
.quick-links { display: flex; flex-wrap: wrap; gap: 10px; }
.quick-btn { padding: 10px 18px; background: white; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 13px; font-weight: 600; color: #334155; cursor: pointer; font-family: 'Sora', sans-serif; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
.quick-btn:hover { background: #f0f9ff; border-color: #0ea5e9; color: #0ea5e9; }
.ql-badge { background: #ef4444; color: white; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 20px; }

/* Export */
.export-btns { display: flex; gap: 8px; margin-left: auto; }
.btn-export-csv { padding: 8px 16px; background: #f0fdf4; color: #15803d; border: 1.5px solid #bbf7d0; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-export-csv:hover { background: #dcfce7; }
.btn-export-pdf { padding: 8px 16px; background: #fff1f2; color: #be123c; border: 1.5px solid #fecaca; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-export-pdf:hover { background: #ffe4e6; }

/* App filters  */
.app-filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
.filter-input { padding: 9px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 13px; font-family: 'Sora', sans-serif; outline: none; background: white; min-width: 180px; transition: border 0.2s; }
.filter-input:focus { border-color: #0ea5e9; }
.filter-select { padding: 9px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 13px; font-family: 'Sora', sans-serif; outline: none; background: white; cursor: pointer; transition: border 0.2s; }
.filter-select:focus { border-color: #0ea5e9; }
.filter-clear { padding: 9px 14px; background: #f1f5f9; color: #64748b; border: none; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.filter-clear:hover { background: #e2e8f0; }

/*  Edit Application Modal */
.btn-edit { padding: 6px 12px; background: #f5f3ff; color: #7c3aed; border: 1.5px solid #ddd6fe; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.btn-edit:hover { background: #ede9fe; }
.ae-field { margin-bottom: 16px; }
.ae-label { display: block; font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.ae-select { width: 100%; padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-family: 'Sora', sans-serif; outline: none; background: white; cursor: pointer; transition: border 0.2s; }
.ae-select:focus { border-color: #7c3aed; }
.ae-input { width: 100%; padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-family: 'Sora', sans-serif; outline: none; background: white; transition: border 0.2s; }
.ae-input:focus { border-color: #7c3aed; }
.ae-btn-cancel { padding: 9px 20px; background: white; color: #475569; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; }
.ae-btn-cancel:hover { background: #f8fafc; }
.ae-btn-save { padding: 9px 22px; background: #7c3aed; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.ae-btn-save:hover { background: #6d28d9; }
.ae-btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.sp-resume-btn { padding: 4px 12px; background: #ede9fe; color: #7c3aed; border: 1.5px solid #ddd6fe; border-radius: 20px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: 'Sora', sans-serif; transition: background 0.2s; }
.sp-resume-btn:hover { background: #ddd6fe; }

@media (max-width: 768px) {
  .sidebar { display: none; }
  .main { margin-left: 0; padding: 20px; }
}
</style>