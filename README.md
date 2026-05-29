# vetcare-lite

Vienkārša veterinārās klīnikas vadības sistēma, izstrādāta ar Python un Flask.

Šis projekts tika veidots kā 12. klases programmēšanas projekta darbs, vairāk pievēršoties backend loģikai, datu bāzēm, autentifikācijai un piekļuves kontrolei, nevis frontend dizainam.

Projektā netiek izmantoti HTML template faili — HTML saturs tiek renderēts Flask maršrutos, lai saglabātu vienkāršāku backend orientētu struktūru.

---

# Funkcionalitāte

- Lietotāju reģistrācija un login sistēma
- Session-based autentifikācija
- Jaunu lietotāju apstiprināšanas sistēma
- Administratora panelis lietotāju pārvaldībai
- Klientu un mājdzīvnieku pārvaldība
- Veterināro vizīšu rezervēšana
- Meklēšana pēc klienta vārda vai telefona numura
- Laikapstākļu API integrācija veterinārajiem ieteikumiem
- Paroļu hashēšana ar Werkzeug
- Paroles redzamības funkcija
- Dzēšanas apstiprinājuma logi

---

# Izmantotās tehnoloģijas

- Python
- Flask
- SQLite
- SQLAlchemy
- Requests
- Werkzeug
- Open-Meteo API

---

# Projekta palaišana


git clone https://github.com/elizacif/vetcare-lite.git
cd vetcare-lite

Install nepieciešamās bibliotēkas:

pip install flask flask_sqlalchemy requests werkzeug


Palaist projektu:

python app.py

Tad atvērt pārlūkprogrammā:

http://127.0.0.1:5000

---

# Admin sistēma

Jauni lietotāji pēc reģistrācijas automātiski tiek atzīmēti kā “pending”.

Tikai administrators var:

- apstiprināt lietotājus;
- rediģēt lietotājus;
- dzēst lietotājus;
- pārvaldīt piekļuvi sistēmai.

---

# Piezīmes

Projekts veidots galvenokārt mācību nolūkiem, lai paplašinātu savas zināšanas un prasmi pielietot teoriju praksē.

Sistēma tika testēta lokāli, izmantojot Flask development serveri.

---

# Autors

Elīza Sofija
12. klases programmēšanas projekta darbs
