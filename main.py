from data.database import init_db
from interface.main_ui import launch_ui

def main():
    init_db()
    launch_ui()

if __name__ == "__main__":
    main()
