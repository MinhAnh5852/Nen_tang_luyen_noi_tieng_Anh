// 1. Cấu hình các Endpoint (Thông qua Gateway cổng 80)
const API_BASE_URL = "http://localhost/api/users";
const PAYMENT_API_URL = "http://localhost/api/payments";
const SUBSCRIPTION_API_URL = "http://localhost/api/subscriptions";

// --- XỬ LÝ ĐĂNG KÝ ---
async function handleRegister(event) {
  event.preventDefault();
  const dataObj = {
    username: document.getElementById("register-name").value,
    email: document.getElementById("register-email").value,
    password: document.getElementById("register-password").value,
    role: document.getElementById("user-role").value.toUpperCase(),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dataObj),
    });

    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      if (response.ok) {
        alert("Đăng ký thành công! Hãy đăng nhập.");
        window.location.href = "login.html";
      } else {
        alert("Lỗi: " + (data.error || data.message || "Đăng ký thất bại"));
      }
    } else {
      alert("Lỗi máy chủ (Nginx Gateway). Hãy kiểm tra log Docker.");
    }
  } catch (error) {
    console.error("Fetch error:", error);
    alert("Không thể kết nối đến Gateway.");
  }
}

// --- XỬ LÝ ĐĂNG NHẬP ---
async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    if (response.ok) {
      localStorage.setItem("access_token", data.token);
      localStorage.setItem("user_info", JSON.stringify(data.user));
      alert("Đăng nhập thành công!");
      window.location.href = `${data.user.role.toLowerCase()}.html`;
    } else {
      alert("Lỗi: " + (data.error || "Sai thông tin đăng nhập"));
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("Lỗi kết nối API.");
  }
}

// --- XỬ LÝ THANH TOÁN (CHECKOUT) ---
async function handleCheckout(packageId) {
  const token = localStorage.getItem("access_token");
  const userInfoStr = localStorage.getItem("user_info");

  if (!token || !userInfoStr) {
    alert("Vui lòng đăng nhập lại!");
    window.location.href = "login.html";
    return;
  }

  const userInfo = JSON.parse(userInfoStr);
  const payload = {
    user_id: userInfo.id,
    amount: packageId === "PREMIUM_MONTHLY" ? 399000 : 149000,
    method: "TRANSFER", // Mặc định chuyển khoản ngân hàng
    package_id: packageId,
    subscription_id: "sub_" + Date.now(),
  };

  try {
    const response = await fetch(`${PAYMENT_API_URL}/checkout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = await response.json();
      alert("Đã tạo yêu cầu thanh toán!");
      // Chuyển hướng đến cổng thanh toán/trang xác nhận
      window.location.href = data.checkout_url;
    } else {
      const err = await response.json();
      alert("Lỗi: " + err.message);
    }
  } catch (error) {
    console.error("Lỗi checkout:", error);
  }
}

// --- XỬ LÝ TRẠNG THÁI GÓI CƯỚC ---
async function fetchSubscriptionStatus() {
  const token = localStorage.getItem("access_token");
  const userInfoStr = localStorage.getItem("user_info");
  if (!token || !userInfoStr) return;

  const userInfo = JSON.parse(userInfoStr);
  try {
    const response = await fetch(
      `${SUBSCRIPTION_API_URL}/status?user_id=${userInfo.id}`,
      {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      },
    );

    if (response.ok) {
      const data = await response.json();
      updateSubscriptionUI(data);
    }
  } catch (error) {
    console.error("Lỗi lấy trạng thái:", error);
  }
}

function updateSubscriptionUI(data) {
  const planNameEl = document.getElementById("current-plan-name");
  const planDetailsEl = document.getElementById("current-plan-details");
  if (!planNameEl || !planDetailsEl) return;

  if (data && data.status === "active") {
    // Hiển thị tên gói đang sử dụng
    planNameEl.textContent = data.package_name;

    const endDate = new Date(data.end_date);
    const now = new Date();
    const daysLeft = Math.ceil((endDate - now) / (1000 * 60 * 60 * 24));

    planDetailsEl.innerHTML = `
      <div class="plan-feature">
        <i class="fas fa-check-circle"></i>
        <span>Trạng thái: <strong>Đang hoạt động</strong></span>
      </div>
      <div class="plan-feature">
        <i class="fas fa-calendar-check"></i>
        <span>Hạn dùng: Còn ${daysLeft > 0 ? daysLeft : 0} ngày</span>
      </div>
      <div class="plan-feature">
        <i class="fas fa-clock"></i>
        <span>Ngày hết hạn: ${endDate.toLocaleDateString("vi-VN")}</span>
      </div>
    `;
  } else {
    // Hiển thị trạng thái khi chưa mua gói
    planNameEl.textContent = "Gói Miễn phí";
    planDetailsEl.innerHTML = `
      <p style="color: rgba(255,255,255,0.8)">Bạn đang sử dụng quyền truy cập hạn chế. Nâng cấp để học không giới hạn!</p>
    `;
  }
}

// --- LẤY LỊCH SỬ GIAO DỊCH ---
async function fetchUserTransactions() {
  const token = localStorage.getItem("access_token");
  const userInfoStr = localStorage.getItem("user_info");
  if (!token || !userInfoStr) return;

  const userInfo = JSON.parse(userInfoStr);
  const transactionListEl = document.getElementById("transaction-list");

  try {
    const response = await fetch(
      `${PAYMENT_API_URL}/my-transactions?user_id=${userInfo.id}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      },
    );

    if (response.ok) {
      const transactions = await response.json();
      console.log("Transactions loaded:", transactions);

      if (transactionListEl) {
        if (transactions.length === 0) {
          transactionListEl.innerHTML =
            '<p style="padding: 20px; color: gray">Chưa có giao dịch nào.</p>';
          return;
        }

        // Hiển thị danh sách giao dịch dưới dạng bảng hoặc list
        let html = '<table style="width:100%; border-collapse: collapse;">';
        html +=
          '<tr style="border-bottom: 1px solid #eee;"><th style="padding:10px; text-align:left;">Ngày</th><th style="text-align:left;">Số tiền</th><th style="text-align:left;">Trạng thái</th><th style="text-align:left;">Phương thức</th></tr>';

        transactions.forEach((tx) => {
          const statusClass = tx.status === "SUCCESS" ? "status-success" : "";
          html += `<tr style="border-bottom: 1px solid #f9f9f9;">
                        <td style="padding:10px;">${tx.date}</td>
                        <td>${tx.amount.toLocaleString("vi-VN")}đ</td>
                        <td><span class="payment-status ${statusClass}">${tx.status}</span></td>
                        <td>${tx.method}</td>
                    </tr>`;
        });
        html += "</table>";
        transactionListEl.innerHTML = html;
      }
    } else {
      console.error("Payment Service trả về lỗi 400/500");
    }
  } catch (error) {
    console.error("Fetch transactions error:", error);
  }
}

// --- ĐĂNG XUẤT ---
function handleLogout() {
  localStorage.clear();
  window.location.href = "login.html";
}

async function fetchUserProfile() {
  const token = localStorage.getItem("access_token");
  if (!token) return;

  try {
    const response = await fetch("http://localhost/api/users/me", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`, // Gửi token để Backend biết bạn là ai
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const userData = await response.json();
      // Cập nhật thông tin lên giao diện profile.html hoặc header
      if (document.getElementById("profile-email")) {
        document.getElementById("profile-email").textContent = userData.email;
        document.getElementById("profile-username").textContent =
          userData.username;
      }
    }
  } catch (error) {
    console.error("Lỗi lấy thông tin cá nhân:", error);
  }
}
