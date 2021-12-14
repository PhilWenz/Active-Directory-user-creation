import sys, os
from pyad import pyad, aduser, adcontainer
from pyad.pyadexceptions import win32Exception
from pywintypes import com_error

# Domain Controller (DC)
controller='GEEK-DC-1'

def replace_umlauts(name):
    name = name.replace('ö','oe')
    name = name.replace('ü','ue')
    name = name.replace('ä', 'ae')
    name = name.replace('ß', 'ss')
    return name

# login name wird aus den ersten (maximal) 4 Zeichen des Nachnamen und den ersten 2 des Nachnamen zusammengesetzt
def generate_login_name(name):
    name = replace_umlauts(name)
    first_name, last_name = name.split()
    if(len(last_name) < 4):
        prefix = last_name
    else:
        prefix = last_name[0 : 4]
    login_name = prefix + first_name[0 : 2]
    return login_name.lower()

def load_user(name):
    user = pyad.aduser.ADUser.from_cn(name)
    return user

# this is where the magic happens
def create_user(name, pw, group):
    ou = pyad.adcontainer.ADContainer.from_dn("OU={},OU={},OU={},DC=geek,DC=local".format(group, "Benutzer", "GEEK-Fitness"))
    login_name = generate_login_name(name)
    profile_dir = '\\\\{}\\Profile$\\{}'.format(controller, login_name)
    home_dir = '\\\\{}\\Homes$\\{}'.format(controller, login_name)
    # Home Directory auf dem Fileserver erstellen
    try:
        os.mkdir(home_dir)
    except OSError:
        print("FEHLER: Das Home Verzeichnis {} konnte nicht angelegt werden.".format(home_dir))
    # Benutzer anlegen
    pyad.aduser.ADUser.create(name, ou, password=pw, enable=True, optional_attributes={
        'pwdLastSet' : 0,
        'sAMAccountName' : login_name, 
        'profilePath' : profile_dir,
        'homeDrive' : "H:",
        'homeDirectory' : home_dir
    })

def main(name, passwd, group):
    # Zum Anlegen des Benutzers wird er in der nach der Abteilung/Gruppe benannten OU abgelegt.
    # Die OUs haben den Präfix Ben_
    ou = "Ben_" + group
    create_user(name, passwd, ou)

    try:
        create_user(name, passwd, ou)
    except win32Exception:
        print("Der Benutzer konnte nicht angelegt werden, da entweder bereits existiert, oder bereits ein Benutzer mit dem selben Anmeldenamen existiert.")
        exit(1)
    except com_error:
         print("Die angegebene Gruppe oder Organisationseinheit existiert nicht.")
         exit(1)

    u = load_user(name)
    # Die Sicherheitsgruppen haben den Präfix Grp_
    group = "Grp_" + group
    g = pyad.adgroup.ADGroup.from_dn("CN={},OU={},OU={},DC=geek,DC=local".format(group, "Gruppen", "GEEK-Fitness"))
    #print("ADDING:\n{}\nTO:\n{}".format(u,g) )
    u.add_to_group(g)

def load_from_file(filepath):
    file = open(filepath)
    for line in file:
        first_name, last_name, password, group = line.split()
        name = "{} {}".format(first_name, last_name)
        main(name, password, group)


if(__name__ == '__main__'):
    args = sys.argv
    if(len(sys.argv) > 1):
        print(args)
        if(args[1] == '-s'):
            fn = args[2]
            ln = args[3]
            pw = args[4]
            grp = args[5]
            main(fn + " " + ln, pw, grp)
        elif(args[1] == '-f'):
            load_from_file(args[2])
    else:
        print("Dieses Tool benötigt weitere Parameter um ausgeführt zu werden.")
        print("Bitte rufen Sie das Tool wie folgt aus um einen Benutzer anzulegen:")
        print("python ./create_user -s Vorname Nachname Initialisierungspasswort Benutzergruppe (Ohne Präfix)")
        print("Oder laden Sie eine Textdatei in der Zeilenweise mehrere Benutzerdaten angelegt sind:")
        print("python ./crate_user -f dateipfad/dateiname.txt")