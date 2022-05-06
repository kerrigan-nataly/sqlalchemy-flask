from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.jobs import Jobs
from forms.user import LoginForm, RegisterForm
from forms.jobs import AddJobForm, EditJobForm

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
    print(current_user.id)
    if current_user.id == 1 or job.team_leader == current_user.id:

        db_sess.query(Jobs).filter(Jobs.id == job_id).delete()
        db_sess.commit()
        return redirect("/")

    return "Доступ запрещен!"



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


if __name__ == '__main__':
    db_session.global_init("db/mars_one.db")
    app.run(port=8080, host='127.0.0.1')