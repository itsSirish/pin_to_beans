# PinToBeans 📌

A Pinterest-inspired social platform built with Django that allows users to create personalized pinboards, share images, and discover content through curated follow streams.

![PinToBeans Architecture](https://github.com/itsSirish/pin_to_beans/blob/main/PinToBeans%20Architecture.png)

## 🚀 Features

### Core Functionality
- **User Management**: Secure registration, login, and profile customization
- **Pinboards**: Create categorized collections of images
- **Pin & Repin**: Upload images or pin from URLs, with full repin chain tracking
- **Social Features**: Friend system, likes, comments with privacy controls
- **Follow Streams**: Create custom feeds aggregating multiple pinboards
- **Search**: Keyword-based search across pins and boards
- **Image Storage**: Robust blob storage with URL fallback

### Advanced Features
- **Privacy Controls**: Friend-only commenting on boards
- **Automatic Collections**: "Liked Pins" board for quick saves
- **Repin Tracking**: Maintains connection to original pins for like aggregation
- **Real-time Updates**: AJAX-powered interface for seamless interactions
- **Data Integrity**: Database triggers prevent circular repins and enforce permissions

## 🛠️ Tech Stack

- **Backend**: Django 5.2, Python
- **Database**: PostgreSQL with advanced triggers and constraints
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), AJAX
- **Styling**: Custom CSS with responsive design
- **Image Processing**: Binary blob storage with URL support
- **Authentication**: Session-based with secure password handling

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/itsSirish/pin_to_beans.git
cd pin_to_beans
```

### 2. Install dependencies
```bash
pip install django psycopg2-binary requests
```

### 3. Configure PostgreSQL
Create a PostgreSQL database and update the credentials in `pin_to_beans/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'PinToBeans',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Run database migrations
```bash
python manage.py migrate
```

### 5. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 6. Start development server
```bash
python manage.py runserver
```

### 7. Access the application
Open `http://127.0.0.1:8000` in your browser and register a new account!

## 🎯 Usage

### Getting Started
1. **Register**: Create your account with name, email, and password
2. **Create Boards**: Set up categorized pinboards for your interests
3. **Pin Images**: Upload from your device or pin from web URLs
4. **Discover**: Browse public boards and follow interesting users
5. **Curate**: Create follow streams combining multiple boards into custom feeds

### Key Workflows
- **Pin from URL**: Paste any image URL to add it to your boards
- **Repin Content**: Share others' pins to your own boards (maintains original attribution)
- **Social Interaction**: Send friend requests, like pins, comment on boards
- **Stream Creation**: Build personalized feeds from followed boards

## 🗄️ Database Schema

The application uses a sophisticated relational database design with:

- **BCNF Normalization**: Eliminates redundancy and update anomalies
- **Referential Integrity**: Comprehensive foreign key constraints
- **Trigger-Based Validation**: Prevents circular repins, enforces friendship rules
- **Optimized Queries**: Efficient many-to-many relationships and indexing

### Key Entities
- `User`: Account management and authentication
- `Pinboard`: Categorized image collections
- `Pin`: Individual image posts with repin tracking
- `Image`: Binary storage with metadata
- `Friendship`: Symmetric relationship management
- `FollowStream`: Custom feed curation

## 🎨 Frontend Architecture

- **AJAX Navigation**: Seamless page transitions without full reloads
- **Responsive Design**: Mobile-friendly interface with Pinterest-style masonry layout
- **Real-time Interactions**: Instant like/unlike, dynamic loading
- **Form Validation**: Client and server-side validation for robust data entry

## 📁 Project Structure

```
pin_to_beans/
├── core/                   # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # Request handlers
│   ├── forms.py           # Form definitions
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, images
│   └── migrations/        # Database migrations
├── pin_to_beans/          # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── manage.py              # Django management script
└── README.md              # This file
```

## 🚦 Key Endpoints

- `/` - Dashboard with personalized feed
- `/pinboards/` - User's pinboard management
- `/friends/` - Social features and friend requests
- `/search/` - Content discovery
- `/profile/<id>/` - User profiles
- `/streams/` - Follow stream management
- `/pin/new/` - Create new pins

## 🔧 Configuration

### Database Setup
1. Create PostgreSQL database named `PinToBeans`
2. Update credentials in `settings.py`
3. Run migrations to create tables and triggers

### Environment Variables
Key settings in `pin_to_beans/settings.py`:
- Database credentials
- Debug mode
- Static file configuration
- Logging setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow Django best practices
- Maintain database integrity with proper migrations
- Test new features thoroughly
- Update documentation for new endpoints

## 📸 Screenshots

The application features a clean, Pinterest-inspired interface with:
- Masonry-style pin layouts
- Responsive design for all devices
- Real-time social interactions
- Intuitive navigation and search

## 🔐 Security Features

- Password validation and secure storage
- CSRF protection on all forms
- SQL injection prevention through Django ORM
- Permission-based access control
- Database triggers for data integrity

## 📝 License

This project was developed as part of an academic assignment for CS6083 Database Systems course. Please contact the authors for usage permissions.

## 👥 Authors

- **Visweswar Sirish Parupudi** - [vsp7230@nyu.edu](mailto:vsp7230@nyu.edu)

## 🎓 Academic Context

This project was developed for **CS6083 Database Systems, Spring 2025** at New York University. It demonstrates advanced database design principles, full-stack web development, and modern software engineering practices.

## 📚 Documentation

For detailed technical documentation, database schema design, and implementation details, refer to the [project report](./PinToBeans_Report.pdf) included in this repository.

---

⭐ **Star this repository if you found it helpful!**

Built with Django and PostgreSQL | © 2025 NYU CS6083
