import React, { useState, useEffect } from 'react';
import './Subscription.css';

interface Plan {
  id: string; 
  name: string;
  price: number;
  duration_days: number;
  features: string[] | string;
  badge_text: string | null;
  is_active: boolean;
}

interface Transaction {
  id: string | number;
  created_at: string;
  amount: number;
  package_name: string;
  status: 'SUCCESS' | 'PENDING' | 'FAILED';
}

const Subscription: React.FC = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const [currentStatusText, setCurrentStatusText] = useState<string>("Đang đồng bộ...");
  const [loading, setLoading] = useState(true);

  const loadAllData = async () => {
    const userInfoStr = localStorage.getItem("user_info");
    const userInfo = userInfoStr ? JSON.parse(userInfoStr) : null;
    const userId = userInfo?.id; 
    const token = localStorage.getItem("token");

    try {
      setLoading(true);
      
      // 1. Lấy danh sách gói
      const plansRes = await fetch('http://localhost/api/subscriptions/plans');
      if (plansRes.ok) {
        const plansData = await plansRes.json();
        if (Array.isArray(plansData)) {
          setPlans(plansData.sort((a, b) => a.price - b.price));
        }
      }

      if (userId && token) {
        // 2. Lấy trạng thái hiện tại (Vương miện)
        // Lưu ý: Dùng try-catch nhỏ bên trong để nếu API này lỗi thì vẫn load được lịch sử
        try {
          const statusRes = await fetch(`http://localhost/api/verify`, {
              headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (statusRes.ok) {
            const statusData = await statusRes.json();
            setActivePlanId(statusData.package_id); 
            setCurrentStatusText(statusData.package_name 
              ? `Bạn đang dùng: ${statusData.package_name}`
              : "Bạn đang dùng gói Miễn phí.");
          }
        } catch (e) { console.error("Verify API Error", e); }

        // 3. Lấy lịch sử giao dịch
        const payRes = await fetch(`http://localhost/api/payments/history/${userId}`);
        if (payRes.ok) {
          const payData = await payRes.json();
          // Ép kiểu dữ liệu để đảm bảo không lỗi "transactions.map is not a function"
          setTransactions(Array.isArray(payData) ? payData : []);
        }
      }
    } catch (error) {
      console.error("Lỗi nạp dữ liệu tổng thể:", error);
      // Hiển thị thông báo lỗi lên giao diện nếu cần
      setCurrentStatusText("Không thể kết nối máy chủ.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleCheckout = async (plan: Plan) => {
    const userInfo = JSON.parse(localStorage.getItem("user_info") || '{}');
    if (!userInfo.id) {
      alert("Vui lòng đăng nhập để thực hiện nâng cấp!");
      return;
    }

    try {
      const response = await fetch('http://localhost/api/payments/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userInfo.id,
          package_id: plan.id,
          package_name: plan.name,
          method: 'cash'
        })
      });

      if (response.ok) {
        alert(`Bạn đã gửi yêu cầu nâng cấp lên ${plan.name} thành công!\n\nVui lòng đến cơ sở AESP bất kỳ để đóng tiền mặt để hoàn thành quá trình kích hoạt gói cước.`);
        loadAllData();
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Lỗi: ${errorData.error || "Không thể tạo yêu cầu."}`);
      }
    } catch (error) {
      alert("Lỗi kết nối máy chủ. Vui lòng kiểm tra hệ thống Docker.");
    }
  };

  if (loading) return <div className="container" style={{ marginTop: '100px', textAlign: 'center' }}>Đang nạp dữ liệu...</div>;

  return (
    <div className="container" style={{ marginTop: '100px' }}>
      <div className="current-plan-banner" style={{ background: 'linear-gradient(45deg, #4158D0, #C850C0)', color: 'white', padding: '20px', borderRadius: '12px', marginBottom: '30px' }}>
        <h2><i className="fas fa-crown"></i> Gói dịch vụ của tôi</h2>
        <div className="plan-info-text" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{currentStatusText}</div>
      </div>

      <h2 className="section-title">Nâng cấp trải nghiệm học tập AI</h2>

      <div className="plans-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        {plans.map(plan => {
          const isCurrent = String(plan.id) === String(activePlanId);
          const featuresList = Array.isArray(plan.features) ? plan.features : (typeof plan.features === 'string' ? plan.features.split(',') : []);

          return plan.is_active && (
            <div key={plan.id} className="plan-card" style={{ border: isCurrent ? '3px solid #4CAF50' : '1px solid #ddd', padding: '20px', borderRadius: '15px', position: 'relative', backgroundColor: 'white' }}>
              {plan.badge_text && <div className="recommend-badge" style={{ position: 'absolute', top: '-10px', right: '10px', background: '#ff9800', color: 'white', padding: '2px 10px', borderRadius: '10px', fontSize: '12px' }}>{plan.badge_text}</div>}
              <h3>{plan.name}</h3>
              <div className="plan-price" style={{ fontSize: '1.5rem', margin: '15px 0', color: '#2196F3', fontWeight: 'bold' }}>
                {plan.price === 0 ? '0đ' : `${Number(plan.price).toLocaleString('vi-VN')}đ`}
              </div>
              
              <ul className="plan-features-list" style={{ listStyle: 'none', padding: 0, textAlign: 'left', marginBottom: '20px' }}>
                {featuresList.map((f, i) => (
                  <li key={i} style={{ marginBottom: '8px', fontSize: '14px' }}>
                    <i className="fas fa-check-circle" style={{ color: '#4CAF50', marginRight: '8px' }}></i> {f.trim()}
                  </li>
                ))}
              </ul>

              <button 
                className={`btn ${isCurrent ? 'btn-current' : 'btn-primary'}`}
                style={{ 
                    width: '100%', padding: '12px', borderRadius: '8px', 
                    backgroundColor: isCurrent ? '#4CAF50' : '#2196F3', 
                    color: 'white', border: 'none', cursor: isCurrent ? 'default' : 'pointer',
                    fontWeight: 'bold', transition: '0.3s'
                }}
                onClick={() => !isCurrent && handleCheckout(plan)}
                disabled={isCurrent}
              >
                {isCurrent ? 'Gói hiện tại' : 'Nâng cấp ngay'}
              </button>
            </div>
          );
        })}
      </div>

      <div className="transaction-section" style={{ marginTop: '50px' }}>
        <h3><i className="fas fa-history"></i> Lịch sử yêu cầu nâng cấp</h3>
        <div className="table-responsive">
          <table className="data-table" style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '10px', overflow: 'hidden' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '15px' }}>Ngày yêu cầu</th>
                <th style={{ padding: '15px' }}>Gói cước</th>
                <th style={{ padding: '15px' }}>Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length > 0 ? transactions.map((tx) => (
                <tr key={tx.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '15px' }}>{new Date(tx.created_at).toLocaleDateString('vi-VN')}</td>
                  <td style={{ padding: '15px' }}>{tx.package_name}</td>
                  <td style={{ padding: '15px' }}>
                    <span style={{ 
                        padding: '4px 12px', borderRadius: '20px', fontSize: '0.85rem',
                        backgroundColor: tx.status === 'SUCCESS' ? '#e8f5e9' : (tx.status === 'PENDING' ? '#fff3e0' : '#ffebee'),
                        color: tx.status === 'SUCCESS' ? '#2e7d32' : (tx.status === 'PENDING' ? '#ef6c00' : '#c62828')
                    }}>
                      {tx.status === 'SUCCESS' ? 'Đã kích hoạt' : (tx.status === 'PENDING' ? 'Chờ nộp tiền' : 'Thất bại')}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center', padding: '30px', color: '#888' }}>Bạn chưa có yêu cầu nâng cấp nào.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Subscription;