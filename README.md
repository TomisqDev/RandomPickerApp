Lucky Wheel Generator

My first serious project!
Simple web app for creating random wheels (wheel of fortune).


Features:
- User registration & login (bcrypt hashed)
- Create custom "wheels"
- Add items to wheels
- Animated random winner picker
- Responsive dark design
- MySQL database


Start

# 1. Install dependencies
pip install flask mysql-connector-python python-dotenv bcrypt

# 2. Create the database
run the database_script.sql in mysql workbench

# 3. Create .env file
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=lucky_wheel

# 4. Run
python app.py
Open http://localhost:5000


About Me

This is my first serious project.
I'm just trying to improve in programming more and more. I already know how to code a bit.

Future Plans
- Deploy to public
- Google/GitHub OAuth login
- Share wheels between users
- Mobile PWA app
