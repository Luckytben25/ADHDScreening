# ADHDScreening
Below is a concise and informative description you can use for your GitHub repository to provide an overview of your ADHD Screening Platform project. Feel free to adjust it based on your preferences or additional details.

# ADHD Screening Platform

The ADHD Screening Platform is a web-based application designed to assist users in assessing their ADHD (Attention Deficit Hyperactivity Disorder) confidence levels using a machine learning approach. Built with Flask, this project leverages a MySQL database to securely store user profiles, assessment results, and activity logs, offering a robust and interactive experience.

## Features
- **User Authentication**: Secure login and registration with password hashing.
- **ADHD Prediction**: Employs a pre-trained Linear Regression model to predict ADHD confidence based on attention test scores (e.g., omissions, reaction speed).
- **Database Integration**: Stores data in a MySQL database with tables for users, results, and logs.
- **Responsive UI**: Utilizes Tailwind CSS for a modern, user-friendly interface.
- **Result Analysis**: Provides detailed results, including scores, risk levels, and professional consultation recommendations.

## Technologies
- **Backend**: Python, Flask
- **Machine Learning**: scikit-learn, joblib
- **Database**: MySQL, pymysql
- **Frontend**: HTML, Tailwind CSS
- **Dependencies**: numpy, pandas

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/adhd-screening-platform.git

   Below is a detailed **Tech Stack** for your ADHD Screening Platform project, outlining the technologies used in its development. This can be included in your GitHub `README.md` or used for documentation purposes. The current date and time is 11:42 PM +0530 on Saturday, September 06, 2025.

---

### Tech Stack

The ADHD Screening Platform is built using a combination of modern technologies to ensure a robust, scalable, and user-friendly application. The stack is divided into frontend, backend, database, machine learning, and development tools.

#### Frontend
- **HTML5**: Used for structuring the web pages, including templates for the dashboard, checklist, and result pages.
- **Tailwind CSS**: A utility-first CSS framework providing a responsive and customizable design system for a modern user interface.
- **JavaScript**: Employed for client-side interactivity, such as form validation and AJAX requests to the backend.

#### Backend
- **Python**: The primary programming language, leveraging its simplicity and extensive libraries for web development and machine learning.
- **Flask**: A lightweight WSGI web framework used to build the RESTful API, handle routing, and manage server-side logic.
- **Werkzeug**: Integrated with Flask for security features like password hashing.

#### Database
- **MySQL**: A relational database management system to store user data, assessment results, and activity logs securely.
- **PyMySQL**: A Python library for connecting to and interacting with the MySQL database.

#### Machine Learning
- **scikit-learn**: A machine learning library used to train and implement the Linear Regression model for ADHD confidence prediction.
- **NumPy**: Supports numerical computations and array operations for data processing.
- **Pandas**: Used for data manipulation and analysis, particularly for handling the ADHD test dataset.
- **joblib**: Employed to serialize and deserialize the trained model, scaler, and feature lists for persistent storage.

#### Development Tools
- **Git**: Version control system for managing code changes and collaborating on the project.
- **GitHub**: Hosting platform for the repository, enabling version tracking, issue management, and community contributions.
- **Virtualenv**: Used to create isolated Python environments for dependency management.
- **pip**: Package manager for installing and managing Python dependencies.
- **unittest**: Framework for writing and running unit tests to ensure code reliability.

#### Optional Enhancements (Future Consideration)
- **Flask-CORS**: For enabling Cross-Origin Resource Sharing if deploying to multiple domains.
- **Chart.js**: Potential addition for visualizing prediction results (if integrated later).
- **GitHub Actions**: For continuous integration and automated testing workflows.

---
