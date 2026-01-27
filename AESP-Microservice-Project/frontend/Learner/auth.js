// 1. NHÚNG NAVBAR
export async function loadNavbar(activePage) {
    const container = document.getElementById('navbar-placeholder');
    if (!container) return;

    try {
        const response = await fetch('navbar.html');
        if (!response.ok) throw new Error("Không tìm thấy navbar.html");
        const html = await response.text();
        container.innerHTML = html;

        // Highlight trang đang xem
        const activeLink = document.getElementById(`nav-${activePage}`);
        if (activeLink) activeLink.classList.add('active');

        // Hiển thị thông tin User
        updateNavbarUserInfo();

        // Gán nút Logout
        const logoutBtn = document.getElementById('btn-logout');
        if (logoutBtn) logoutBtn.onclick = handleLogout;
    } catch (error) {
        console.error("Lỗi nhúng Navbar:", error);
    }
}

// 2. HIỆN THÔNG TIN USER TRÊN NAVBAR
export function updateNavbarUserInfo() {
    const userInfoStr = localStorage.getItem("user_info");
    if (userInfoStr) {
        const user = JSON.parse(userInfoStr);
        const nameEl = document.getElementById('display-name');
        const avatarEl = document.getElementById('display-avatar');
        if (nameEl) nameEl.innerText = user.username || "Học viên";
        if (avatarEl && user.username) {
            avatarEl.innerText = user.username.charAt(0).toUpperCase();
        }
    }
}

// 3. GỌI API KÈM TOKEN (Dành cho Analytics/Practice Service)
export async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("token");
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) handleLogout();
    return response;
}

// 4. ĐĂNG XUẤT
export function handleLogout() {
    if(confirm("Bạn có chắc chắn muốn đăng xuất?")) {
        localStorage.clear();
        window.location.href = "/index.html";
    }
}

window.handleLogout = handleLogout;