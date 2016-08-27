from flask_script import Manager, Server, prompt_bool
import memesocial


manager = Manager(memesocial.app)
manager.add_command("runserver", Server(host="0.0.0.0", port=1337))


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


if __name__ == "__main__":
    manager.run()
