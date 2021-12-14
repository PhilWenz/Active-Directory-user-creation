# Script zum automatisierten Erstellen neuer Benutzer in AD
 Dieses Script erstellt AD-User für die fiktive Fitness-GEEK GmbH
 
 ## Benutzung:
 Aufrufen des Scripts:
* -s für single user
 ```
 python create_user.py -s Name Nachnamen InitPasswort123! Abteilung(Ohne Präfix)
 ```
* -f um eine Textdatei zu laden
 ```
 python create_user.py -f dateipfad/dateiname.txt
 ```