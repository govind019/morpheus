# Form Builder

A powerful and flexible Django-based form builder application that allows users to create, manage, and analyze custom forms. Built with Django and Django REST Framework, this application provides a modern UI and comprehensive analytics for form responses.

## Features

- **Form Management**
  - Create and manage custom forms
  - Add different question types (text, dropdown, checkbox)
  - Set required/optional fields
  - Reorder questions easily

- **Form Submission**
  - Anonymous form submissions supported
  - Real-time validation
  - Mobile-friendly responsive design
  - Support for multiple answer types

- **Analytics Dashboard**
  - View total responses and response rates
  - Track average completion time
  - Visualize responses with charts
  - Export responses to CSV
  - Word frequency analysis for text responses

- **User Management**
  - User registration and authentication
  - Form ownership and permissions
  - Secure access control

## Technology Stack

- **Backend**: Django 5.0, Django REST Framework 3.14.0
- **Frontend**: Bootstrap 5, jQuery, Chart.js
- **Database**: SQLite (default), compatible with PostgreSQL
- **Additional**: django-crispy-forms, django-cors-headers

## Installation

1. Clone the repository:
bash
git clone https://github.com/yourusername/form-builder.git
cd form-builder


2. Create a virtual environment and activate it:
bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


3. Install dependencies:
bash
pip install -r requirements.txt


4. Apply database migrations:
bash
python manage.py migrate


5. Create a superuser (admin):
bash
python manage.py createsuperuser


6. Run the development server:
bash
python manage.py runserver


The application will be available at http://localhost:8000

## Environment Variables

Create a .env file in the project root with the following variables:
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
  change the readme code and creeate a new read me
