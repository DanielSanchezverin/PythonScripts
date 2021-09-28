#!/usr/bin/env python3

import subprocess

prueba = subprocess.check_output("df /mnt/ | awk 'NR==2 { print $5 }' | grep -o '^.'", shell=True)
prueba = str(prueba)

def rmCharacters(string):
    characters = "b'\\n"
    for i in range(len(characters)):
        string = string.replace(characters[i],"")
    return string

prueba = rmCharacters(prueba)

if int(prueba) <= 95:
    date = subprocess.check_output("date +%d-%m-%Y-%T", shell=True)
    date = str(date)
    date = rmCharacters(date)
    subprocess.run("sudo tar --exclude='.ssh' --exclude='.aws' -cvpzf /mnt/" + date + "-fullbackup.tar.gz /home/*", shell=True)
    subprocess.run("sudo tar -cvpzf /mnt/" + date + "-logbackup.tar.gz /var/log/", shell=True)
    print("Backup created succesfully")
    subprocess.run("aws s3 sync /mnt s3://bucket/Backups --delete", shell=True)
    subprocess.run("echo -e \"Subject: Backup:Succesfully\n\nBackup (" + date + ") created succesfully\" | sendmail mail@mail.com", shell=True)
    print("Email sent")
else:
    print("Not enough space to backup")
    subprocess.run("echo -e \"Subject: Backup:Error\n\nBackup (" + date + ") cannot be created. Not enough space to backup\" | sendmail mail@mail.com" , shell=True)