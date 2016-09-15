from flask_script import Manager, Server, prompt_bool
import memesocial

memesocial.init('memesocial.config.devConfig')

from memesocial import app

manager = Manager(app)
manager.add_command("runserver", Server(
    host="0.0.0.0", port=1337, threaded=True))


@manager.command
def createdb():
    memesocial.db.create_tables(
        memesocial.all_tables
    )


@manager.command
def dropdb():
    if prompt_bool("Are you sure you wanna drop the database ?"):
        memesocial.db.drop_tables(
            memesocial.all_tables
        )


@manager.command
def recreatedb():
    dropdb()
    createdb()


@manager.command
def autopep8():
    # only works in Unix
    import commands
    print commands.getoutput('autopep8 memesocial --recursive --in-place --pep8-passes 2000 --verbose')


@manager.command
def pep8():
    import commands
    print commands.getoutput('pep8 memesocial')


if __name__ == "__main__":
    manager.run()
