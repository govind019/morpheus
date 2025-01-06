# Dynamic Form Creator

An innovative application designed for seamless form creation, management, and analysis. Built with Django and a modern tech stack, this solution empowers users to build custom forms, collect responses, and gain insights through interactive analytics.

---

## Highlights

- **Customizable Form Design**  
  Effortlessly build forms with drag-and-drop functionality and support for multiple field types (text, dropdown, checkboxes).  
  Set conditional logic and validations for enhanced user experiences.

- **Seamless Response Collection**  
  Gather responses securely through a responsive design optimized for desktop and mobile devices.  
  Save time with real-time form validation.

- **Interactive Insights**  
  Monitor responses through visually engaging dashboards.  
  Export data to CSV for offline analysis or integrate with external tools.  
  Discover patterns with word cloud generation for open-ended questions.

- **Secure User Access**  
  Role-based permissions ensure forms and data are accessible only to authorized users.  
  Includes robust authentication for user accounts.

---

## Core Technologies

- **Backend**: Django (5.0) and Django REST Framework (3.14.0)  
- **Frontend**: Bootstrap 5  
- **Database**: SQLite for quick setup, scalable with PostgreSQL  
- **Enhancements**: django-crispy-forms for streamlined form styling

---


## Installation

1. Clone the repository:
bash
git clone https://github.com/yourusername/form-builder.git
cd form-builder


2. Apply database migrations:
bash
python manage.py migrate


3. Create a superuser (admin):
bash
python manage.py createsuperuser


4. Run the development server:
bash
python manage.py runserver


The application will be available at http://localhost:8000

## Environment Variables

Create a .env file in the project root with the following variables:
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
  change the readme code and creeate a new read me
