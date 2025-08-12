* [General info])(#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [More detailed information about modules](#more-detailed-information-about-modules)
* [Application view](#application-view)

## General info
<details>
<summary>Click here to see general information about <b>Project</b>!</summary>
<b>WszbiPatientPortal</b> is an appointment management system.
It allows patients to book appointments, doctors to manage their schedules and notes,
and administrators to control the entire system.
The platform supports email notifications and weekly schedule automation via Celery.
</details>

## Tools & Technologies
<ul>
<li>Python</li>
<li>Django</li>
<li>Bootstrap4</li>
<li>PostgreSQL</li>
<li>requests</li>
<li>Celery + Redis</li>
<li>Sentry</li>
<li>unittest</li>
<li>Pre-commit</li>
<li>Docker-Compose & Docker</li>
<li>Poetry</li>
<li>Silk / Django Debug Toolbar</li>
<li>Coverage</li>
</ul>



## Setup
Clone the repo
```bash
git clone https://github.com/your-username/wszbipatientportal.git
cd wszbipatientportal
```
Install poetry
```bash
pip install poetry
```
Install all modules
```bash
poetry install
```
Migrate
```bash
poetry run python manage.py migrate
```
Run application
```bash
poetry run python manage.py runserver
```
To create permission groups
```bash
poetry run python manage.py create_permission_groups
```
To create superuser and generate random 20 doctors with assigned specializations and departments
and generate random 100 patients
```bash
poetry run python manage.py populate_db
```
Run tests
```bash
poetry run python manage.py test
```


## Application features
<ul>
<li>User registration & login (Patient / Doctor / Admin roles)</li>
<li>Browse departments, specializations, and doctors</li>
<li>Book appointments with available doctors</li>
<li>Doctors and patients can add notes to appointments</li>
<li>Doctors can manage their work schedules</li>
<li>searching for products</li>
<li>Old schedules are cleaned up automatically (via Celery Beat)</li>
<li>Role-based permissions using Django Groups</li>
</ul>

## Application View
<ul>
<li>Main</li>
<img src="https://github.com/user-attachments/assets/1003b266-caa3-465f-9800-f657726d3abd" width="50%" height="50%"></img>
<li>Appointments view for doctor</li>
<img src="https://github.com/user-attachments/assets/7e4434d3-aeb0-4799-9b99-4465490eb690" width="50%" height="50%"></img>
<li>Appointments view for patient</li>
<img src="https://github.com/user-attachments/assets/f07ef83d-3609-487a-97f4-1526427fdc46" width="50%" height="50%"></img>
<li>Make appointment view</li>
<img src="https://github.com/user-attachments/assets/fe905724-870c-4940-8c9d-616a4f864842" width="50%" height="50%"></img>
