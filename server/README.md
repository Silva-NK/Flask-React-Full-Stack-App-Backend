# FLASK-REACT-FULL-STACK-APP
Event-Manager-Flask-React-App-Backend

Event Manager App is a full-stack event management system built with Flask, SQLAlchemy, and React, deployed seamlessly on Render for both frontend and backend. It models an event planning platform where planners can register, log in, and manage their events, guests, and guest attendances. The backend uses Flask-RESTful for API endpoints, Flask-Migrate for database migrations, Flask-CORS for cross-origin requests, and session-based authentication for secure login and logout functionality. Authentication is required for managing events, guests, and attendance data, ensuring protected access to user-specific resources.

This is the back-end repository.

### **Features**

- **User Authentication**: Planners can register, log in, and log out securely.
- **Event Management**: Planners can create, view, edit, and delete events.
- **Guest Management**: Planners can manage guest lists for each event.
- **Attendance Management**: Planners can manage deatils such as guest RSVPs for events and manage their status.
- **Session-based Authentication**: Protects event and guest data, ensuring that each planner can only access their own data.

## **Technologies**

- **Frontend**: React, JSX, CSS
- **Backend**: Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate, Flask-CORS
- **Database**: PostgreSQL (via Render)
- **Deployment**: Render (both frontend and backend)


## Project Structure

.
├── client
│   ├── build
│   ├── node_modules
│   ├── package.json
│   ├── package-lock.json
│   ├── public
│   ├── README.md
│   └── src
│       ├── components
│       │   ├── App.js
│       │   ├── AttendanceForm.js
│       │   ├── EventsForm.js
│       │   ├── GuestsForm.js
│       │   └── NavBar.js
│       ├── contexts
│       │   └── AuthContext.js
│       ├── index.css
│       ├── index.js
│       └── pages
│           ├── AddAttendance.js
│           ├── AddEvents.js
│           ├── AddGuests.js
│           ├── Dashboard.js
│           ├── EditAttendance.js
│           ├── EditEvents.js
│           ├── EditGuests.js
│           ├── EventsPage.js
│           ├── GuestsPage.js
│           ├── LoginPage.js
│           ├── RegisterPage.js
│           └── ViewAttendance.js
├── Pipfile
├── Pipfile.lock
├── README.md
└── server
    ├── app.py
    ├── config.py
    ├── migrations
    ├── models.py
    ├── __pycache__
    └── seed.py


# Backend Overview (Flask)
----------------------------

### **app.py**

This is the main entry point for the Flask application. It sets up configurations, initializes extensions (Flask-SQLAlchemy, Flask-Migrate, Flask-CORS), and includes the API routes and models.

**Key Functions:**

*   **create_app()**: Initializes and configures the Flask app.
    
*   **db.create_all()**: Creates tables in the database (for development only).

---

### **models.py**

Contains SQLAlchemy models that represent the application's data structures. It includes models for `Planner`, `Event`, `Guest`, and `Attendance`.

**Key Models:**

*   **Planner**: Represents a user who manages events.
    
*   **Event**: Represents an event that a planner creates.
    
*   **Guest**: Represents a guest who can attend an event.
    
*   **Attendance**: Represents a guest's RSVP status for a specific event.

---

### **routes.py**

Defines the API endpoints for the app using Flask-RESTful. It includes routes for user authentication (login, logout), event management (CRUD operations), and guest management.

**Key Routes:**

*   `/register` [POST] - Registers a new planner. Takes username, email, and password as form data.
    
*   `/login` [POST] - Logs in a planner using either their username or email and password.

*   `/check_session` [GET] - Checks if the user is logged in by validating their session.

*   `/profile` [GET] - Retrieves the current logged-in planner's profile details (username, email).

*   `/events` [GET, POST] - 
    - [GET] Retrieves all events for the logged-in planner.
    - [POST] Creates a new event for the logged-in planner with event name, description, venue, date, and time.

*   `/events/<int:id>` [GET, PATCH, DELETE] - 
    - [GET] Retrieves a specific event by ID for the logged-in planner.
    - [PATCH] Updates an existing event's details (name, description, venue, date, time).
    - [DELETE] Deletes a specific event by ID.

*   `/guests` [GET, POST] - 
    - [GET] Retrieves all guests for the logged-in planner.
    - [POST] Adds a new guest for the logged-in planner with name, email, and phone.

*   `/guests/<int:id>` [GET, PATCH, DELETE] - 
    - [GET] Retrieves details of a specific guest by ID for the logged-in planner.
    - [PATCH] Updates a guest's information (name, email, phone).
    - [DELETE] Deletes a guest by ID.

*   `/events/<int:event_id>/guests` [GET] - Retrieves all guests attending a specific event for the logged-in planner.

*   `/attendances` [POST] - Creates a new attendance record for a guest attending an event, including RSVP status and plus ones.

*   `/attendances/<int:id>` [GET, PATCH, DELETE] - 
    - [GET] Retrieves attendance details (RSVP status, plus ones) for a specific event/guest.
    - [PATCH] Updates attendance status or the number of plus ones.
    - [DELETE] Deletes a specific attendance record.
    
*   `/logout` [DELETE] - Logs out the current user by clearing the session.

---

### **config.py**

Contains configuration settings for the Flask app, such as the database URI and CORS settings. It loads environment variables for sensitive data (e.g., database credentials) using `python-dotenv`.

---

### **requirements.txt**

Lists all the Python dependencies required for the backend (e.g., Flask, Flask-SQLAlchemy, Flask-RESTful, etc.).

---

### **.env**

Stores environment-specific variables such as the database URI (`DATABASE_URL`) and secret key (`SECRET_KEY`).


# **Frontend Overview (React)**

### **App.js**
The main entry point for the React app. It contains the root component and handles routing between different pages using React Router.

### **components/**
Contains reusable UI components like `AttendanceForm.js`, `EventsForm.js`, `GuestsForm.js`, and `NavBar.js` that are used to display event details and provide form handling for adding guests, events, and attendance.

- **App.js**: The root component that contains the app's layout and routes.
- **AttendanceForm.js**: A component for managing the creation or editing of guest attendance.
- **EventsForm.js**: A component for managing the creation or editing of events.
- **GuestsForm.js**: A component for managing the addition or editing of guests.
- **NavBar.js**: The navigation bar used across the app to access different pages and features.

### **contexts/**
Contains context providers like `AuthContext.js` for managing authentication state across the app.

- **AuthContext.js**: Manages the authentication state and provides login/logout functionality for the user.

### **pages/**
Contains different pages of the application, such as the **EventsPage**, **EventDetailsPage**, and **LoginPage**. These pages are rendered based on routes defined in the app.

- **AddAttendance.js**: Page for adding new attendance records for an event.
- **AddEvents.js**: Page for creating new events.
- **AddGuests.js**: Page for adding new guests to the system.
- **Dashboard.js**: The main dashboard displaying events, guests, and attendance details.
- **EditAttendance.js**: Page for editing existing attendance records.
- **EditEvents.js**: Page for editing event details.
- **EditGuests.js**: Page for editing guest details.
- **EventsPage.js**: Page for displaying all events with options to view, edit, or delete them.
- **GuestsPage.js**: Page for displaying all guests with options to manage them.
- **LoginPage.js**: Page for logging in users.
- **RegisterPage.js**: Page for new users to register.
- **ViewAttendance.js**: Page to view guest attendance for a particular event.

### **index.js**
The entry point for the React app. It renders the root component (`App.js`) and sets up React Router and other necessary setups for the application.

### **index.css**
Global styles for the React app, setting up the theme, layout, and styling for various components across the app.

### **package.json**
Lists frontend dependencies and scripts for building, testing, and deploying the React app.

- Dependencies include React, React Router, Axios, etc.
- Contains build scripts for bundling the app into production-ready code.
- Includes testing scripts to run unit tests using Jest or other test frameworks.

---


## Setting Up the Project Locally

1. **Clone the repository**  
   Clone the repository to your local machine using Git:

   ```bash
   git clone https://github.com/your-username/project-name.git
   ```

2. **Navigate into the project directory**
Move into the project directory:

    ```bash
    cd project-name
    ```

3. **Install Backend Dependencies**
Make sure you're inside the project directory and install the backend dependencies listed in the Pipfile:

    ```bash
    pipenv install
    ```

4. **Set Up Environment Variable**s
Create a .env file in the root of your project and add the necessary environment variables. Here’s an example:

    ```bash
    DATABASE_URL=your_database_url
    SECRET_KEY=your_secret_key
    PORT=your_port
    ```

5. **Run Migrations**
Before running the app, you need to set up the database. You can run the migrations with the following command:

    ```bash
    flask db upgrade
    ```

6. **Start the Backend Server**
Run the Flask server to start the backend:

    ```bash
    python app.py
    ```

By default, this will start the server on http://127.0.0.1:5555/.

7. **Install Frontend Dependencies**
Navigate to the client directory and install the frontend dependencies:

    ```bash
    cd client
    npm install
    ```

8. **Start the Frontend Server**
Run the React development server:

    ```bash
    npm start
    ```

This will start the frontend on http://localhost:3000/.

9. **Open Your Browser**
Open your browser and go to http://localhost:3000/ to see the application running.


## Deploying the App

**NOTE:** Still in the works.

## Resources

- [Flask-React-Full-Stack-App Git Repo](https://github.com/Silva-NK/Flask-React-Full-Stack-App)

- [Deployed Front End](https://event-manager-flask-react-app.onrender.com)

- [Flask-React-Full-Stack-App-Backend Git Repo](https://github.com/Silva-NK/Flask-React-Full-Stack-App-Backend)

- [Back End](https://event-manager-flask-react-app-backend.onrender.com)