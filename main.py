from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.departments import Department
from forms.user import LoginForm, RegisterForm
from forms.jobs import AddJobForm, EditJobForm
from forms.departments import AddDepartmentForm, EditDepartmentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()

    jobs = db_sess.query(Jobs)

    return render_template('index.html', jobs=jobs, current_user=current_user)


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddJobForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        job = Jobs(
            job=form.job.data,
            team_leader=form.team_leader.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_finished=form.is_finished.data
        )

        db_sess = db_session.create_session()
        db_sess.add(job)
        db_sess.commit()
        return redirect("/")

    return render_template('/jobs/add.html', title='Добавление работы', form=form)


@app.route('/jobs/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):

    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if job.team_leader != current_user.id:
        if current_user.id != 1:
            return "Доступ запрещен!"

    form = EditJobForm(obj=job)

    if form.validate_on_submit():
        db_sess.query(Jobs).filter(Jobs.id == job_id).update({
            Jobs.job: form.job.data,
            Jobs.work_size: form.work_size.data,
            Jobs.team_leader: form.team_leader.data,
            Jobs.collaborators: form.collaborators.data,
            Jobs.start_date: form.start_date.data,
            Jobs.end_date: form.end_date.data,
            Jobs.is_finished: form.is_finished.data
        })
        db_sess.commit()
        return redirect("/")

    return render_template('/jobs/edit.html', title='Редактирование работы', form=form, job_id=job_id)


@app.route('/jobs/<int:job_id>/delete')
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if current_user.id == 1 or job.team_leader == current_user.id:
        db_sess.query(Jobs).filter(Jobs.id == job_id).delete()
        db_sess.commit()
        return redirect("/")

    return "Доступ запрещен!"


@app.route('/departments')
@login_required
def departments_index():
    db_sess = db_session.create_session()
    departments = db_sess.query(Department).all()
    return render_template('/departments/index.html', title='Департаменты', departments=departments)


@app.route('/departments/add', methods=['GET', 'POST'])
@login_required
def departments_add():
    form = AddDepartmentForm()
    if form.validate_on_submit():
        department = Department(
            title=form.title.data,
            chief_id=form.chief_id.data,
            members=form.members.data,
            email=form.email.data
        )

        db_sess = db_session.create_session()
        db_sess.add(department)
        db_sess.commit()
        return redirect("/departments")

    return render_template('/departments/add.html', title='Добавление департамента', form=form)


@app.route('/departments/<int:dep_id>/delete')
@login_required
def departments_delete(dep_id):
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).get(dep_id)
    if current_user.id == 1 or dep.chief_id == current_user.id:
        db_sess.query(Department).filter(Department.id == dep_id).delete()
        db_sess.commit()
        return redirect("/departments")

    return "Доступ запрещен!"


@app.route('/departments/<int:dep_id>', methods=['GET', 'POST'])
@login_required
def departments_edit(dep_id):

    db_sess = db_session.create_session()
    dep = db_sess.query(Department).get(dep_id)
    if dep.chief_id != current_user.id:
        if current_user.id != 1:
            return "Доступ запрещен!"

    form = EditDepartmentForm(obj=dep)

    if form.validate_on_submit():
        db_sess.query(Department).filter(Department.id == dep_id).update({
            Department.title: form.title.data,
            Department.email: form.email.data,
            Department.chief_id: form.chief_id.data,
            Department.members: form.members.data
        })
        db_sess.commit()
        return redirect("/departments")

    return render_template('/departments/edit.html', title='Редактирование департамента', form=form, dep_id=dep_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def prep_db(session):
    cap = User()
    cap.surname = "Scott"
    cap.name = "Ridley"
    cap.age = 21
    cap.position = "captain"
    cap.speciality = "research engineer"
    cap.address = "module_1"
    cap.email = "cap@mars.org"
    cap.set_password('test')

    nav = User()
    nav.surname = "Watny"
    nav.name = "Mark"
    nav.age = 25
    nav.position = "rover navigator"
    nav.speciality = "navigator"
    nav.address = "module_1"
    nav.email = "mark_wanty@mars.org"

    astro1 = User()
    astro1.surname = "Weir"
    astro1.name = "Andy"
    astro1.age = 49
    astro1.position = "scientist"
    astro1.speciality = "climatologist"
    astro1.address = "module_2"
    astro1.email = "andy_weir@mars.org"

    astro2 = User()
    astro2.surname = "Sanders"
    astro2.name = "Teddy"
    astro2.age = 41
    astro2.position = "NASA director"
    astro2.speciality = "tourist"
    astro2.address = "module_2"
    astro2.email = "teddy_sanders@mars.org"

    astro3 = User()
    astro3.surname = "Sigourney"
    astro3.name = "Weaver"
    astro3.age = 30
    astro3.position = "Secondary pilot"
    astro3.speciality = "warrant officer"
    astro3.address = "module_2"
    astro3.email = "weaver_sigourney@mars.org"

    astro4 = User()
    astro4.surname = "House"
    astro4.name = "Gregory"
    astro4.age = 49
    astro4.position = "chief medical officer"
    astro4.speciality = "therapist"
    astro4.address = "module_3"
    astro4.email = "house_gregory@mars.org"

    session.add(cap)
    session.add(nav)
    session.add(astro1)
    session.add(astro2)
    session.add(astro3)
    session.add(astro4)
    session.commit()

    job = Jobs()
    job.team_leader = cap.id
    job.job = 'deployment of residential modules 1 and 2'
    job.work_size = 15
    job.collaborators = '2, 3'
    job.is_finished = False

    exploration = Jobs()
    exploration.team_leader = astro1.id
    exploration.job = 'Exploration of mineral resources'
    exploration.work_size = 15
    exploration.collaborators = '4, 3'
    exploration.is_finished = True

    development = Jobs()
    development.team_leader = astro2.id
    development.job = 'Development of a managment system'
    development.work_size = 5
    development.collaborators = '5'
    development.is_finished = False

    development = Jobs()
    development.team_leader = astro4.id
    development.job = 'Warehouse organization'
    development.work_size = 7
    development.collaborators = '3, 4'
    development.is_finished = False

    air = Jobs()
    air.team_leader = astro4.id
    air.job = 'analysis of atmospheric air samples'
    air.work_size = 5
    air.collaborators = '3, 5, 4'
    air.is_finished = False

    maintenance = Jobs()
    maintenance.team_leader = astro4.id
    maintenance.job = 'Mars Rover maintenance'
    maintenance.work_size = 10
    maintenance.collaborators = '1, 4'
    maintenance.is_finished = False

    session.add(job)
    session.add(maintenance)
    session.add(air)
    session.add(exploration)
    session.add(development)

    dep = Department()
    dep.email = 'geological_exploration@mars.org'
    dep.title = 'Департамент геологической разведки'
    dep.members = '2, 4'
    dep.chief_id = 1

    dep2 = Department()
    dep2.email = 'technical_support@mars.org'
    dep2.title = 'Департамент технического обеспечения'
    dep2.members = '3, 5'
    dep2.chief_id = 6

    session.add(dep)
    session.add(dep2)

    session.commit()


if __name__ == '__main__':
    db_session.global_init("db/mars_project.db")
    session = db_session.create_session()
    users = session.query(User).all()
    if not users:
        prep_db(session)

    app.run(port=8080, host='127.0.0.1')