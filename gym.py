import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json

class GymManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_database()
        self.init_ui()
        self.load_data()
        
    def init_database(self):
        """Initialize SQLite database with all required tables"""
        self.conn = sqlite3.connect('gym_management.db')
        cursor = self.conn.cursor()
        
        # Members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                membership_type TEXT,
                start_date DATE,
                end_date DATE,
                amount_paid REAL,
                payment_method TEXT DEFAULT 'Cash',
                status TEXT DEFAULT 'Active',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Visits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_amount REAL DEFAULT 0,
                payment_method TEXT DEFAULT 'None',
                notes TEXT,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Payments table for detailed tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_type TEXT DEFAULT 'Membership',
                notes TEXT,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        self.conn.commit()
    
    def init_ui(self):
        """Initialize the main user interface"""
        self.setWindowTitle("Advanced Gym Management System")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self.get_stylesheet())
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header
        header = self.create_header()
        layout.addWidget(header)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #c0c0c0; }
            QTabBar::tab { 
                background: #e1e1e1; 
                padding: 10px 20px; 
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { 
                background: #4CAF50; 
                color: white;
            }
        """)
        
        # Add tabs
        self.create_dashboard_tab()
        self.create_members_tab()
        self.create_visits_tab()
        self.create_reports_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Gym Management System Ready")
    
    def create_header(self):
        """Create application header with logo and title"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title_label = QLabel("💪 ADVANCED GYM MANAGEMENT SYSTEM")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
        """)
        
        # Current date/time
        datetime_label = QLabel()
        datetime_label.setText(datetime.now().strftime("%A, %B %d, %Y - %I:%M %p"))
        datetime_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            padding: 20px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(datetime_label)
        
        return header_widget
    
    def create_dashboard_tab(self):
        """Create dashboard with key metrics and alerts"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Metrics cards row
        metrics_layout = QHBoxLayout()
        
        # Total Members Card
        self.total_members_card = self.create_metric_card("👥 Total Members", "0", "#3498db")
        metrics_layout.addWidget(self.total_members_card)
        
        # Active Members Card
        self.active_members_card = self.create_metric_card("✅ Active Members", "0", "#27ae60")
        metrics_layout.addWidget(self.active_members_card)
        
        # Expiring This Week Card
        self.expiring_members_card = self.create_metric_card("⚠️ Expiring This Week", "0", "#f39c12")
        metrics_layout.addWidget(self.expiring_members_card)
        
        # Today's Revenue Card
        self.revenue_card = self.create_metric_card("💰 Today's Revenue", "KSh 0", "#e74c3c")
        metrics_layout.addWidget(self.revenue_card)
        
        layout.addLayout(metrics_layout)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        quick_add_btn = QPushButton("➕ Quick Add Member")
        quick_add_btn.setStyleSheet(self.get_button_style("#27ae60"))
        quick_add_btn.clicked.connect(self.quick_add_member)
        
        record_visit_btn = QPushButton("📝 Record Visit")
        record_visit_btn.setStyleSheet(self.get_button_style("#3498db"))
        record_visit_btn.clicked.connect(self.quick_record_visit)
        
        view_alerts_btn = QPushButton("🚨 View Alerts")
        view_alerts_btn.setStyleSheet(self.get_button_style("#e67e22"))
        view_alerts_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(3))
        
        actions_layout.addWidget(quick_add_btn)
        actions_layout.addWidget(record_visit_btn)
        actions_layout.addWidget(view_alerts_btn)
        actions_layout.addStretch()
        
        layout.addWidget(actions_group)
        
        # Recent Activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
        """)
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard_widget, "📊 Dashboard")
    
    def create_members_tab(self):
        """Create members management tab"""
        members_widget = QWidget()
        layout = QVBoxLayout(members_widget)
        
        # Search and filter bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search members by name, phone, or email...")
        self.search_input.textChanged.connect(self.search_members)
        
        filter_combo = QComboBox()
        filter_combo.addItems(["All Members", "Active", "Expired", "Expiring Soon"])
        filter_combo.currentTextChanged.connect(self.filter_members)
        
        add_member_btn = QPushButton("➕ Add New Member")
        add_member_btn.setStyleSheet(self.get_button_style("#27ae60"))
        add_member_btn.clicked.connect(self.add_member)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(filter_combo, 1)
        search_layout.addWidget(add_member_btn, 1)
        
        layout.addLayout(search_layout)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(9)
        self.members_table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Membership", 
            "Start Date", "End Date", "Status", "Actions"
        ])
        
        # Style the table
        self.members_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.members_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.members_table)
        
        self.tab_widget.addTab(members_widget, "👥 Members")
    
    def create_visits_tab(self):
        """Create visits tracking tab"""
        visits_widget = QWidget()
        layout = QVBoxLayout(visits_widget)
        
        # Visit recording section
        record_group = QGroupBox("Record New Visit")
        record_layout = QHBoxLayout(record_group)
        
        # Member selection
        self.visit_member_combo = QComboBox()
        self.visit_member_combo.setEditable(True)
        self.visit_member_combo.setPlaceholderText("Select or search member...")
        
        # Payment amount
        self.visit_payment_input = QLineEdit()
        self.visit_payment_input.setPlaceholderText("Payment amount (optional)")
        
        # Payment method
        self.visit_payment_method = QComboBox()
        self.visit_payment_method.addItems(["None", "Cash", "M-Pesa", "Bank Transfer", "Card"])
        
        # Notes
        self.visit_notes_input = QLineEdit()
        self.visit_notes_input.setPlaceholderText("Notes (optional)")
        
        # Record button
        record_visit_btn = QPushButton("✅ Record Visit")
        record_visit_btn.setStyleSheet(self.get_button_style("#27ae60"))
        record_visit_btn.clicked.connect(self.record_visit)
        
        record_layout.addWidget(QLabel("Member:"))
        record_layout.addWidget(self.visit_member_combo, 2)
        record_layout.addWidget(QLabel("Payment:"))
        record_layout.addWidget(self.visit_payment_input, 1)
        record_layout.addWidget(self.visit_payment_method, 1)
        record_layout.addWidget(QLabel("Notes:"))
        record_layout.addWidget(self.visit_notes_input, 1)
        record_layout.addWidget(record_visit_btn)
        
        layout.addWidget(record_group)
        
        # Visits table
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(7)
        self.visits_table.setHorizontalHeaderLabels([
            "ID", "Member", "Visit Date", "Payment", "Payment Method", "Notes", "Actions"
        ])
        
        self.visits_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        self.visits_table.horizontalHeader().setStretchLastSection(True)
        self.visits_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.visits_table)
        
        self.tab_widget.addTab(visits_widget, "📝 Visits")
    
    def create_reports_tab(self):
        """Create comprehensive reports tab with analytics"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        
        # Create reports sub-tabs
        reports_tabs = QTabWidget()
        
        # Dashboard Report
        self.create_dashboard_report_tab(reports_tabs)
        
        # Expiry Alerts
        self.create_expiry_alerts_tab(reports_tabs)
        
        # Payment Reports
        self.create_payment_reports_tab(reports_tabs)
        
        # Individual Reports
        self.create_individual_reports_tab(reports_tabs)
        
        layout.addWidget(reports_tabs)
        
        self.tab_widget.addTab(reports_widget, "📊 Reports")
    
    def create_dashboard_report_tab(self, parent_tabs):
        """Create dashboard report with key statistics"""
        dashboard_report = QWidget()
        layout = QVBoxLayout(dashboard_report)
        
        # Key Statistics
        stats_group = QGroupBox("📈 Key Statistics")
        stats_layout = QGridLayout(stats_group)
        
        # Create statistics labels
        self.stats_labels = {}
        stats = [
            ("Total Members", "total_members"),
            ("Active Members", "active_members"),
            ("Expired Members", "expired_members"),
            ("Total Revenue", "total_revenue"),
            ("This Month Revenue", "month_revenue"),
            ("Today's Visits", "today_visits"),
            ("Average Daily Visits", "avg_visits"),
            ("Member Retention Rate", "retention_rate")
        ]
        
        for i, (label, key) in enumerate(stats):
            row, col = i // 2, (i % 2) * 2
            
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; color: #2c3e50;")
            
            value_widget = QLabel("Loading...")
            value_widget.setStyleSheet("font-size: 16px; color: #27ae60; font-weight: bold;")
            
            self.stats_labels[key] = value_widget
            
            stats_layout.addWidget(label_widget, row, col)
            stats_layout.addWidget(value_widget, row, col + 1)
        
        layout.addWidget(stats_group)
        
        # Recent Transactions
        transactions_group = QGroupBox("💳 Recent Transactions")
        transactions_layout = QVBoxLayout(transactions_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Member", "Amount", "Method", "Type"
        ])
        self.transactions_table.setMaximumHeight(300)
        
        transactions_layout.addWidget(self.transactions_table)
        layout.addWidget(transactions_group)
        
        layout.addStretch()
        
        parent_tabs.addTab(dashboard_report, "📊 Dashboard")
    
    def create_expiry_alerts_tab(self, parent_tabs):
        """Create expiry alerts tab"""
        expiry_widget = QWidget()
        layout = QVBoxLayout(expiry_widget)
        
        # Alert summary
        alert_summary = QGroupBox("🚨 Membership Expiry Alerts")
        summary_layout = QHBoxLayout(alert_summary)
        
        self.expired_label = QLabel("EXPIRED: 0")
        self.expired_label.setStyleSheet("background: #e74c3c; color: white; padding: 10px; border-radius: 4px; font-weight: bold;")
        
        self.urgent_label = QLabel("URGENT (1-3 days): 0")
        self.urgent_label.setStyleSheet("background: #f39c12; color: white; padding: 10px; border-radius: 4px; font-weight: bold;")
        
        self.warning_label = QLabel("WARNING (4-7 days): 0")
        self.warning_label.setStyleSheet("background: #f1c40f; color: black; padding: 10px; border-radius: 4px; font-weight: bold;")
        
        summary_layout.addWidget(self.expired_label)
        summary_layout.addWidget(self.urgent_label)
        summary_layout.addWidget(self.warning_label)
        summary_layout.addStretch()
        
        layout.addWidget(alert_summary)
        
        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(7)
        self.alerts_table.setHorizontalHeaderLabels([
            "Status", "Member", "Phone", "Email", "End Date", "Days Left", "Actions"
        ])
        
        self.alerts_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.alerts_table)
        
        parent_tabs.addTab(expiry_widget, "🚨 Expiry Alerts")
    
    def create_payment_reports_tab(self, parent_tabs):
        """Create payment analysis tab"""
        payment_widget = QWidget()
        layout = QVBoxLayout(payment_widget)
        
        # Daily payment summary
        daily_group = QGroupBox("💰 Today's Payment Summary")
        daily_layout = QGridLayout(daily_group)
        
        self.payment_method_labels = {}
        methods = ["Cash", "M-Pesa", "Bank Transfer", "Card"]
        
        for i, method in enumerate(methods):
            method_label = QLabel(f"{method}:")
            method_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
            
            amount_label = QLabel("KSh 0")
            amount_label.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
            
            self.payment_method_labels[method] = amount_label
            
            daily_layout.addWidget(method_label, i // 2, (i % 2) * 2)
            daily_layout.addWidget(amount_label, i // 2, (i % 2) * 2 + 1)
        
        layout.addWidget(daily_group)
        
        # Payment history table
        history_group = QGroupBox("📋 Payment History")
        history_layout = QVBoxLayout(history_group)
        
        # Date filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by date:"))
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        
        filter_btn = QPushButton("📊 Generate Report")
        filter_btn.setStyleSheet(self.get_button_style("#3498db"))
        filter_btn.clicked.connect(self.generate_payment_report)
        
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("to"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(filter_btn)
        filter_layout.addStretch()
        
        history_layout.addLayout(filter_layout)
        
        # Payment history table
        self.payment_history_table = QTableWidget()
        self.payment_history_table.setColumnCount(6)
        self.payment_history_table.setHorizontalHeaderLabels([
            "Date", "Member", "Amount", "Method", "Type", "Notes"
        ])
        
        history_layout.addWidget(self.payment_history_table)
        layout.addWidget(history_group)
        
        parent_tabs.addTab(payment_widget, "💳 Payment Reports")
    
    def create_individual_reports_tab(self, parent_tabs):
        """Create individual member reports tab"""
        individual_widget = QWidget()
        layout = QVBoxLayout(individual_widget)
        
        # Member selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Member:"))
        
        self.report_member_combo = QComboBox()
        self.report_member_combo.setEditable(True)
        self.report_member_combo.currentTextChanged.connect(self.generate_individual_report)
        
        selection_layout.addWidget(self.report_member_combo, 2)
        selection_layout.addStretch()
        
        layout.addLayout(selection_layout)
        
        # Member report display
        self.member_report_text = QTextEdit()
        self.member_report_text.setReadOnly(True)
        self.member_report_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        layout.addWidget(self.member_report_text)
        
        parent_tabs.addTab(individual_widget, "👤 Individual Reports")
    
    def create_metric_card(self, title, value, color):
        """Create a metric card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 24px;")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setObjectName("value_label")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def get_stylesheet(self):
        """Return application stylesheet"""
        return """
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
        """
    
    def get_button_style(self, color):
        """Return button style with specified color"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """
    
    def load_data(self):
        """Load all data and refresh UI"""
        self.load_members()
        self.load_visits()
        self.update_dashboard()
        self.update_member_combos()
        self.update_expiry_alerts()
        self.update_payment_summary()
        self.load_recent_activity()
    
    def load_members(self):
        """Load members into table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, phone, email, membership_type, 
                   start_date, end_date, status
            FROM members ORDER BY registration_date DESC
        """)
        
        members = cursor.fetchall()
        self.members_table.setRowCount(len(members))
        
        for row, member in enumerate(members):
            for col, value in enumerate(member):
                if col == 6:  # end_date column
                    # Check if membership is expired or expiring soon
                    if value:
                        end_date = datetime.strptime(value, '%Y-%m-%d')
                        days_left = (end_date - datetime.now()).days
                        
                        item = QTableWidgetItem(value)
                        if days_left < 0:
                            item.setBackground(QColor("#ffebee"))  # Light red for expired
                        elif days_left <= 7:
                            item.setBackground(QColor("#fff3e0"))  # Light orange for expiring soon
                        
                        self.members_table.setItem(row, col, item)
                    else:
                        self.members_table.setItem(row, col, QTableWidgetItem(""))
                else:
                    self.members_table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Edit Member")
            edit_btn.setMaximumSize(30, 25)
            edit_btn.clicked.connect(lambda checked, m_id=member[0]: self.edit_member(m_id))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete Member")
            delete_btn.setMaximumSize(30, 25)
            delete_btn.clicked.connect(lambda checked, m_id=member[0]: self.delete_member(m_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.members_table.setCellWidget(row, 8, actions_widget)
    
    def load_visits(self):
        """Load visits into table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.id, m.name, v.visit_date, v.payment_amount, 
                   v.payment_method, v.notes
            FROM visits v
            JOIN members m ON v.member_id = m.id
            ORDER BY v.visit_date DESC
            LIMIT 100
        """)
        
        visits = cursor.fetchall()
        self.visits_table.setRowCount(len(visits))
        
        for row, visit in enumerate(visits):
            for col, value in enumerate(visit):
                if col == 2:  # visit_date
                    # Format datetime
                    try:
                        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        formatted_date = dt.strftime('%Y-%m-%d %I:%M %p')
                        self.visits_table.setItem(row, col, QTableWidgetItem(formatted_date))
                    except:
                        self.visits_table.setItem(row, col, QTableWidgetItem(str(value)))
                elif col == 3:  # payment_amount
                    try:
                        amount_val = float(value) if value else 0
                        amount_text = "KSh {:.0f}".format(amount_val) if amount_val > 0 else "No Payment"
                    except (ValueError, TypeError):
                        amount_text = "No Payment"
                    self.visits_table.setItem(row, col, QTableWidgetItem(amount_text))
                else:
                    self.visits_table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete Visit")
            delete_btn.setMaximumSize(30, 25)
            delete_btn.clicked.connect(lambda checked, v_id=visit[0]: self.delete_visit(v_id))
            
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.visits_table.setCellWidget(row, 6, actions_widget)
    
    def update_dashboard(self):
        """Update dashboard metrics"""
        cursor = self.conn.cursor()
        
        # Total members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        self.total_members_card.findChild(QLabel, "value_label").setText(str(total_members))
        
        # Active members
        cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
        active_members = cursor.fetchone()[0]
        self.active_members_card.findChild(QLabel, "value_label").setText(str(active_members))
        
        # Members expiring this week
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE end_date <= ? AND end_date >= date('now') AND status = 'Active'
        """, (next_week,))
        expiring_count = cursor.fetchone()[0]
        self.expiring_members_card.findChild(QLabel, "value_label").setText(str(expiring_count))
        
        # Today's revenue
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COALESCE(SUM(payment_amount), 0) FROM visits 
            WHERE date(visit_date) = ?
        """, (today,))
        today_revenue = cursor.fetchone()[0] or 0
        try:
            today_revenue = float(today_revenue)
        except (ValueError, TypeError):
            today_revenue = 0.0
        self.revenue_card.findChild(QLabel, "value_label").setText("KSh {:,.0f}".format(today_revenue))
        
        # Update dashboard report statistics
        if hasattr(self, 'stats_labels'):
            self.update_dashboard_stats()
    
    def update_dashboard_stats(self):
        """Update detailed dashboard statistics"""
        cursor = self.conn.cursor()
        
        # Total members
        cursor.execute("SELECT COUNT(*) FROM members")
        self.stats_labels['total_members'].setText(str(cursor.fetchone()[0]))
        
        # Active members
        cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
        self.stats_labels['active_members'].setText(str(cursor.fetchone()[0]))
        
        # Expired members
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE end_date < date('now') AND status = 'Active'
        """)
        self.stats_labels['expired_members'].setText(str(cursor.fetchone()[0]))
        
        # Total revenue
        cursor.execute("SELECT COALESCE(SUM(amount_paid), 0) FROM members")
        total_rev = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COALESCE(SUM(payment_amount), 0) FROM visits")
        visit_rev = cursor.fetchone()[0] or 0
        try:
            total_rev = float(total_rev)
            visit_rev = float(visit_rev)
        except (ValueError, TypeError):
            total_rev = 0.0
            visit_rev = 0.0
        self.stats_labels['total_revenue'].setText("KSh {:,.0f}".format(total_rev + visit_rev))
        
        # This month revenue
        cursor.execute("""
            SELECT COALESCE(SUM(payment_amount), 0) FROM visits 
            WHERE strftime('%Y-%m', visit_date) = strftime('%Y-%m', 'now')
        """)
        month_rev = cursor.fetchone()[0] or 0
        try:
            month_rev = float(month_rev)
        except (ValueError, TypeError):
            month_rev = 0.0
        self.stats_labels['month_revenue'].setText("KSh {:,.0f}".format(month_rev))
        
        # Today's visits
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM visits WHERE date(visit_date) = ?", (today,))
        self.stats_labels['today_visits'].setText(str(cursor.fetchone()[0]))
        
        # Average daily visits (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) FROM visits 
            WHERE visit_date >= date('now', '-30 days')
        """)
        total_visits = cursor.fetchone()[0]
        avg_visits = total_visits / 30
        self.stats_labels['avg_visits'].setText("{:.1f}".format(avg_visits))
        
        # Member retention rate (simplified calculation)
        cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
        active = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM members")
        total = cursor.fetchone()[0]
        retention = (active / total * 100) if total > 0 else 0
        self.stats_labels['retention_rate'].setText("{:.1f}%".format(retention))
    
    def update_member_combos(self):
        """Update member combo boxes"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM members WHERE status = 'Active' ORDER BY name")
        members = cursor.fetchall()
        
        # Clear and populate combo boxes
        self.visit_member_combo.clear()
        self.report_member_combo.clear()
        
        for member_id, name in members:
            self.visit_member_combo.addItem(name, member_id)
            self.report_member_combo.addItem(name, member_id)
    
    def update_expiry_alerts(self):
        """Update expiry alerts display"""
        cursor = self.conn.cursor()
        
        # Get members expiring or expired
        cursor.execute("""
            SELECT id, name, phone, email, end_date, status
            FROM members 
            WHERE end_date <= date('now', '+7 days') AND status = 'Active'
            ORDER BY end_date
        """)
        
        alerts = cursor.fetchall()
        
        # Count by status
        expired_count = 0
        urgent_count = 0
        warning_count = 0
        
        for alert in alerts:
            end_date = datetime.strptime(alert[4], '%Y-%m-%d')
            days_left = (end_date - datetime.now()).days
            
            if days_left < 0:
                expired_count += 1
            elif days_left <= 3:
                urgent_count += 1
            else:
                warning_count += 1
        
        # Update summary labels
        if hasattr(self, 'expired_label'):
            self.expired_label.setText("EXPIRED: {}".format(expired_count))
            self.urgent_label.setText("URGENT (1-3 days): {}".format(urgent_count))
            self.warning_label.setText("WARNING (4-7 days): {}".format(warning_count))
        
        # Update alerts table
        if hasattr(self, 'alerts_table'):
            self.alerts_table.setRowCount(len(alerts))
            
            for row, alert in enumerate(alerts):
                end_date = datetime.strptime(alert[4], '%Y-%m-%d')
                days_left = (end_date - datetime.now()).days
                
                # Status with color coding
                if days_left < 0:
                    status_text = "EXPIRED"
                    status_color = "#e74c3c"
                elif days_left <= 3:
                    status_text = "URGENT"
                    status_color = "#f39c12"
                else:
                    status_text = "WARNING"
                    status_color = "#f1c40f"
                
                status_item = QTableWidgetItem(status_text)
                status_item.setBackground(QColor(status_color))
                status_item.setForeground(QColor("white" if days_left < 4 else "black"))
                
                self.alerts_table.setItem(row, 0, status_item)
                self.alerts_table.setItem(row, 1, QTableWidgetItem(alert[1]))  # name
                self.alerts_table.setItem(row, 2, QTableWidgetItem(alert[2] or ""))  # phone
                self.alerts_table.setItem(row, 3, QTableWidgetItem(alert[3] or ""))  # email
                self.alerts_table.setItem(row, 4, QTableWidgetItem(alert[4]))  # end_date
                self.alerts_table.setItem(row, 5, QTableWidgetItem(str(days_left)))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                
                renew_btn = QPushButton("🔄 Renew")
                renew_btn.setStyleSheet(self.get_button_style("#27ae60"))
                renew_btn.setMaximumHeight(25)
                renew_btn.clicked.connect(lambda checked, m_id=alert[0]: self.renew_membership(m_id))
                
                actions_layout.addWidget(renew_btn)
                actions_layout.addStretch()
                
                self.alerts_table.setCellWidget(row, 6, actions_widget)
    
    def update_payment_summary(self):
        """Update daily payment summary"""
        if not hasattr(self, 'payment_method_labels'):
            return
            
        cursor = self.conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for method in ["Cash", "M-Pesa", "Bank Transfer", "Card"]:
            cursor.execute("""
                SELECT COALESCE(SUM(payment_amount), 0) FROM visits 
                WHERE date(visit_date) = ? AND payment_method = ?
            """, (today, method))
            
            amount = cursor.fetchone()[0] or 0
            try:
                amount = float(amount)
            except (ValueError, TypeError):
                amount = 0.0
            self.payment_method_labels[method].setText("KSh {:,.0f}".format(amount))
    
    def load_recent_activity(self):
        """Load recent activity into dashboard"""
        if not hasattr(self, 'activity_list'):
            return
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 'Visit' as type, m.name, v.visit_date, v.payment_amount, v.payment_method
            FROM visits v
            JOIN members m ON v.member_id = m.id
            WHERE date(v.visit_date) = date('now')
            UNION ALL
            SELECT 'Registration' as type, name, registration_date, amount_paid, payment_method
            FROM members
            WHERE date(registration_date) = date('now')
            ORDER BY 3 DESC
            LIMIT 10
        """)
        
        activities = cursor.fetchall()
        self.activity_list.clear()
        
        for activity in activities:
            activity_type, name, timestamp, amount, method = activity
            
            if activity_type == "Visit":
                try:
                    amount_val = float(amount) if amount else 0
                except (ValueError, TypeError):
                    amount_val = 0
                    
                if amount_val > 0:
                    text = "🏃 {} visited - Paid KSh {} via {}".format(name, amount_val, method)
                else:
                    text = "🏃 {} visited".format(name)
            else:
                try:
                    amount_val = float(amount) if amount else 0
                except (ValueError, TypeError):
                    amount_val = 0
                text = "👤 New member: {} registered - KSh {} via {}".format(name, amount_val, method)
            
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime('%I:%M %p')
                text = "[{}] {}".format(time_str, text)
            except:
                pass
            
            self.activity_list.addItem(text)
    
    def search_members(self, text):
        """Search members by name, phone, or email"""
        for row in range(self.members_table.rowCount()):
            match = False
            for col in range(4):  # Search in name, phone, email columns
                item = self.members_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            
            self.members_table.setRowHidden(row, not match)
    
    def filter_members(self, filter_type):
        """Filter members by status"""
        cursor = self.conn.cursor()
        
        if filter_type == "All Members":
            query = "SELECT id FROM members"
            params = ()
        elif filter_type == "Active":
            query = "SELECT id FROM members WHERE status = 'Active'"
            params = ()
        elif filter_type == "Expired":
            query = "SELECT id FROM members WHERE end_date < date('now') AND status = 'Active'"
            params = ()
        elif filter_type == "Expiring Soon":
            next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            query = """SELECT id FROM members 
                      WHERE end_date <= ? AND end_date >= date('now') AND status = 'Active'"""
            params = (next_week,)
        
        cursor.execute(query, params)
        visible_ids = [str(row[0]) for row in cursor.fetchall()]
        
        # Hide/show rows based on filter
        for row in range(self.members_table.rowCount()):
            id_item = self.members_table.item(row, 0)
            if id_item:
                self.members_table.setRowHidden(row, id_item.text() not in visible_ids)
    
    def quick_add_member(self):
        """Quick add member dialog"""
        self.add_member()
    
    def quick_record_visit(self):
        """Switch to visits tab for quick recording"""
        self.tab_widget.setCurrentIndex(2)
    
    def add_member(self):
        """Add new member dialog"""
        dialog = MemberDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
    
    def edit_member(self, member_id):
        """Edit member dialog"""
        dialog = MemberDialog(self, member_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
    
    def delete_member(self, member_id):
        """Delete member with confirmation"""
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            'Are you sure you want to delete this member?\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM visits WHERE member_id = ?", (member_id,))
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            self.conn.commit()
            
            QMessageBox.information(self, "Success", "Member deleted successfully!")
            self.load_data()
    
    def record_visit(self):
        """Record a new visit"""
        if self.visit_member_combo.currentData() is None:
            QMessageBox.warning(self, "Error", "Please select a member!")
            return
        
        member_id = self.visit_member_combo.currentData()
        payment_amount = 0
        payment_method = self.visit_payment_method.currentText()
        notes = self.visit_notes_input.text()
        
        # Parse payment amount
        if self.visit_payment_input.text():
            try:
                payment_amount = float(self.visit_payment_input.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter a valid payment amount!")
                return
        
        # Insert visit record
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO visits (member_id, payment_amount, payment_method, notes)
            VALUES (?, ?, ?, ?)
        """, (member_id, payment_amount, payment_method, notes))
        
        self.conn.commit()
        
        # Clear inputs
        self.visit_payment_input.clear()
        self.visit_payment_method.setCurrentText("None")
        self.visit_notes_input.clear()
        
        QMessageBox.information(self, "Success", "Visit recorded successfully!")
        self.load_data()
    
    def delete_visit(self, visit_id):
        """Delete visit record"""
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            'Are you sure you want to delete this visit record?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM visits WHERE id = ?", (visit_id,))
            self.conn.commit()
            
            QMessageBox.information(self, "Success", "Visit deleted successfully!")
            self.load_data()
    
    def renew_membership(self, member_id):
        """Renew membership dialog"""
        dialog = RenewalDialog(self, member_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
    
    def generate_payment_report(self):
        """Generate payment report for selected date range"""
        date_from = self.date_from.date().toString('yyyy-MM-dd')
        date_to = self.date_to.date().toString('yyyy-MM-dd')
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.visit_date, m.name, v.payment_amount, v.payment_method, 
                   'Visit Payment' as type, v.notes
            FROM visits v
            JOIN members m ON v.member_id = m.id
            WHERE date(v.visit_date) BETWEEN ? AND ? AND v.payment_amount > 0
            UNION ALL
            SELECT m.registration_date, m.name, m.amount_paid, m.payment_method,
                   'Membership Fee' as type, 'Registration' as notes
            FROM members m
            WHERE date(m.registration_date) BETWEEN ? AND ?
            ORDER BY 1 DESC
        """, (date_from, date_to, date_from, date_to))
        
        payments = cursor.fetchall()
        self.payment_history_table.setRowCount(len(payments))
        
        for row, payment in enumerate(payments):
            for col, value in enumerate(payment):
                if col == 0:  # date formatting
                    try:
                        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        formatted_date = dt.strftime('%Y-%m-%d %I:%M %p')
                        self.payment_history_table.setItem(row, col, QTableWidgetItem(formatted_date))
                    except:
                        self.payment_history_table.setItem(row, col, QTableWidgetItem(str(value)))
                elif col == 2:  # amount formatting
                    try:
                        amount_val = float(value) if value else 0
                        self.payment_history_table.setItem(row, col, QTableWidgetItem("KSh {:,.0f}".format(amount_val)))
                    except (ValueError, TypeError):
                        self.payment_history_table.setItem(row, col, QTableWidgetItem("KSh 0"))
                else:
                    self.payment_history_table.setItem(row, col, QTableWidgetItem(str(value) if value else ""))
    
    def generate_individual_report(self, member_name):
        """Generate individual member report"""
        if not member_name:
            self.member_report_text.clear()
            return
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM members WHERE name = ?", (member_name,))
        member = cursor.fetchone()
        
        if not member:
            return
        
        member_id = member[0]
        
        # Get visit history
        cursor.execute("""
            SELECT visit_date, payment_amount, payment_method, notes
            FROM visits 
            WHERE member_id = ?
            ORDER BY visit_date DESC
        """, (member_id,))
        visits = cursor.fetchall()
        
        # Generate report text
        # Safely convert values to proper types
        try:
            initial_payment = float(member[9]) if member[9] is not None else 0.0
        except (ValueError, TypeError):
            initial_payment = 0.0
            
        try:
            additional_payments = sum(float(v[1]) if v[1] is not None else 0.0 for v in visits)
        except (ValueError, TypeError):
            additional_payments = 0.0
            
        total_paid = initial_payment + additional_payments
        
        try:
            days_since_reg = (datetime.now() - datetime.strptime(member[11], '%Y-%m-%d %H:%M:%S')).days
        except (ValueError, TypeError):
            days_since_reg = 0
            
        try:
            visits_with_payment = len([v for v in visits if v[1] and float(v[1]) > 0])
        except (ValueError, TypeError):
            visits_with_payment = 0
        
        report = """
═══════════════════════════════════════════════════════════════
                        MEMBER PROFILE REPORT
═══════════════════════════════════════════════════════════════

🏷️ BASIC INFORMATION
────────────────────────────────────────────────────────────────
Name:               {}
Phone:              {}
Email:              {}
Address:            {}

💳 MEMBERSHIP DETAILS
────────────────────────────────────────────────────────────────
Membership Type:    {}
Start Date:         {}
End Date:           {}
Status:             {}
Registration Date:  {}

💰 FINANCIAL SUMMARY
────────────────────────────────────────────────────────────────
Initial Payment:    KSh {:,.0f} ({})
Additional Payments: KSh {:,.0f}
Total Paid:         KSh {:,.0f}

📊 MEMBERSHIP ANALYTICS
────────────────────────────────────────────────────────────────
Days Since Registration: {} days
Total Visits:       {}
Visits with Payment: {}
""".format(
            member[1],
            member[2] or 'Not provided',
            member[3] or 'Not provided', 
            member[4] or 'Not provided',
            member[5],
            member[6],
            member[7],
            member[8],
            member[11],
            initial_payment, member[10],
            additional_payments,
            total_paid,
            days_since_reg,
            len(visits),
            visits_with_payment
        )
        
        if member[7]:  # end_date exists
            end_date = datetime.strptime(member[7], '%Y-%m-%d')
            days_left = (end_date - datetime.now()).days
            if days_left >= 0:
                report += "Days Until Expiry:  {} days\n".format(days_left)
            else:
                report += "Days Overdue:       {} days\n".format(abs(days_left))
        
        report += """
📋 VISIT HISTORY ({} total visits)
────────────────────────────────────────────────────────────────
""".format(len(visits))
        
        if visits:
            for i, visit in enumerate(visits[:20], 1):  # Show last 20 visits
                visit_date = visit[0]
                try:
                    payment_amount = float(visit[1]) if visit[1] else 0
                    payment = "KSh {:,.0f} ({})".format(payment_amount, visit[2]) if payment_amount > 0 else "No payment"
                except (ValueError, TypeError):
                    payment = "No payment"
                    
                notes = " - {}".format(visit[3]) if visit[3] else ""
                
                try:
                    dt = datetime.strptime(visit_date, '%Y-%m-%d %H:%M:%S')
                    formatted_date = dt.strftime('%Y-%m-%d %I:%M %p')
                except:
                    formatted_date = visit_date
                
                report += "{:2d}. {} | {}{}\n".format(i, formatted_date, payment, notes)
            
            if len(visits) > 20:
                report += "\n... and {} more visits\n".format(len(visits) - 20)
        else:
            report += "No visits recorded yet.\n"
        
        report += "\n" + "═" * 63 + "\n"
        report += "Report generated on: {}\n".format(datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'))
        report += "═" * 63
        
        self.member_report_text.setPlainText(report)


class MemberDialog(QDialog):
    def __init__(self, parent, member_id=None):
        super().__init__(parent)
        self.parent = parent
        self.member_id = member_id
        self.init_ui()
        if member_id:
            self.load_member_data()
    
    def init_ui(self):
        """Initialize member dialog UI"""
        self.setWindowTitle("Add Member" if not self.member_id else "Edit Member")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Form fields
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        
        self.membership_combo = QComboBox()
        self.membership_combo.addItems([
            "Monthly", "Quarterly", "Half-yearly", "Yearly", "Daily"
        ])
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        self.end_date.setCalendarPopup(True)
        
        self.amount_input = QLineEdit()
        
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["Cash", "M-Pesa", "Bank Transfer", "Card"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        
        # Add fields to form
        form_layout.addRow("Name*:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Address:", self.address_input)
        form_layout.addRow("Membership Type*:", self.membership_combo)
        form_layout.addRow("Start Date*:", self.start_date)
        form_layout.addRow("End Date*:", self.end_date)
        form_layout.addRow("Amount Paid*:", self.amount_input)
        form_layout.addRow("Payment Method:", self.payment_method_combo)
        form_layout.addRow("Status:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet(self.parent.get_button_style("#27ae60"))
        save_btn.clicked.connect(self.save_member)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet(self.parent.get_button_style("#e74c3c"))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect membership type change to auto-calculate end date
        self.membership_combo.currentTextChanged.connect(self.update_end_date)
    
    def update_end_date(self, membership_type):
        """Update end date based on membership type"""
        start_date = self.start_date.date()
        
        if membership_type == "Daily":
            end_date = start_date.addDays(1)
        elif membership_type == "Monthly":
            end_date = start_date.addMonths(1)
        elif membership_type == "Quarterly":
            end_date = start_date.addMonths(3)
        elif membership_type == "Half-yearly":
            end_date = start_date.addMonths(6)
        elif membership_type == "Yearly":
            end_date = start_date.addYears(1)
        else:
            end_date = start_date.addMonths(1)
        
        self.end_date.setDate(end_date)
    
    def load_member_data(self):
        """Load existing member data for editing"""
        cursor = self.parent.conn.cursor()
        cursor.execute("SELECT * FROM members WHERE id = ?", (self.member_id,))
        member = cursor.fetchone()
        
        if member:
            self.name_input.setText(member[1] or "")
            self.phone_input.setText(member[2] or "")
            self.email_input.setText(member[3] or "")
            self.address_input.setPlainText(member[4] or "")
            
            membership_index = self.membership_combo.findText(member[5] or "Monthly")
            if membership_index >= 0:
                self.membership_combo.setCurrentIndex(membership_index)
            
            if member[6]:  # start_date
                self.start_date.setDate(QDate.fromString(member[6], "yyyy-MM-dd"))
            
            if member[7]:  # end_date
                self.end_date.setDate(QDate.fromString(member[7], "yyyy-MM-dd"))
            
            self.amount_input.setText(str(member[9] or ""))
            
            payment_index = self.payment_method_combo.findText(member[10] or "Cash")
            if payment_index >= 0:
                self.payment_method_combo.setCurrentIndex(payment_index)
            
            status_index = self.status_combo.findText(member[8] or "Active")
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)
    
    def save_member(self):
        """Save member data"""
        # Validation
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Name is required!")
            return
        
        if not self.amount_input.text().strip():
            QMessageBox.warning(self, "Error", "Amount paid is required!")
            return
        
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount!")
            return
        
        # Prepare data
        data = (
            self.name_input.text().strip(),
            self.phone_input.text().strip() or None,
            self.email_input.text().strip() or None,
            self.address_input.toPlainText().strip() or None,
            self.membership_combo.currentText(),
            self.start_date.date().toString("yyyy-MM-dd"),
            self.end_date.date().toString("yyyy-MM-dd"),
            amount,
            self.payment_method_combo.currentText(),
            self.status_combo.currentText()
        )
        
        cursor = self.parent.conn.cursor()
        
        if self.member_id:
            # Update existing member
            cursor.execute("""
                UPDATE members SET name=?, phone=?, email=?, address=?, 
                membership_type=?, start_date=?, end_date=?, amount_paid=?,
                payment_method=?, status=?
                WHERE id=?
            """, data + (self.member_id,))
        else:
            # Insert new member
            cursor.execute("""
                INSERT INTO members (name, phone, email, address, membership_type, 
                start_date, end_date, amount_paid, payment_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
        
        self.parent.conn.commit()
        
        QMessageBox.information(self, "Success", 
                              "Member updated successfully!" if self.member_id 
                              else "Member added successfully!")
        self.accept()


class RenewalDialog(QDialog):
    def __init__(self, parent, member_id):
        super().__init__(parent)
        self.parent = parent
        self.member_id = member_id
        self.init_ui()
        self.load_member_data()
    
    def init_ui(self):
        """Initialize renewal dialog UI"""
        self.setWindowTitle("Renew Membership")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Member info display
        self.member_info = QLabel()
        self.member_info.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.member_info)
        
        # Renewal form
        form_layout = QFormLayout()
        
        self.membership_combo = QComboBox()
        self.membership_combo.addItems([
            "Monthly", "Quarterly", "Half-yearly", "Yearly", "Daily"
        ])
        
        self.new_end_date = QDateEdit()
        self.new_end_date.setDate(QDate.currentDate().addMonths(1))
        self.new_end_date.setCalendarPopup(True)
        
        self.renewal_amount = QLineEdit()
        
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "M-Pesa", "Bank Transfer", "Card"])
        
        form_layout.addRow("New Membership Type:", self.membership_combo)
        form_layout.addRow("New End Date:", self.new_end_date)
        form_layout.addRow("Renewal Amount:", self.renewal_amount)
        form_layout.addRow("Payment Method:", self.payment_method)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        renew_btn = QPushButton("🔄 Renew Membership")
        renew_btn.setStyleSheet(self.parent.get_button_style("#27ae60"))
        renew_btn.clicked.connect(self.renew_membership)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet(self.parent.get_button_style("#e74c3c"))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(renew_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect membership change to update end date
        self.membership_combo.currentTextChanged.connect(self.update_end_date)
    
    def load_member_data(self):
        """Load member data for renewal"""
        cursor = self.parent.conn.cursor()
        cursor.execute("SELECT name, phone, end_date, membership_type FROM members WHERE id = ?", 
                      (self.member_id,))
        member = cursor.fetchone()
        
        if member:
            name, phone, end_date, membership_type = member
            
            info_text = """
Member: {}
Phone: {}
Current End Date: {}
Current Membership: {}
            """.format(name, phone or 'Not provided', end_date, membership_type)
            self.member_info.setText(info_text.strip())
            
            # Set default values
            membership_index = self.membership_combo.findText(membership_type or "Monthly")
            if membership_index >= 0:
                self.membership_combo.setCurrentIndex(membership_index)
            
            self.update_end_date(membership_type)
    
    def update_end_date(self, membership_type):
        """Update end date based on membership type"""
        # Start from current end date or today, whichever is later
        cursor = self.parent.conn.cursor()
        cursor.execute("SELECT end_date FROM members WHERE id = ?", (self.member_id,))
        current_end = cursor.fetchone()[0]
        
        if current_end:
            start_date = max(QDate.currentDate(), 
                           QDate.fromString(current_end, "yyyy-MM-dd"))
        else:
            start_date = QDate.currentDate()
        
        if membership_type == "Daily":
            end_date = start_date.addDays(1)
        elif membership_type == "Monthly":
            end_date = start_date.addMonths(1)
        elif membership_type == "Quarterly":
            end_date = start_date.addMonths(3)
        elif membership_type == "Half-yearly":
            end_date = start_date.addMonths(6)
        elif membership_type == "Yearly":
            end_date = start_date.addYears(1)
        else:
            end_date = start_date.addMonths(1)
        
        self.new_end_date.setDate(end_date)
    
    def renew_membership(self):
        """Process membership renewal"""
        if not self.renewal_amount.text().strip():
            QMessageBox.warning(self, "Error", "Renewal amount is required!")
            return
        
        try:
            amount = float(self.renewal_amount.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount!")
            return
        
        # Update member record
        cursor = self.parent.conn.cursor()
        cursor.execute("""
            UPDATE members SET 
                end_date = ?,
                membership_type = ?,
                status = 'Active'
            WHERE id = ?
        """, (
            self.new_end_date.date().toString("yyyy-MM-dd"),
            self.membership_combo.currentText(),
            self.member_id
        ))
        
        # Record payment as a visit
        cursor.execute("""
            INSERT INTO visits (member_id, payment_amount, payment_method, notes)
            VALUES (?, ?, ?, ?)
        """, (
            self.member_id,
            amount,
            self.payment_method.currentText(),
            f"Membership renewal - {self.membership_combo.currentText()}"
        ))
        
        self.parent.conn.commit()
        
        QMessageBox.information(self, "Success", "Membership renewed successfully!")
        self.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = GymManagementSystem()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()