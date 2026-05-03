VetCare Lite - Documentation

Elīza Cif  
Programmēšana II Projekts
April-May 2026

1. Project Description
Lightweight web application designed for small veterinary clinics to help clinic staff manage pet owners, pets, and appointments efficiently. 

Includes a simple ML feature that classifies common pet symptoms 
and suggests possible conditions (e.g. "Possible Gastritis", "Allergic Reaction", "Routine Check"). 
It also integrates one public API.




2. Target Audience
- Vet clinic staff (receptionists and veterinarians)
(Pet owners, maybe limited access in future versions?)

Staff needs:
- Easy management of pet owners, pets and appointments
- Quick overview of daily schedule
- Simple tool to assess symptom urgency using Machine Learning
- Automatic weather and parasite risk information




3. Software Requirements Specification (SRS)

Functional Requirements - Staff View

- Secure staff login (with password hashing) :
  - Authentication: passwords not stored as plain text,
  system uses the Werkzeug security library to hash passwords stored in String(128) under class User.

  - Constraints: Unique applied to usernames to prevent double accounts and ensure reliable logins. 

- CRUD operations for Pet Owners (stores full name, unique contact phone, optional email)

- CRUD operations for Pets (includes name, species and breed. Linked via owner_id To Pet owner table)

- CRUD operations for Appointments (stores DateTime object and text based reason for the visit.)

- ML Symptom triage assistant
  - Staff answers 6–8 simple symptom questions
  - System predicts possible condition and urgency level (Low/Medium/High)
- Dashboard with today's appointments
- Public API Integration: OpenWeatherMap API (shows weather + seasonal parasite advice)
- Responsive and clean user interface

Non-Functional Requirements
- Lightweight and easy to run
- Clean, intuitive UI using Bootstrap
- Responsive design
- Secure password handling
- Unit tests for core functions
- Algorithm complexity analysis for the ML model




4. Chosen Technologies
  4.1 Data Architecture:
  - Database: SqLite, Flask-SQLAlchemy

- Backend: Python + Flask
- Frontend: HTML, CSS, JavaScript + Bootstrap 5
- Machine Learning: scikit-learn (Decision Tree / Random Forest)
- Public API: OpenWeatherMap API
- Version Control: Git + GitHub

Development model Scrum