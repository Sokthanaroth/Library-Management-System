# Library Management System

A comprehensive Django-based library management system with modern features including barcode scanning, automated fine calculation, and comprehensive reporting.

## Features

### Core Functionality
- **Book Management**: Complete CRUD operations for books with categories, authors, and publishers
- **Member Management**: User registration and member profile management
- **Borrow/Return System**: Automated borrowing with due date tracking and fine calculation
- **Barcode Integration**: Generate and scan barcodes for quick book identification
- **Dashboard**: Real-time statistics and activity monitoring
- **Reporting**: Excel report generation for books, members, and transactions

### Advanced Features
- **3-Book Borrowing Limit**: Business rule preventing members from borrowing more than 3 books
- **Fine Calculation**: Automatic $2/day overdue fines
- **Barcode Scanning**: Camera-based barcode scanning for mobile devices
- **Responsive Design**: Bootstrap-based UI that works on all devices
- **REST API**: Django REST Framework integration for API access

## Project Structure

```
library_management_system/
├── library_project/          # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
├── library_app/              # Main Django app
│   ├── migrations/          # Database migrations
│   ├── management/          # Custom management commands
│   ├── templates/           # HTML templates
│   ├── static/              # Static files (CSS, JS, images)
│   ├── emails/              # Email templates
│   ├── fixtures/            # Test data fixtures
│   ├── tests/               # Unit and integration tests
│   ├── __init__.py
│   ├── admin.py             # Django admin configuration
│   ├── api.py               # REST API views
│   ├── apps.py
│   ├── decorators.py        # Custom decorators
│   ├── forms.py             # Django forms
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── signals.py           # Django signals
│   ├── urls.py              # App URL routing
│   ├── utils.py             # Utility functions
│   ├── validators.py        # Custom validators
│   └── views.py             # Django views
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── tests/                   # Project-wide tests
├── media/                   # User-uploaded files
├── static/                  # Project static files
├── db.sqlite3               # SQLite database
├── manage.py                # Django management script
└── README.md
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd library_management_system
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Usage

### Web Interface
- Access the application at `http://127.0.0.1:8000`
- Login with your superuser credentials
- Use the dashboard for an overview of library operations

### API Access
- REST API available at `http://127.0.0.1:8000/api/`
- Authentication required for most endpoints

### Barcode Features
- Generate barcodes for books from the book detail page
- Use the barcode scanner interface for quick book lookup
- Print barcodes for physical book labeling

## Key Models

### Book
- Title, subtitle, authors, ISBN
- Publisher, categories, description
- Available copies, status, barcode
- Cover image upload

### Member
- Linked to Django User model
- Membership details and borrowing limits
- Fine tracking and payment status

### BorrowRecord
- Book and member relationship
- Borrow/return dates and due dates
- Fine calculation and status tracking

### Category, Author, Publisher
- Supporting models for book organization
- Full CRUD operations available

## Business Rules

1. **Borrowing Limit**: Members can borrow maximum 3 books simultaneously
2. **Availability Check**: Books must have available copies to be borrowed
3. **Fine Calculation**: $2.00 per day overdue
4. **Membership Validation**: Members must have valid membership to borrow

## Technologies Used

- **Backend**: Django 4.2, Python 3.8+
- **Database**: SQLite (development), MySQL (production)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **API**: Django REST Framework
- **Barcode**: python-barcode library
- **Rich Text**: CKEditor for book descriptions
- **Email**: Django email system with Gmail SMTP

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.