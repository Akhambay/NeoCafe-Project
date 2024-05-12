# NeoCafe

## About
Neocafe is an innovative mobile application designed to automate the process of placing orders in cafes/restaurants. It enables users to place orders quickly and conveniently, track their status in real time, and receive notifications upon order readiness. Neocafe has various user roles, including customers, administrators, waiters, and baristas, making it a versatile tool for enhancing service and process management in cafe settings.

## Installation
Ensure your environment is set up with the following:

1. **Python version 3.x, redis-server, and pip3.**
2. Clone the repository:
```
git clone https://github.com/Akhambay/NeoCafe-Project.git
```
3. Navigate to the project directory:
```
cd NeoCafe-Project
```
4. Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```
5. Install the required packages:
```
pip3 install -r requirements.txt
```
6. Make migrations and migrate:
```
python3 manage.py makemigrations
python3 manage.py migrate
```
7. Create a superuser:
```
python3 manage.py createsuperuser
```
Run the app and celery:
```
python3 -m uvicorn config.asgi:application --reload
celery -A config worker -l info
```
10. Open the app in your browser at http://127.0.0.1:8000/schema/swagger/.
    
## Technologies and Services
Neocafe utilizes a state-of-the-art technology stack including:

**Python 3.8:** For backend development, provides high speed development and efficiency.
**Django REST Framework:** A powerful and flexible framework for building APIs.
**Redis & Celery:** For asynchronous task processing and data caching.
**Cloudinary:** Provides convenient media management.

# Roles
**Customer:** Can register, edit profile, view menus, place orders, track their status and receive notifications.
**Administrator:** Can create branches, menu items, add employees and stock items.
**Waiter/Barista:** Processes and fulfills orders.

Using the API
The Neocafe backend provides a RESTful API for managing orders, user accounts, and more. Below is a guide on how to start interacting with our API endpoints.

API Overview
Our API allows you to programmatically perform actions like creating new orders, updating user profiles, and more. The API is organized around REST. Our API has predictable resource-oriented URLs, accepts form-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

Authentication
Our API uses API keys to authenticate requests. You can view and manage your API keys in the Dashboard. Your API keys carry many privileges, so be sure to keep them secure! Do not share your secret API keys in publicly accessible areas such as GitHub, client-side code, and so forth.

Contributing
We welcome contributions to the Neocafe project! If you're interested in helping improve Neocafe, please follow these steps:

Fork the repository: This creates your own copy of the repository where you can make your changes.
Create a new branch: Use the command git checkout -b feature/AmazingFeature to create a new branch for your feature.
Make your changes: Implement your new feature or bug fix in this branch.
Commit your changes: Use the command git commit -m 'Add some AmazingFeature' to save your changes with a descriptive commit message.
Push the branch: Use the command git push origin feature/AmazingFeature to upload your changes to your forked repository.
Open a Pull Request: Go to the GitHub page of your forked repository and click on "New pull request" to submit your changes for review.

Author & Contact
Assyl Akhambay
If you have questions, suggestions, or would like to report a bug, feel free to contact me at assyl.akhambay@gmail.com, or contact me on LinkedIn (assyl-akhambay)
