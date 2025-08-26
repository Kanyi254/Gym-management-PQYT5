# 🏋️ Gym-management-PQYT5

A modern Gym Management System built with **PyQt5** and **SQLite**, designed for gyms and fitness centers to efficiently manage members, visits, payments, and reports with real-time insights and smart alerts.

---

## 📊 Features Overview

### 1. Dashboard Tab
- Real-time Metrics Cards: Total members, active members, expiring this week, today’s revenue  
- Quick Actions: Fast member addition, visit recording, alert viewing  
- Recent Activity Feed: Live updates of today’s registrations and visits  
- Smart Alerts: Visual indicators for urgent items  

### 2. Members Management 👥
- Advanced Search & Filtering: Search by name/phone/email, filter by status  
- Comprehensive Member Profiles: Complete member information management  
- Visual Status Indicators: Color-coded expiry warnings in the table  
- Inline Actions: Edit, delete, and manage members directly from the table  

### 3. Visits Tracking 📝
- Quick Visit Recording: Easy member selection with payment tracking  
- Payment Method Support: Cash, M-Pesa, Bank Transfer, Card options  
- Visit History: Complete chronological record with payment details  
- Notes Support: Add extra context for each visit  

### 4. Advanced Reports System 📊
#### Dashboard Report
- Business statistics and KPIs  
- Recent transaction history  
- Revenue tracking and analytics  

#### Expiry Alerts 🚨
- Color-coded Status System:  
  - **RED**: Expired memberships  
  - **ORANGE**: Urgent (1–3 days left)  
  - **YELLOW**: Warning (4–7 days left)  
- One-click Renewal: Direct membership renewal from alerts  
- Proactive Management: Never miss renewals again  

#### Payment Reports 💳
- Daily Payment Summary by payment method  
- Date Range Filtering for custom reports  
- Complete Payment History (audit trail)  
- Revenue Analytics: Track payment preferences and trends  

#### Individual Reports 👤
- Full Member Lifecycle Analysis  
- Key Performance Metrics:  
  - Days since registration  
  - Total visits vs. recorded visits  
  - Payment history and patterns  
  - Membership status analytics  
- Visit Timeline with chronological history and payment details  

---

## 🛠️ Technical Features

### Database Design
- **SQLite Backend**: Reliable and lightweight  
- Three Main Tables: `Members`, `Visits`, `Payments`  
- Backward Compatibility: Existing data preserved during updates  
- Data Integrity: Foreign key relationships and constraints  

### User Interface
- Professional Styling: Modern, clean UI with custom stylesheets  
- Responsive Design: Adaptive layouts for different screen sizes  
- Color-coded Alerts for important information  
- Tabbed Navigation: Organized and intuitive  

### Business Intelligence
- Real-time Analytics: Live dashboard updates  
- Predictive Alerts: Proactive membership management  
- Financial Tracking: Comprehensive revenue analysis  
- Member Insights: Behavioral pattern analysis  

---

## 🚀 Key Business Benefits
- **Proactive Management**: Never miss renewals with smart alerts  
- **Financial Insights**: Track payment preferences and cash flow patterns  
- **Member Analytics**: Understand member behavior and engagement  
- **Audit Trail**: Complete transaction history for compliance  
- **Efficiency**: Streamlined operations with automation  

---

## 📦 Installation & Usage

```bash
# Clone this repository
git clone https://github.com/yourusername/Gym-management-PQYT5.git
cd Gym-management-PQYT5

# Install required dependencies
pip install PyQt5

# Run the application
python gym_management_system.py
