import json


def save_drives(drives):
    with open('drives.json', 'w') as file:
        json.dump(drives, file)


def load_drives():
    try:
        with open('drives.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_jobs(jobs):
    with open('jobs.json', 'w') as file:
        json.dump(jobs, file)


def load_jobs():
    try:
        with open('jobs.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_rclone_config(rcloneConfig):
    with open('rclone_config.json', 'w') as file:
        json.dump(rcloneConfig, file)


def load_rclone_config():
    try:
        with open('rclone_config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'rclone_path': ''}
