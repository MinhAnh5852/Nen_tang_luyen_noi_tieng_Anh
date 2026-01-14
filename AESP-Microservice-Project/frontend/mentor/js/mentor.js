/* =========================================================
   CONFIG (DEMO)
========================================================= */
const DEMO_MODE = true;
const API_BASE  = "http://localhost:5000";
const TOKEN_KEY = "token";
const token     = localStorage.getItem(TOKEN_KEY);
function canUseApi() { return !DEMO_MODE && !!token; }

/* =========================================================
   I18N
========================================================= */
let currentLang = localStorage.getItem("lang") || "vi";

const I18N = {
  vi: {
    roleMentor:"Mentor",
    groupDashboard:"DASHBOARD",
    groupManage:"QUẢN LÝ",
    menuLearners:"Học viên",
    menuProgress:"Tiến độ",
    menuFeedback:"Phản hồi",
    menuTasks:"Giao bài",
    menuRanking:"Xếp hạng",
    menuResources:"Tài liệu",
    menuTopics:"Chủ đề",
    menuSubmissions:"Bài nộp",
    menuSettings:"Cài đặt",

    pageTitle:"Bảng Điều Khiển Mentor",
    mentorProfile:"Hồ Sơ Mentor",

    ddInfo:"Thông tin cá nhân",
    ddAvailability:"Lịch & thời gian rảnh",
    ddSecurity:"Đổi mật khẩu",
    ddLogout:"Đăng xuất",

    alertsLabel:"Cảnh báo:",
    alertsText:"3 học viên chưa luyện tập 7 ngày. 2 học viên cần phản hồi.",

    learnersTitle:"Học Viên Của Tôi",
    phSearch:"Tìm theo tên hoặc email",
    filterStatus:"Trạng thái",
    optAll:"All Status",
    optActive:"Active",
    optInactive:"Inactive",

    thId:"ID",
    thName:"Tên",
    thLevel:"Cấp độ",
    thLastPractice:"Lần luyện gần nhất",
    thAvg:"Điểm TB",
    thWeak:"Kỹ năng yếu",
    thStatus:"Trạng thái",
    thActions:"Hành động",
    noLearners:"Chưa có học viên nào được phân công.",

    btnView:"Xem",
    btnSendFeedback:"Gửi nhận xét",
    btnAssignTask:"Giao bài",
    btnOpen:"Mở",

    progressTitle:"Tiến Độ Học Viên",
    selectLearner:"Chọn học viên",
    progressHint:"Chọn học viên để xem tiến độ.",
    skillPron:"Phát âm",
    skillFlu:"Trôi chảy",
    skillVocab:"Từ vựng",
    skillGram:"Ngữ pháp",
    recentPractice:"Các lần luyện nói gần đây",
    colDate:"Ngày",
    colScore:"Điểm",

    feedbackTitle:"Phản Hồi AI",
    feedbackHint:"Chọn học viên (mục Tiến độ) để xem phản hồi AI.",
    fbForPrefix:"Phản hồi cho:",
    fbErrTitle:"Lỗi phát âm phát hiện",
    fbSugTitle:"Gợi ý sửa lỗi",
    fbVocabTitle:"Gợi ý từ vựng thay thế",
    fbPracticeTitle:"Câu luyện tập",
    fbClarityTitle:"Gợi ý diễn đạt rõ ràng & tự tin",
    fbVocabTipsTitle:"Mẹo học từ vựng / cụm từ",
    fbNativeTipsTitle:"Kinh nghiệm giao tiếp với người bản ngữ",

    tasksTitle:"Giao Bài",
    assignNewTask:"Giao Bài Mới",
    task1:"Bài 1: Luyện phát âm cho học viên 1",
    task2:"Bài 2: Ôn từ vựng cho học viên 2",

    rankingTitle:"Xếp Hạng Học Viên",
    rankingTopTitle:"Top học viên theo điểm TB",
    rankingNeedHelpTitle:"Học viên cần hỗ trợ thêm",
    rankingNoteTitle:"Gợi ý đánh giá",
    rankingNote:"Dựa trên điểm TB + trạng thái luyện tập gần đây, mentor có thể ưu tiên phản hồi cho học viên thấp điểm hoặc lâu không luyện.",
    avgScoreLabel:"Điểm TB",
    statusLabel:"Trạng thái",
    weakLabel:"Kỹ năng yếu",

    resourcesTitle:"Tài Liệu Hỗ Trợ",
    resourceAll:"Tất cả kỹ năng",
    resPron:"Phát âm",
    resVocab:"Từ vựng",
    resGram:"Ngữ pháp",
    resFlu:"Trôi chảy",
    resColType:"Kỹ năng",
    resColTitle:"Tài liệu",
    resColDesc:"Mô tả",
    resColAction:"Hành động",
    resourceHint:"Mentor có thể gửi link/tài liệu phù hợp theo “Kỹ năng yếu” của từng học viên.",
    noResource:"Không có tài liệu phù hợp.",

    topicsTitle:"Chủ Đề & Tình Huống Giao Tiếp",
    topicSelectLearner:"Chọn học viên",
    topicSelectTopic:"Chọn chủ đề",
    topicAssignBtn:"Giao chủ đề",
    topicLibraryTitle:"Thư viện chủ đề",
    topicAssignedTitle:"Chủ đề đã giao (demo)",
    noAssignedTopics:"Chưa giao chủ đề nào.",
    msgPickBoth:"Vui lòng chọn học viên và chủ đề.",
    msgAssignedPrefix:"Đã giao chủ đề",

    submissionsTitle:"Bài Nói Mới Nộp",
    subColLearner:"Học viên",
    subColTopic:"Chủ đề",
    subColTime:"Thời gian nộp",
    subColAction:"Hành động",
    submissionsHint:"Sau khi học viên nộp bài nói, mentor có thể nghe và phản hồi ngay để học viên tiến bộ nhanh hơn.",
    noSubmissions:"Chưa có bài nộp mới.",
    btnListen:"Nghe & phản hồi",
    btnReviewed:"Đánh dấu đã xem",
    msgReviewed:"Đã đánh dấu đã xem.",
    msgListenDemo:"Demo: đang mở bài nói và chuẩn bị phản hồi.",

    settingsTitle:"Cài Đặt",
    settingsDesc:"Tuỳ chỉnh giao diện, ngôn ngữ và nhắc nhở.",
    setTheme:"Đổi theme",
    setLang:"Đổi ngôn ngữ",
    setReminder:"Bật/tắt nhắc nhở",
    setAvail:"Lịch & thời gian rảnh",
    saveTheme:"Lưu theme",
    saveLang:"Lưu ngôn ngữ",
    saveReminder:"Lưu nhắc nhở",

    modalInfoTitle:"Thông tin cá nhân",
    modalAvailabilityTitle:"Lịch & thời gian rảnh",
    modalSecurityTitle:"Đổi mật khẩu (demo)",
    btnClose:"Đóng",
    btnCancel:"Hủy",
    btnSave:"Lưu",
    btnChangePass:"Đổi mật khẩu",
    msgSavedProfile:"Đã lưu hồ sơ mentor!",
    msgSavedAvail:"Đã lưu lịch rảnh!",
    msgPassMismatch:"Mật khẩu mới không khớp!",
    msgPassOk:"Demo: Đổi mật khẩu thành công (bạn nối API sau).",
    msgLoggedOut:"Đã đăng xuất (đã xoá token).",
    msgSavedTheme:"Đã lưu theme!",
    msgSavedLang:"Đã lưu ngôn ngữ!",
    msgSavedReminder:"Đã lưu nhắc nhở!"
  },

  en: {
    roleMentor:"Mentor",
    groupDashboard:"DASHBOARD",
    groupManage:"MANAGEMENT",
    menuLearners:"Learners",
    menuProgress:"Progress",
    menuFeedback:"Feedback",
    menuTasks:"Tasks",
    menuRanking:"Ranking",
    menuResources:"Resources",
    menuTopics:"Topics",
    menuSubmissions:"Submissions",
    menuSettings:"Settings",

    pageTitle:"Mentor Dashboard",
    mentorProfile:"Mentor Profile",

    ddInfo:"Personal info",
    ddAvailability:"Availability",
    ddSecurity:"Change password",
    ddLogout:"Logout",

    alertsLabel:"Alerts:",
    alertsText:"3 learners haven't practiced for 7 days. 2 learners need feedback.",

    learnersTitle:"My Learners",
    phSearch:"Search by name or email",
    filterStatus:"Status",
    optAll:"All Status",
    optActive:"Active",
    optInactive:"Inactive",

    thId:"ID",
    thName:"Name",
    thLevel:"Level",
    thLastPractice:"Last practice",
    thAvg:"Avg score",
    thWeak:"Weak skill",
    thStatus:"Status",
    thActions:"Actions",
    noLearners:"No learners assigned.",

    btnView:"View",
    btnSendFeedback:"Send feedback",
    btnAssignTask:"Assign task",
    btnOpen:"Open",

    progressTitle:"Learner Progress",
    selectLearner:"Select a learner",
    progressHint:"Select a learner to view progress.",
    skillPron:"Pronunciation",
    skillFlu:"Fluency",
    skillVocab:"Vocabulary",
    skillGram:"Grammar",
    recentPractice:"Recent speaking practices",
    colDate:"Date",
    colScore:"Score",

    feedbackTitle:"AI Feedback",
    feedbackHint:"Select a learner (in Progress) to see AI feedback.",
    fbForPrefix:"Feedback for:",
    fbErrTitle:"Pronunciation issues found",
    fbSugTitle:"Fix suggestions",
    fbVocabTitle:"Vocabulary suggestions",
    fbPracticeTitle:"Practice sentence",
    fbClarityTitle:"Clarity & confidence tips",
    fbVocabTipsTitle:"Vocabulary / phrases tips",
    fbNativeTipsTitle:"Tips for talking to natives",

    tasksTitle:"Tasks",
    assignNewTask:"Assign new task",
    task1:"Task 1: Practice pronunciation for learner 1",
    task2:"Task 2: Review vocabulary for learner 2",

    rankingTitle:"Learner Ranking",
    rankingTopTitle:"Top learners by avg score",
    rankingNeedHelpTitle:"Learners who need more support",
    rankingNoteTitle:"Evaluation tips",
    rankingNote:"Based on avg score + recent practice status, prioritize feedback for low-score or inactive learners.",
    avgScoreLabel:"Avg score",
    statusLabel:"Status",
    weakLabel:"Weak skill",

    resourcesTitle:"Resources",
    resourceAll:"All skills",
    resPron:"Pronunciation",
    resVocab:"Vocabulary",
    resGram:"Grammar",
    resFlu:"Fluency",
    resColType:"Skill",
    resColTitle:"Resource",
    resColDesc:"Description",
    resColAction:"Action",
    resourceHint:"Mentor can share suitable links/resources based on each learner's weak skill.",
    noResource:"No matching resources.",

    topicsTitle:"Topics & Speaking Scenarios",
    topicSelectLearner:"Select learner",
    topicSelectTopic:"Select topic",
    topicAssignBtn:"Assign topic",
    topicLibraryTitle:"Topic library",
    topicAssignedTitle:"Assigned topics (demo)",
    noAssignedTopics:"No topics assigned yet.",
    msgPickBoth:"Please select a learner and a topic.",
    msgAssignedPrefix:"Assigned topic",

    submissionsTitle:"New Submissions",
    subColLearner:"Learner",
    subColTopic:"Topic",
    subColTime:"Submitted at",
    subColAction:"Action",
    submissionsHint:"After learners submit, you can listen and reply quickly to help them improve faster.",
    noSubmissions:"No new submissions.",
    btnListen:"Listen & feedback",
    btnReviewed:"Mark reviewed",
    msgReviewed:"Marked as reviewed.",
    msgListenDemo:"Demo: opening submission and preparing feedback.",

    settingsTitle:"Settings",
    settingsDesc:"Customize theme, language and reminders.",
    setTheme:"Theme",
    setLang:"Language",
    setReminder:"Reminders",
    setAvail:"Availability",
    saveTheme:"Save theme",
    saveLang:"Save language",
    saveReminder:"Save reminders",

    modalInfoTitle:"Personal info",
    modalAvailabilityTitle:"Availability",
    modalSecurityTitle:"Change password (demo)",
    btnClose:"Close",
    btnCancel:"Cancel",
    btnSave:"Save",
    btnChangePass:"Change password",
    msgSavedProfile:"Saved mentor profile!",
    msgSavedAvail:"Saved availability!",
    msgPassMismatch:"New passwords do not match!",
    msgPassOk:"Demo: Password changed successfully (connect API later).",
    msgLoggedOut:"Logged out (token removed).",
    msgSavedTheme:"Saved theme!",
    msgSavedLang:"Saved language!",
    msgSavedReminder:"Saved reminders!"
  }
};

function t(key){
  const dict = I18N[currentLang] || I18N.en;
  return dict[key] ?? key;
}

function applyLanguage(){
  document.documentElement.lang = currentLang === "vi" ? "vi" : "en";

  document.querySelectorAll("[data-i18n]").forEach(el=>{
    const key = el.getAttribute("data-i18n");
    el.textContent = t(key);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(el=>{
    const key = el.getAttribute("data-i18n-placeholder");
    el.setAttribute("placeholder", t(key));
  });

  const alertsText = document.getElementById("alertsText");
  if (alertsText) alertsText.textContent = t("alertsText");

  const tasksUl = document.getElementById("tasksUl");
  if (tasksUl) tasksUl.innerHTML = `<li>${t("task1")}</li><li>${t("task2")}</li>`;
}

/* =========================================================
   STATE + DATA
========================================================= */
let learnersCache = [];
let progressChart = null;
let assignedTopicsState = [];
let submissionsState = [];
let currentSection = "learners";

function escapeHtml(str){
  return String(str ?? '').replace(/[&<>"']/g, s => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'
  }[s]));
}

function getMockLearners(){
  return [
    { id: 1, email: "learner1@example.com", name: "Nguyễn Văn A", level: "B1", lastPractice: "2026-01-05", avgScore: 78, weakSkill: "Pronunciation", status: "active" },
    { id: 2, email: "learner2@example.com", name: "Trần Thị B", level: "A2", lastPractice: "2025-12-28", avgScore: 62, weakSkill: "Vocabulary", status: "inactive" },
    { id: 3, email: "learner3@example.com", name: "Lê Minh C", level: "B2", lastPractice: "2026-01-09", avgScore: 85, weakSkill: "Grammar", status: "active" },
    { id: 4, email: "learner4@example.com", name: "Phạm Thị D", level: "B1", lastPractice: "2025-12-20", avgScore: 55, weakSkill: "Fluency", status: "inactive" },
  ];
}

const RESOURCES = [
  { skill: "Pronunciation", title: "/θ/ vs /t/", desc_vi: "Luyện phân biệt âm /θ/ (think) và /t/ (tin).", desc_en: "Practice distinguishing /θ/ (think) vs /t/ (tin).", url: "https://www.youtube.com/results?search_query=theta+sound+practice" },
  { skill: "Pronunciation", title: "Shadowing technique", desc_vi: "Luyện bắt chước ngữ điệu theo video/audio.", desc_en: "Mimic intonation using video/audio.", url: "https://www.youtube.com/results?search_query=english+shadowing+technique" },
  { skill: "Vocabulary", title: "Basic collocations", desc_vi: "Học cụm từ đi kèm tự nhiên: make a decision, take a break...", desc_en: "Learn natural collocations: make a decision, take a break...", url: "https://www.oxfordlearnersdictionaries.com/" },
  { skill: "Grammar", title: "Quick tenses review", desc_vi: "Tóm tắt các thì thường dùng khi nói.", desc_en: "Quick review of common tenses for speaking.", url: "https://www.perfect-english-grammar.com/" },
  { skill: "Fluency", title: "Speaking frameworks", desc_vi: "Mẫu trả lời 2–3 ý: opinion → reason → example.", desc_en: "A 2–3 point template: opinion → reason → example.", url: "https://www.youtube.com/results?search_query=speaking+framework+opinion+reason+example" },
];

const TOPICS = [
  { key: "airport", vi: "Sân bay (Airport)", en: "Airport" },
  { key: "interview", vi: "Phỏng vấn xin việc (Job interview)", en: "Job interview" },
  { key: "restaurant", vi: "Nhà hàng (Restaurant)", en: "Restaurant" },
  { key: "hotel", vi: "Khách sạn (Hotel check-in)", en: "Hotel check-in" },
  { key: "smalltalk", vi: "Giao tiếp xã giao (Small talk)", en: "Small talk" },
];

function initDemoSubmissions(){
  submissionsState = [
    { learnerId: 2, topicKey: "restaurant", submittedAt: "2026-01-12 20:10" },
    { learnerId: 4, topicKey: "interview", submittedAt: "2026-01-12 19:30" },
  ];
}

/* =========================================================
   SECTION LOADER
========================================================= */
let sectionHost = null;
const sectionFiles = {
  learners: "./sections/learners.html",
  progress: "./sections/progress.html",
  feedback: "./sections/feedback.html",
  tasks: "./sections/tasks.html",
  ranking: "./sections/ranking.html",
  resources: "./sections/resources.html",
  topics: "./sections/topics.html",
  submissions: "./sections/submissions.html",
  settings: "./sections/settings.html"
};

function setActiveSidebar(section){
  document.querySelectorAll(".sb-link[data-section]").forEach(a=>{
    a.classList.toggle("active", a.dataset.section === section);
  });
}

/* ======= UI FIX: đồng bộ style input/select + fix spacing hàng control ======= */
function applyControlLook(root){
  const scope = root || document;
  const controls = scope.querySelectorAll("select, input[type='text'], input[type='search'], input:not([type]), textarea, input[type='time']");
  controls.forEach(el=>{
    // không đụng button
    if (el.tagName === "BUTTON") return;
    el.style.border = "1px solid var(--border)";
    el.style.borderRadius = "12px";
    el.style.padding = "10px 12px";
    el.style.outline = "none";
    el.style.fontFamily = "inherit";
    el.style.background = "var(--card)";
    el.style.color = "var(--text)";
  });
}

function normalizeControlBars(){
  // Mục tiêu: các row chứa select + button (Topics / Resources / Tasks / Progress)
  const ids = [
    "learnerSelect",         // progress
    "topicLearnerSelect",    // topics
    "topicSelect",           // topics
    "topicAssignBtn",        // topics
    "resourceFilter",        // resources
    "assignNewTaskBtn",      // tasks (nút có thể là id khác tuỳ file)
    "assignNewTaskBtn2",     // dự phòng
    "assignNewTaskBtn3"
  ];

  ids.forEach(id=>{
    const el = document.getElementById(id);
    if (!el) return;
    const parent = el.parentElement;
    if (!parent) return;

    // ép hàng control về cùng kiểu: flex-start + gap, tránh space-between gây “xa”
    parent.style.display = "flex";
    parent.style.alignItems = "center";
    parent.style.justifyContent = "flex-start";
    parent.style.gap = "12px";
    parent.style.flexWrap = "wrap";
  });

  // Nếu file HTML dùng wrapper khác (một div chung chứa 2 select + button),
  // mình quét các block có 2+ select và 1 button rồi ép lại.
  document.querySelectorAll(".content-card, .container, #sectionHost").forEach(box=>{
    box.querySelectorAll("div").forEach(d=>{
      const selects = d.querySelectorAll(":scope > select").length;
      const btns = d.querySelectorAll(":scope > button, :scope > a.btn").length;
      if (selects >= 1 && btns >= 1){
        const st = getComputedStyle(d);
        // chỉ can thiệp nếu nó đang space-between hoặc justify-content gây xa
        if (st.display.includes("flex")){
          d.style.justifyContent = "flex-start";
          d.style.gap = d.style.gap || "12px";
          d.style.flexWrap = "wrap";
          d.style.alignItems = "center";
        }
      }
    });
  });

  // Nút "Giao bài mới" trong Tasks: nếu nằm trong header có justify space-between -> kéo lại cho gần
  const assignBtn = document.getElementById("assignNewTaskBtn") || document.querySelector("[data-role='assignNewTaskBtn']");
  if (assignBtn && assignBtn.parentElement){
    const p = assignBtn.parentElement;
    p.style.display = "flex";
    p.style.alignItems = "center";
    p.style.justifyContent = "flex-start";
    p.style.gap = "12px";
    p.style.flexWrap = "wrap";
  }
}

async function loadSection(section){
  currentSection = section || "learners";
  const file = sectionFiles[currentSection] || sectionFiles.learners;

  setActiveSidebar(currentSection);

  let html = "";
  try{
    const res = await fetch(file);
    if (!res.ok) throw new Error(`Fetch failed: ${file} (${res.status})`);
    html = await res.text();
  }catch(err){
    console.error(err);
    html = `
      <div class="content-card">
        <h2 style="margin:0 0 8px; font-weight:900;">Section load error</h2>
        <p class="muted">Không tải được: <b>${escapeHtml(file)}</b>. Hãy kiểm tra đường dẫn + có file trong thư mục sections.</p>
      </div>
    `;
  }

  sectionHost.innerHTML = html;

  applyLanguage();
  applyTheme();                 // đảm bảo theme áp lại sau khi load section
  applyControlLook(sectionHost);
  normalizeControlBars();

  if (currentSection === "learners") initLearnersSection();
  if (currentSection === "progress") initProgressSection();
  if (currentSection === "feedback") initFeedbackSection();
  if (currentSection === "tasks") initTasksSection();
  if (currentSection === "ranking") initRankingSection();
  if (currentSection === "resources") initResourcesSection();
  if (currentSection === "topics") initTopicsSection();
  if (currentSection === "submissions") initSubmissionsSection();
  if (currentSection === "settings") initSettingsSection();

  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelectorAll(".sb-link[data-section]").forEach(a=>{
  a.addEventListener("click", (e)=>{
    e.preventDefault();
    loadSection(a.dataset.section);
  });
});

/* =========================================================
   Learners
========================================================= */
function getFilteredLearners(){
  const qEl = document.getElementById("search");
  const statusEl = document.getElementById("statusFilter");

  const q = (qEl ? qEl.value : "").trim().toLowerCase();
  const status = statusEl ? statusEl.value : "all"; // all|active|inactive

  return learnersCache.filter(l=>{
    const text = `${l.name} ${l.email}`.toLowerCase();
    const okSearch = !q || text.includes(q);
    const okStatus = (status === "all") ? true : (l.status === status);
    return okSearch && okStatus;
  });
}

function renderLearners(){
  const tbody = document.querySelector("#learnersTable tbody");
  const noData = document.getElementById("noData");
  if (!tbody) return;

  const list = getFilteredLearners();
  tbody.innerHTML = "";

  if (!list.length){
    if (noData) noData.style.display = "block";
    return;
  }
  if (noData) noData.style.display = "none";

  list.forEach(l=>{
    const tr = document.createElement("tr");
    const pillClass = (l.status === "active") ? "pill pill-success" : "pill pill-muted";
    tr.innerHTML = `
      <td>${escapeHtml(l.id)}</td>
      <td>
        <div style="font-weight:900;">${escapeHtml(l.name)}</div>
        <div style="color:var(--muted); font-size:12px;">${escapeHtml(l.email)}</div>
      </td>
      <td>${escapeHtml(l.level)}</td>
      <td>${escapeHtml(l.lastPractice)}</td>
      <td>${escapeHtml(l.avgScore)}</td>
      <td>${escapeHtml(l.weakSkill)}</td>
      <td><span class="${pillClass}">${escapeHtml(l.status)}</span></td>
      <td>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn btn-primary btn-sm" data-act="view" data-id="${l.id}">${escapeHtml(t("btnView"))}</button>
          <button class="btn btn-outline btn-sm" data-act="sendfb" data-id="${l.id}">${escapeHtml(t("btnSendFeedback"))}</button>
          <button class="btn btn-outline btn-sm" data-act="task" data-id="${l.id}">${escapeHtml(t("btnAssignTask"))}</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button[data-act]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const id = btn.dataset.id;
      const act = btn.dataset.act;
      if (act === "view"){
        loadSection("progress").then(()=>{
          const sel = document.getElementById("learnerSelect");
          if (sel){ sel.value = String(id); viewProgress(id); }
        });
      }
      if (act === "sendfb"){
        loadSection("feedback").then(()=> alert(`${t("btnSendFeedback")}: #${id}`));
      }
      if (act === "task"){
        loadSection("tasks").then(()=> alert(`${t("btnAssignTask")}: #${id}`));
      }
    });
  });

  applyControlLook(document); // đảm bảo input/select trong learners cũng đẹp
}

function initLearnersSection(){
  const search = document.getElementById("search");
  const status = document.getElementById("statusFilter");
  if (search) search.addEventListener("keyup", renderLearners);
  if (status) status.addEventListener("change", renderLearners);

  const optAll = document.getElementById("optAll");
  const optActive = document.getElementById("optActive");
  const optInactive = document.getElementById("optInactive");
  if (optAll) optAll.textContent = t("optAll");
  if (optActive) optActive.textContent = t("optActive");
  if (optInactive) optInactive.textContent = t("optInactive");

  renderLearners();
}

/* =========================================================
   Progress + Chart
========================================================= */
function rand(a,b){ return Math.floor(Math.random()*(b-a+1))+a; }
function mockProgress(){
  const history = [
    { date: "2025-12-28", score: 60 },
    { date: "2026-01-04", score: 68 },
    { date: "2026-01-07", score: 72 },
    { date: "2026-01-09", score: 78 },
    { date: "2026-01-11", score: 81 }
  ];
  return {
    pronunciation: rand(55, 95),
    fluency: rand(50, 92),
    vocabulary: rand(52, 94),
    grammar: rand(48, 90),
    history
  };
}

function viewProgress(learnerId){
  const learner = learnersCache.find(x => String(x.id) === String(learnerId));
  const p = mockProgress();
  const box = document.getElementById("progressDetails");
  if (!box) return;

  box.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap:10px; margin-bottom:12px;">
      <div class="mini-card" style="background:var(--card);">
        <div style="font-weight:900;">${escapeHtml(t("skillPron"))}</div>
        <div style="color:var(--muted); margin-top:6px; font-weight:800;">${p.pronunciation}%</div>
      </div>
      <div class="mini-card" style="background:var(--card);">
        <div style="font-weight:900;">${escapeHtml(t("skillFlu"))}</div>
        <div style="color:var(--muted); margin-top:6px; font-weight:800;">${p.fluency}%</div>
      </div>
      <div class="mini-card" style="background:var(--card);">
        <div style="font-weight:900;">${escapeHtml(t("skillVocab"))}</div>
        <div style="color:var(--muted); margin-top:6px; font-weight:800;">${p.vocabulary}%</div>
      </div>
      <div class="mini-card" style="background:var(--card);">
        <div style="font-weight:900;">${escapeHtml(t("skillGram"))}</div>
        <div style="color:var(--muted); margin-top:6px; font-weight:800;">${p.grammar}%</div>
      </div>
    </div>

    <div style="padding:12px; border-radius:12px; border:1px solid var(--border); margin-bottom:12px; background:var(--card);">
      <canvas id="progressChart" height="120"></canvas>
    </div>

    <h3 style="margin: 0 0 8px; font-weight:900;">${escapeHtml(t("recentPractice"))}</h3>
    <div class="table-container">
      <table class="data-table">
        <thead><tr><th>${escapeHtml(t("colDate"))}</th><th>${escapeHtml(t("colScore"))}</th></tr></thead>
        <tbody>
          ${p.history.map(h => `<tr><td>${h.date}</td><td>${h.score}</td></tr>`).join("")}
        </tbody>
      </table>
    </div>
  `;

  if (progressChart) progressChart.destroy();
  const canvas = document.getElementById("progressChart");
  if (canvas && window.Chart){
    const ctx = canvas.getContext("2d");
    progressChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: p.history.map(h => h.date),
        datasets: [{
          label: t("colScore"),
          data: p.history.map(h => h.score),
          borderWidth: 2,
          tension: 0.25
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 100 } }
      }
    });
  }

  renderAIFeedback(learner);
}

function initProgressSection(){
  const select = document.getElementById("learnerSelect");
  if (!select) return;

  select.innerHTML = `<option value="">${escapeHtml(t("selectLearner"))}</option>`;
  learnersCache.forEach(l=>{
    const opt = document.createElement("option");
    opt.value = l.id;
    opt.textContent = l.name;
    select.appendChild(opt);
  });

  // fix style/select look
  applyControlLook(document);

  // fix spacing near label/hint (nếu HTML đang space-between)
  if (select.parentElement){
    select.parentElement.style.display = "flex";
    select.parentElement.style.alignItems = "center";
    select.parentElement.style.justifyContent = "flex-start";
    select.parentElement.style.gap = "12px";
    select.parentElement.style.flexWrap = "wrap";
  }

  select.addEventListener("change", function(){
    const id = this.value;
    if (id) viewProgress(id);
  });
}

/* =========================================================
   Feedback
========================================================= */
function renderAIFeedback(learner){
  const hint = document.getElementById("feedbackHint");
  const body = document.getElementById("aiFeedbackBody");
  if (!hint || !body) return;

  hint.style.display = "none";
  body.style.display = "block";

  const name = learner ? `${learner.name} (${learner.email})` : "N/A";
  const fbFor = document.getElementById("fbFor");
  if (fbFor) fbFor.textContent = `${t("fbForPrefix")} ${name}`;

  const errs = [
    `/s/ sound mispronounced in "speech"`,
    `/θ/ sound in "think" needs improvement`
  ];
  const ul = document.getElementById("fbErrList");
  if (ul) ul.innerHTML = errs.map(e => `<li>${escapeHtml(e)}</li>`).join("");

  const sug = document.getElementById("fbSug");
  const vocab = document.getElementById("fbVocab");
  const practice = document.getElementById("fbPractice");
  const clarity = document.getElementById("fbClarity");
  const vocabTips = document.getElementById("fbVocabTips");
  const nativeTips = document.getElementById("fbNativeTips");

  if (sug) sug.textContent = (currentLang === "vi")
    ? `Luyện đặt lưỡi đúng với /s/. Tập từ chậm → tốc độ bình thường.`
    : `Practice correct tongue placement for /s/. Start slow → normal speed.`;

  if (vocab) vocab.textContent = (currentLang === "vi")
    ? `Dùng "believe" thay vì "think" để câu trang trọng hơn.`
    : `Use "believe" instead of "think" to sound more formal.`;

  if (practice) practice.textContent = `"I believe in practicing regularly."`;

  if (clarity) clarity.textContent = (currentLang === "vi")
    ? `Nói theo cấu trúc 3 bước (Ý kiến → Lý do → Ví dụ). Giữ tốc độ vừa phải và ngắt nghỉ sau mỗi ý.`
    : `Use a 3-step structure (Opinion → Reason → Example). Keep a steady pace and pause between points.`;

  if (vocabTips) vocabTips.textContent = (currentLang === "vi")
    ? `Học theo cụm: "take a break", "make a decision". Mỗi ngày 3 cụm + đặt 2 câu ví dụ.`
    : `Learn chunks: "take a break", "make a decision". Daily: 3 chunks + write 2 example sentences.`;

  if (nativeTips) nativeTips.textContent = (currentLang === "vi")
    ? `Ưu tiên rõ ràng hơn hoàn hảo. Nếu không nghe kịp: "Could you repeat that more slowly?"`
    : `Prioritize clarity over perfection. If you can’t catch it: "Could you repeat that more slowly?"`;
}

function initFeedbackSection(){}

/* =========================================================
   Ranking
========================================================= */
function renderRanking(){
  const topBox = document.getElementById("topRankingList");
  const botBox = document.getElementById("bottomRankingList");
  if (!topBox || !botBox) return;

  const sorted = [...learnersCache].sort((a,b) => (b.avgScore||0) - (a.avgScore||0));
  const top = sorted.slice(0, 3);
  const bottom = sorted.slice(-3).reverse();

  function item(l, rank){
    return `
      <div style="display:flex; justify-content:space-between; gap:10px; padding:10px; border-bottom:1px solid var(--border);">
        <div>
          <div style="font-weight:900;">#${rank} ${escapeHtml(l.name)}</div>
          <div style="color:var(--muted); font-size:12px;">${escapeHtml(l.email)}</div>
          <div style="margin-top:6px; display:flex; gap:8px; flex-wrap:wrap;">
            <span class="pill">${escapeHtml(t("statusLabel"))}: ${escapeHtml(l.status)}</span>
            <span class="pill">${escapeHtml(t("weakLabel"))}: ${escapeHtml(l.weakSkill)}</span>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:900; font-size:18px;">${escapeHtml(l.avgScore)}</div>
          <div style="color:var(--muted); font-size:12px;">${escapeHtml(t("avgScoreLabel"))}</div>
          <div style="margin-top:8px;">
            <button class="btn btn-outline btn-sm" data-view="${l.id}">${escapeHtml(t("btnView"))}</button>
          </div>
        </div>
      </div>
    `;
  }

  topBox.innerHTML = top.length ? top.map((l,i)=>item(l, i+1)).join("") : `<p class="muted">—</p>`;
  botBox.innerHTML = bottom.length ? bottom.map((l,i)=>item(l, sorted.length - (bottom.length - 1 - i))).join("") : `<p class="muted">—</p>`;

  document.querySelectorAll("button[data-view]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const id = btn.dataset.view;
      loadSection("progress").then(()=>{
        const sel = document.getElementById("learnerSelect");
        if (sel){ sel.value = String(id); viewProgress(id); }
      });
    });
  });

  applyControlLook(document);
}
function initRankingSection(){ renderRanking(); }

/* =========================================================
   Resources
========================================================= */
function renderResources(){
  const filterEl = document.getElementById("resourceFilter");
  const tbody = document.querySelector("#resourcesTable tbody");
  if (!filterEl || !tbody) return;

  const filter = filterEl.value || "all";
  tbody.innerHTML = "";

  const list = (filter === "all") ? RESOURCES : RESOURCES.filter(r => r.skill === filter);
  list.forEach(r=>{
    const desc = (currentLang === "vi") ? r.desc_vi : r.desc_en;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(r.skill)}</td>
      <td style="font-weight:900;">${escapeHtml(r.title)}</td>
      <td>${escapeHtml(desc)}</td>
      <td><a class="btn btn-outline btn-sm" href="${r.url}" target="_blank" rel="noopener">${escapeHtml(t("btnOpen"))}</a></td>
    `;
    tbody.appendChild(tr);
  });

  if (!list.length){
    const tr = document.createElement("tr");
    tr.innerHTML = `<td colspan="4" style="color:var(--muted);">${escapeHtml(t("noResource"))}</td>`;
    tbody.appendChild(tr);
  }

  // fix UI
  applyControlLook(document);
  normalizeControlBars();
}
function initResourcesSection(){
  const filterEl = document.getElementById("resourceFilter");
  if (filterEl) filterEl.addEventListener("change", renderResources);

  // ép filter không chạy sang tận bên phải (nếu header đang space-between)
  if (filterEl && filterEl.parentElement){
    filterEl.parentElement.style.display = "flex";
    filterEl.parentElement.style.alignItems = "center";
    filterEl.parentElement.style.justifyContent = "flex-start";
    filterEl.parentElement.style.gap = "12px";
    filterEl.parentElement.style.flexWrap = "wrap";
  }

  renderResources();
}

/* =========================================================
   Topics
========================================================= */
function renderTopics(){
  const learnerSel = document.getElementById("topicLearnerSelect");
  const topicSel = document.getElementById("topicSelect");
  const lib = document.getElementById("topicsLibrary");
  const ul = document.getElementById("assignedTopics");
  if (!learnerSel || !topicSel || !lib || !ul) return;

  learnerSel.innerHTML = `<option value="">${escapeHtml(t("topicSelectLearner"))}</option>`;
  learnersCache.forEach(l=>{
    const opt = document.createElement("option");
    opt.value = l.id;
    opt.textContent = l.name;
    learnerSel.appendChild(opt);
  });

  topicSel.innerHTML = `<option value="">${escapeHtml(t("topicSelectTopic"))}</option>`;
  TOPICS.forEach(tp=>{
    const opt = document.createElement("option");
    opt.value = tp.key;
    opt.textContent = (currentLang === "vi") ? tp.vi : tp.en;
    topicSel.appendChild(opt);
  });

  lib.innerHTML = "";
  TOPICS.forEach(tp=>{
    const span = document.createElement("span");
    span.className = "pill";
    span.textContent = (currentLang === "vi") ? tp.vi : tp.en;
    lib.appendChild(span);
  });

  ul.innerHTML = assignedTopicsState.length
    ? assignedTopicsState.map(x => `<li>${escapeHtml(x.text)} — <span style="color:var(--muted);">${escapeHtml(x.learnerName)}</span></li>`).join("")
    : `<li style="color:var(--muted);">${escapeHtml(t("noAssignedTopics"))}</li>`;

  // fix spacing: 2 select + button không bị cách xa
  const assignBtn = document.getElementById("topicAssignBtn");
  if (assignBtn && assignBtn.parentElement){
    const row = assignBtn.parentElement;
    row.style.display = "flex";
    row.style.alignItems = "center";
    row.style.justifyContent = "flex-start";
    row.style.gap = "12px";
    row.style.flexWrap = "wrap";
  }

  applyControlLook(document);
  normalizeControlBars();
}

function assignTopic(){
  const learnerId = document.getElementById("topicLearnerSelect").value;
  const topicKey = document.getElementById("topicSelect").value;
  if (!learnerId || !topicKey){
    alert(t("msgPickBoth"));
    return;
  }
  const learner = learnersCache.find(x => String(x.id) === String(learnerId));
  const tp = TOPICS.find(x => x.key === topicKey);

  const topicText = tp ? ((currentLang === "vi") ? tp.vi : tp.en) : "N/A";
  const learnerName = learner?.name || "N/A";

  assignedTopicsState.unshift({ learnerId, topicKey, text: topicText, learnerName });
  alert(`${t("msgAssignedPrefix")} "${topicText}" → ${learnerName}.`);
  renderTopics();
}
function initTopicsSection(){
  renderTopics();
  const btn = document.getElementById("topicAssignBtn");
  if (btn) btn.onclick = assignTopic;
}

/* =========================================================
   Submissions
========================================================= */
function renderSubmissions(){
  const tbody = document.querySelector("#submissionsTable tbody");
  if (!tbody) return;

  tbody.innerHTML = "";
  if (!submissionsState.length){
    const tr = document.createElement("tr");
    tr.innerHTML = `<td colspan="4" style="color:var(--muted);">${escapeHtml(t("noSubmissions"))}</td>`;
    tbody.appendChild(tr);
    return;
  }

  submissionsState.forEach(s=>{
    const learner = learnersCache.find(x => String(x.id) === String(s.learnerId));
    const tp = TOPICS.find(x => x.key === s.topicKey);
    const learnerName = learner ? `${learner.name} (${learner.email})` : "N/A";
    const topicText = tp ? ((currentLang === "vi") ? tp.vi : tp.en) : "N/A";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight:900;">${escapeHtml(learnerName)}</td>
      <td>${escapeHtml(topicText)}</td>
      <td>${escapeHtml(s.submittedAt)}</td>
      <td style="display:flex; gap:8px; flex-wrap:wrap;">
        <button class="btn btn-primary btn-sm" data-listen="${s.learnerId}" data-topic="${s.topicKey}">${escapeHtml(t("btnListen"))}</button>
        <button class="btn btn-outline btn-sm" data-reviewed="${s.learnerId}" data-topic="${s.topicKey}">${escapeHtml(t("btnReviewed"))}</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button[data-listen]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const id = btn.dataset.listen;
      loadSection("feedback").then(()=>{
        const learner = learnersCache.find(x => String(x.id) === String(id));
        if (learner) renderAIFeedback(learner);
        alert(t("msgListenDemo"));
      });
    });
  });

  tbody.querySelectorAll("button[data-reviewed]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const id = btn.dataset.reviewed;
      const topic = btn.dataset.topic;
      submissionsState = submissionsState.filter(s => !(String(s.learnerId)===String(id) && s.topicKey===topic));
      renderSubmissions();
      alert(t("msgReviewed"));
    });
  });

  applyControlLook(document);
}
function initSubmissionsSection(){ renderSubmissions(); }

/* =========================================================
   Tasks
========================================================= */
function initTasksSection(){
  const ul = document.getElementById("tasksUl");
  if (ul) ul.innerHTML = `<li>${t("task1")}</li><li>${t("task2")}</li>`;

  const btn = document.getElementById("assignNewTaskBtn") || document.querySelector("[data-role='assignNewTaskBtn']");
  if (btn) btn.onclick = ()=>alert(t("assignNewTask"));

  // Fix spacing của nút "Giao bài mới"
  if (btn && btn.parentElement){
    const p = btn.parentElement;
    p.style.display = "flex";
    p.style.alignItems = "center";
    p.style.justifyContent = "flex-start";
    p.style.gap = "12px";
    p.style.flexWrap = "wrap";
  }

  applyControlLook(document);
  normalizeControlBars();
}

/* =========================================================
   SETTINGS (Hoạt động thật)
========================================================= */
const SETTINGS_KEY = "mentor_settings";

function getSettings(){
  return JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}");
}
function setSettings(data){
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(data));
}

/* ====== Dark theme: set CSS vars + inject overrides để chữ rõ ====== */
function ensureThemeStyleTag(){
  let tag = document.getElementById("themeOverrides");
  if (tag) return tag;

  tag = document.createElement("style");
  tag.id = "themeOverrides";
  tag.textContent = `
    /* pill status */
    .pill-success{ border-color: rgba(16,185,129,.35) !important; background: rgba(16,185,129,.12) !important; color: #065f46 !important; }
    .pill-muted{ border-color: rgba(148,163,184,.35) !important; background: rgba(148,163,184,.10) !important; color: #334155 !important; }

    body.theme-dark .pill-success{ color:#a7f3d0 !important; background: rgba(16,185,129,.18) !important; border-color: rgba(16,185,129,.35) !important; }
    body.theme-dark .pill-muted{ color:#e5e7eb !important; background: rgba(148,163,184,.10) !important; border-color: rgba(148,163,184,.25) !important; }

    body.theme-dark .topbar{ background: rgba(15,23,42,.85) !important; border-bottom-color: rgba(148,163,184,.18) !important; backdrop-filter: blur(10px); }
    body.theme-dark .topbar-title{ color: var(--text) !important; }

    body.theme-dark .content-card{ box-shadow: 0 18px 40px rgba(0,0,0,.35) !important; }
    body.theme-dark .alert-card{ background: rgba(250,204,21,.10) !important; border-color: rgba(250,204,21,.22) !important; color: var(--text) !important; }

    body.theme-dark .table-container{ background: rgba(2,6,23,.25) !important; border-color: rgba(148,163,184,.18) !important; }
    body.theme-dark table.data-table{ color: var(--text) !important; }
    body.theme-dark .data-table thead th{
      background: rgba(148,163,184,.08) !important;
      border-bottom-color: rgba(148,163,184,.18) !important;
      color: rgba(226,232,240,.85) !important;
    }
    body.theme-dark .data-table tbody td{ border-bottom-color: rgba(148,163,184,.14) !important; }
    body.theme-dark .data-table tbody tr:hover{ background: rgba(148,163,184,.06) !important; }

    body.theme-dark .modal{ background: var(--card) !important; border-color: rgba(148,163,184,.18) !important; }
    body.theme-dark .modal-hd{ background: rgba(148,163,184,.08) !important; border-bottom-color: rgba(148,163,184,.18) !important; }
    body.theme-dark .modal-ft{ background: var(--card) !important; border-top-color: rgba(148,163,184,.18) !important; }

    body.theme-dark .btn-outline{ background: rgba(2,6,23,.20) !important; color: var(--text) !important; border-color: rgba(148,163,184,.18) !important; }
    body.theme-dark .btn-outline:hover{ background: rgba(148,163,184,.10) !important; }
  `;
  document.head.appendChild(tag);
  return tag;
}

function setCssVarsForTheme(theme){
  const root = document.documentElement;

  if (theme === "dark"){
    root.style.setProperty("--bg", "#0b1220");
    root.style.setProperty("--card", "#0f172a");
    root.style.setProperty("--border", "rgba(148,163,184,.18)");
    root.style.setProperty("--text", "#e5e7eb");
    root.style.setProperty("--muted", "#94a3b8");
    root.style.setProperty("--pill", "rgba(148,163,184,.08)");
  }else{
    // clear to css defaults
    root.style.removeProperty("--bg");
    root.style.removeProperty("--card");
    root.style.removeProperty("--border");
    root.style.removeProperty("--text");
    root.style.removeProperty("--muted");
    root.style.removeProperty("--pill");
  }
}

function applyTheme(){
  ensureThemeStyleTag();

  const s = getSettings();
  const theme = s.theme || "light";
  document.body.classList.toggle("theme-dark", theme === "dark");
  setCssVarsForTheme(theme);

  // re-apply control styles to ensure readable on dark
  applyControlLook(document);
}

function initSettingsSection(){
  const s = getSettings();

  const themeSelect = document.getElementById("themeSelect");
  const saveThemeBtn = document.getElementById("saveThemeBtn");

  const langSelect = document.getElementById("langSelect");
  const saveLangBtn = document.getElementById("saveLangBtn");

  const remindEnable = document.getElementById("remindEnable");
  const remindTime = document.getElementById("remindTime");
  const saveRemindBtn = document.getElementById("saveRemindBtn");

  if (themeSelect) themeSelect.value = s.theme || "light";
  if (langSelect) langSelect.value = currentLang;
  if (remindEnable) remindEnable.checked = !!s.remindEnable;
  if (remindTime) remindTime.value = s.remindTime || "20:00";

  if (saveThemeBtn){
    saveThemeBtn.onclick = ()=>{
      const next = { ...getSettings(), theme: themeSelect ? themeSelect.value : "light" };
      setSettings(next);
      applyTheme();
      alert(t("msgSavedTheme"));
    };
  }

  if (saveLangBtn){
    saveLangBtn.onclick = ()=>{
      currentLang = langSelect ? langSelect.value : "vi";
      localStorage.setItem("lang", currentLang);
      applyLanguage();
      alert(t("msgSavedLang"));
      loadSection(currentSection);
    };
  }

  if (saveRemindBtn){
    saveRemindBtn.onclick = ()=>{
      const next = {
        ...getSettings(),
        remindEnable: !!(remindEnable && remindEnable.checked),
        remindTime: remindTime ? remindTime.value : "20:00"
      };
      setSettings(next);
      alert(t("msgSavedReminder"));
    };
  }

  applyControlLook(document);
  normalizeControlBars();
}

/* =========================================================
   Mentor Profile Modal + Dropdown
========================================================= */
const MENTOR_KEY = "mentor_profile";
function getMentorProfile(){ return JSON.parse(localStorage.getItem(MENTOR_KEY) || "{}"); }
function setMentorProfile(data){ localStorage.setItem(MENTOR_KEY, JSON.stringify(data)); }

/* ======= VN provinces/cities only (no foreign) ======= */
const VN_PROVINCES = [
  "Hà Nội","TP. Hồ Chí Minh","Đà Nẵng","Hải Phòng","Cần Thơ",
  "An Giang","Bà Rịa - Vũng Tàu","Bạc Liêu","Bắc Giang","Bắc Kạn","Bắc Ninh",
  "Bến Tre","Bình Định","Bình Dương","Bình Phước","Bình Thuận",
  "Cà Mau","Cao Bằng","Đắk Lắk","Đắk Nông","Điện Biên","Đồng Nai","Đồng Tháp",
  "Gia Lai","Hà Giang","Hà Nam","Hà Tĩnh","Hải Dương","Hậu Giang","Hòa Bình",
  "Hưng Yên","Khánh Hòa","Kiên Giang","Kon Tum","Lai Châu","Lâm Đồng","Lạng Sơn",
  "Lào Cai","Long An","Nam Định","Nghệ An","Ninh Bình","Ninh Thuận","Phú Thọ",
  "Phú Yên","Quảng Bình","Quảng Nam","Quảng Ngãi","Quảng Ninh",
  "Quảng Trị","Sóc Trăng","Sơn La","Tây Ninh","Thái Bình","Thái Nguyên",
  "Thanh Hóa","Thừa Thiên Huế","Tiền Giang","Trà Vinh","Tuyên Quang",
  "Vĩnh Long","Vĩnh Phúc","Yên Bái"
];

function openMentorModal(mode){
  const modal = document.getElementById("mentorModal");
  const title = document.getElementById("mentorModalTitle");
  const body  = document.getElementById("mentorModalBody");
  const ft    = document.getElementById("mentorModalFooter");
  const data  = getMentorProfile();

  function close(){ modal.classList.remove("show"); }
  const closeBtn = document.getElementById("closeMentorModal");
  if (closeBtn) closeBtn.onclick = close;
  ft.innerHTML = "";

  if (mode === "info"){
    title.textContent = t("modalInfoTitle");
    body.innerHTML = `
      <div class="form-row"><label>${currentLang==="vi"?"Họ tên":"Full name"}</label><input id="m_name" value="${escapeHtml(data.name || "Mentor Tran")}" /></div>
      <div class="form-row"><label>Email</label><input id="m_email" value="${escapeHtml(data.email || "mentor@example.com")}" /></div>
      <div class="form-row"><label>${currentLang==="vi"?"SĐT":"Phone"}</label><input id="m_phone" value="${escapeHtml(data.phone || "")}" placeholder="09xxxxxxxx" /></div>
      <div class="form-row"><label>Bio</label><textarea id="m_bio" rows="3" placeholder="${currentLang==="vi"?"Giới thiệu ngắn...":"Short introduction..."}">${escapeHtml(data.bio || "")}</textarea></div>
      <p class="muted">* Demo: saved to localStorage.</p>
    `;
    ft.innerHTML = `
      <button class="btn btn-outline btn-sm" type="button" id="m_cancel">${escapeHtml(t("btnCancel"))}</button>
      <button class="btn btn-primary btn-sm" type="button" id="m_save">${escapeHtml(t("btnSave"))}</button>
    `;
    document.getElementById("m_cancel").onclick = close;
    document.getElementById("m_save").onclick = ()=>{
      setMentorProfile({
        ...data,
        name: document.getElementById("m_name").value.trim(),
        email: document.getElementById("m_email").value.trim(),
        phone: document.getElementById("m_phone").value.trim(),
        bio: document.getElementById("m_bio").value.trim()
      });
      alert(t("msgSavedProfile"));
      close();
    };
  }

  if (mode === "availability"){
    title.textContent = t("modalAvailabilityTitle");

    const province = data.province || "TP. Hồ Chí Minh";

    body.innerHTML = `
      <div class="form-row"><label>${currentLang==="vi"?"Tỉnh/Thành phố":"Province/City"}</label>
        <select id="m_province">
          ${VN_PROVINCES.map(c=>`<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("")}
        </select>
      </div>

      <div class="form-row"><label>${currentLang==="vi"?"Múi giờ":"Time zone"}</label>
        <select id="m_tz" disabled>
          <option value="Asia/Ho_Chi_Minh">Asia/Ho_Chi_Minh (UTC+7)</option>
        </select>
      </div>

      <div class="form-row"><label>${currentLang==="vi"?"Khung giờ rảnh":"Available time"}</label>
        <input id="m_time" value="${escapeHtml(data.time || "Thứ 2–Thứ 6: 19:00 - 21:00")}" />
      </div>

      <div class="form-row"><label>${currentLang==="vi"?"Ghi chú":"Notes"}</label>
        <textarea id="m_note" rows="3" placeholder="${currentLang==="vi"?"VD: Thứ 4 nghỉ...":"E.g. Not available on Wed..."}">${escapeHtml(data.note || "")}</textarea>
      </div>

      <p class="muted">
        * Múi giờ mặc định của Việt Nam: <b>UTC+7</b>.
      </p>
    `;

    ft.innerHTML = `
      <button class="btn btn-outline btn-sm" type="button" id="m_cancel">${escapeHtml(t("btnCancel"))}</button>
      <button class="btn btn-primary btn-sm" type="button" id="m_save">${escapeHtml(t("btnSave"))}</button>
    `;
    document.getElementById("m_cancel").onclick = close;

    const provinceEl = document.getElementById("m_province");
    if (provinceEl) provinceEl.value = province;

    document.getElementById("m_save").onclick = ()=>{
      setMentorProfile({
        ...data,
        province: provinceEl ? provinceEl.value : province,
        tz: "Asia/Ho_Chi_Minh",
        time: document.getElementById("m_time").value.trim(),
        note: document.getElementById("m_note").value.trim()
      });
      alert(t("msgSavedAvail"));
      close();
    };

    applyControlLook(body);
  }

  if (mode === "security"){
    title.textContent = t("modalSecurityTitle");
    body.innerHTML = `
      <div class="form-row"><label>${currentLang==="vi"?"Mật khẩu cũ":"Old password"}</label><input id="m_old" type="password" placeholder="••••••••" /></div>
      <div class="form-row"><label>${currentLang==="vi"?"Mật khẩu mới":"New password"}</label><input id="m_new" type="password" placeholder="••••••••" /></div>
      <div class="form-row"><label>${currentLang==="vi"?"Xác nhận":"Confirm"}</label><input id="m_new2" type="password" placeholder="••••••••" /></div>
      <p class="muted">* Demo only.</p>
    `;
    ft.innerHTML = `
      <button class="btn btn-outline btn-sm" type="button" id="m_cancel">${escapeHtml(t("btnCancel"))}</button>
      <button class="btn btn-primary btn-sm" type="button" id="m_save">${escapeHtml(t("btnChangePass"))}</button>
    `;
    document.getElementById("m_cancel").onclick = close;
    document.getElementById("m_save").onclick = ()=>{
      if (document.getElementById("m_new").value !== document.getElementById("m_new2").value){
        alert(t("msgPassMismatch"));
        return;
      }
      alert(t("msgPassOk"));
      close();
    };

    applyControlLook(body);
  }

  if (mode === "logout"){
    localStorage.removeItem(TOKEN_KEY);
    alert(t("msgLoggedOut"));
    close();
    return;
  }

  modal.classList.add("show");
  applyTheme();
  applyControlLook(modal);
}

/* dropdown */
function toggleDropdown(){
  const dd = document.getElementById("dropdown");
  if (!dd) return;
  dd.style.display = (dd.style.display === "block") ? "none" : "block";
}
const profileBtn = document.getElementById("profileBtn");
if (profileBtn){
  profileBtn.addEventListener("click", (e)=>{
    e.stopPropagation();
    toggleDropdown();
  });
}
window.addEventListener("click", ()=>{
  const dd = document.getElementById("dropdown");
  if (dd) dd.style.display = "none";
});
const dropdown = document.getElementById("dropdown");
if (dropdown){
  dropdown.addEventListener("click", (e)=>{
    const a = e.target.closest("a");
    if (!a) return;
    e.preventDefault();
    const mode = a.dataset.profile;
    dropdown.style.display = "none";
    openMentorModal(mode);
  });
}
const mentorModal = document.getElementById("mentorModal");
if (mentorModal){
  mentorModal.addEventListener("click", (e)=>{
    if (e.target.id === "mentorModal") mentorModal.classList.remove("show");
  });
}

/* =========================================================
   INIT
========================================================= */
document.addEventListener("DOMContentLoaded", ()=>{
  sectionHost = document.getElementById("sectionHost");

  initDemoSubmissions();
  learnersCache = getMockLearners();

  ensureThemeStyleTag();
  applyTheme();
  applyLanguage();

  const alertsText = document.getElementById("alertsText");
  if (alertsText) alertsText.textContent = t("alertsText");

  loadSection("learners");
});

