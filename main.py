from flask import Flask, render_template, request, redirect, url_for,g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cx_Oracle
import bcrypt
import re
from datetime import date, datetime

app = Flask(__name__)
# Replace 'sys' and 'admin' with your actual sysdba username and password
connection_str = cx_Oracle.makedsn('bd-dc.cs.tuiasi.ro', 1539, service_name='orcl')
conn = cx_Oracle.connect('bd110', 'parvanavlad123', connection_str)
app.config['SECRET_KEY'] = '2023proiectbd2024'
login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, user_id, email, is_admin):
        self.id = user_id
        self.email = email
        self.is_admin = is_admin

def contains_digits(input_str):
    return bool(re.search(r'\d', input_str))

def contains_letters(sir):
    pattern = re.compile(r'^\d+(\.\d+)?$')
    match = pattern.match(sir)
    return bool(match)

def este_pret_bilet(input_str):
    pattern = re.compile(r'^\d*(\.\d{1,2})?$')
    match = pattern.match(input_str)
    return bool(match)

def user_exists(email):
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM UTILIZATORI WHERE EMAIL = :email", email=email)
    return cursor.fetchone() is not None

def add_user(nume, prenume, dataNastere, email, parola):
    salt = bcrypt.gensalt()
    parola_criptata = bcrypt.hashpw(parola.encode('utf-8'), salt)
    cursor = conn.cursor()
    # Schimbarea liniei pentru adăugarea utilizatorului
    cursor.execute("""
        INSERT INTO UTILIZATORI (NUME, PRENUME, DATANASTERE, EMAIL, PAROLA, ADMIN, SAREA) 
        VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5, 'NU', :6)
        """, (nume, prenume, dataNastere, email, parola_criptata.decode('utf-8'), salt.decode('utf-8')))
    conn.commit()

def get_user_by_email(email):
    cursor = conn.cursor()
    cursor.execute("SELECT USERID, EMAIL, PAROLA, ADMIN, SAREA FROM UTILIZATORI WHERE EMAIL = :email", email=email)
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        # Schimbarea liniei pentru citirea utilizatorului
        user = {
            'id': user_data[0],
            'email': user_data[1],
            'parola': user_data[2].encode('utf-8'),  # Utilizați direct hash-ul stocat în baza de date
            'admin': user_data[3],
            'salt': user_data[4].encode('utf-8')
        }

        #print("Debug - User data:", user)

        return user
    return None

@login_manager.user_loader
def load_user(user_id):
    # Funcție pentru Flask-Login care încarcă un utilizator în funcție de id
    cursor = conn.cursor()
    cursor.execute("SELECT USERID, EMAIL, ADMIN FROM UTILIZATORI WHERE USERID = :id", id=user_id)
    user_data = cursor.fetchone()
    cursor.close()

    if user_data:
        return User(user_data[0], user_data[1], user_data[2] == 'DA')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        parola = request.form['parola']

        user = get_user_by_email(email)


        #print("Debug - Before concatenation - Parola:", parola)
        #print("Debug - Before concatenation - Salt:", user['salt'])
        #print(bcrypt.hashpw(parola.encode('utf-8'), user['salt'].encode('utf-8')))

        if user and bcrypt.checkpw(parola.encode('utf-8'), user['parola']):
            login_user(User(user['id'], user['email'], user['admin'] == 'DA'))
            return render_template('mesaj.html', title="Felicitari", message="Te-ai conectat la contul tau!",
                                   tipActiune="Acasa", redirectLink=url_for('dashboard'))
        else:
            return render_template('mesaj.html', title="Ne pare rau",
                                   message="Contul nu exista sau parola este incorectă.", tipActiune="Acasa",
                                   redirectLink="/")

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('zboruri_admin'))
    else:
        return redirect(url_for('zboruri_user'))


@app.route('/zboruri_admin')
@login_required
def zboruri_admin():
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Zboruri order by ZBORID")
        zbor_data = cursor.fetchall()
        cursor.close()
        return render_template('zboruri_admin.html', zbor_data=zbor_data)
    else:
        return redirect(url_for('index'))

@app.route('/new_zbor', methods=['GET', 'POST'])
@login_required
def new_zbor():
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT ORASPLECARE, ORASDESTINATIE, RUTAID FROM RUTE")
        rute_data = cursor.fetchall()
        if request.method == 'POST':
            bagajCala=request.form['BagajCala']
            locuriDisponibile=request.form['LocuriDisponibile']
            rutaId=request.form['Ruta']
            dataPlecare=request.form['DataPlecare']
            pretBilet=request.form['PretBilet']
            if datetime.strptime(dataPlecare, '%Y-%m-%d').date() < date.today():
                cursor.close()
                return render_template('mesaj.html', title="Eroare",
                                       message="Nu poti adauga un zbor cu o data din trecut",
                                       tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_admin'))
            if este_pret_bilet(pretBilet) and int(locuriDisponibile) > 0:
                cursor.execute("SELECT * FROM ZBORURI WHERE RUTAID = :rutaId and dataPlecare = TO_DATE(:dataPlecare, 'YYYY-MM-DD')", rutaId=rutaId, dataPlecare=dataPlecare)
                if cursor.fetchone() is None:
                    try:
                        cursor.execute("""
                                INSERT INTO ZBORURI (RutaID, DataPlecare, LocuriDisponibile, PretBilet, BagajCala) 
                                VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5)
                                """, (rutaId, dataPlecare, locuriDisponibile, pretBilet,bagajCala ))
                        cursor.execute("SELECT zboruri_seq.CURRVAL FROM dual")
                        zbor_id = cursor.fetchone()[0]
                        for i in range(1, int(locuriDisponibile) + 1):
                            cursor.execute("""
                                    INSERT INTO BILETE (BiletID, ZborID,LOC) 
                                    VALUES (:1, :2, :3)
                                    """, (i, zbor_id , i ))
                        if bagajCala == 'DA':
                            return redirect(url_for('new_bagajcala',zbor_id=zbor_id))
                        conn.commit()
                        cursor.close()
                        return render_template('mesaj.html', title="Succes",
                                               message="Zborul a fost adaugat in baza de date.",
                                               tipActiune="Acasa",
                                               redirectLink=url_for('zboruri_admin'))
                    except Exception:
                        conn.rollback()
                        return render_template('mesaj.html', title="Eroare",
                                               message="Campurile nu au fost completate corect.", tipActiune="Acasa",
                                               redirectLink=url_for('zboruri_admin'))

                else:
                    cursor.close();
                    return render_template('mesaj.html', title="Eroare",
                                           message="Exista deja un zbor cu aceeasi ruta si data de plecare.", tipActiune="Acasa",
                                           redirectLink=url_for('zboruri_admin'))
            else:
                return render_template('mesaj.html', title="Eroare",
                                       message="Pretul trebuie sa fie numar zecimal si numarul locurilor trebuie sa fie numar natural pozitiv.", tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_admin'))
        return render_template('new_zbor.html',rute_data=rute_data)
    else:
        cursor.close()
        return redirect(url_for('index'))


@app.route('/new_bagajcala/<int:zbor_id>', methods=['GET', 'POST'])
@login_required
def new_bagajcala(zbor_id):
    if current_user.is_admin:
        if request.method == 'POST':
            greutateBagaj=request.form['GreutateBagaj']
            greutateMaxima=request.form['GreutateMaxima']
            pretBagaj=request.form['PretBagaj']
            dimensiuni=request.form['Dimensiuni']
            if este_pret_bilet(pretBagaj) and int(greutateMaxima)>=int(greutateBagaj):
                try:
                    cursor=conn.cursor()
                    cursor.execute("""INSERT INTO DETALIIBAGAJCALA ( ZborID, GreutateBagaj, GreutateMaxima, Dimensiuni,PretBagaj) 
                                                VALUES (:1, :2, :3, :4, :5)
                                                """, (zbor_id, greutateBagaj, greutateMaxima, dimensiuni, pretBagaj))
                    conn.commit();
                    return render_template('mesaj.html', title="Succes",
                                           message="Zborul a fost adaugat in baza de date.",
                                           tipActiune="Acasa",
                                           redirectLink=url_for('zboruri_admin'))
                except Exception:
                    conn.rollback()
                    return render_template('mesaj.html', title="Eroare",
                                           message="Campurile nu au fost completate corect.", tipActiune="Acasa",
                                           redirectLink=url_for('zboruri_admin'))


            else:
                conn.rollback()
                return render_template('mesaj.html', title="Eroare",
                                       message="Pretul trebuie sa fie numar zecimal,iar greutatea maxima trebuie sa fie mai mare decat greutatea bagajului", tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_admin'))

        return render_template('new_bagajcala.html',zbor_id=zbor_id)
    else:
        return redirect(url_for('index'))
@app.route('/display_zbor/<int:zbor_id>', methods=['GET', 'POST'])
@login_required
def display_zbor(zbor_id):
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ZBoruri WHERE ZborID = :zbor_id", zbor_id=zbor_id)
        zbor_data = cursor.fetchone()
        cursor.execute("SELECT LOC, USERID ,STARE, CASE WHEN USERID IS NULL THEN NULL ELSE DATACUMPARARE END, BAGAJCALA FROM Bilete WHERE ZborID = :zbor_id order by BiletID", zbor_id=zbor_id)
        bilete_data = cursor.fetchall()
        cursor.execute(
            "SELECT GREUTATEBAGAJ, GREUTATEMAXIMA, PRETBAGAJ,DIMENSIUNI FROM DETALIIBAGAJCALA WHERE ZborID = :zbor_id ",zbor_id=zbor_id)
        bagajcalainfo =cursor.fetchone()
        if request.method == 'POST':
            cursor.execute("SELECT count(*) FROM BILETE WHERE ZborID = :zbor_id and STARE = 'Cumparat'", zbor_id=zbor_id)
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM BILETE WHERE ZborID = :zbor_id",zbor_id=zbor_id)
                cursor.execute("DELETE FROM DETALIIBAGAJCALA WHERE ZborID = :zbor_id",zbor_id=zbor_id)
                cursor.execute("DELETE FROM Zboruri WHERE ZborID = :zbor_id", zbor_id=zbor_id)
                conn.commit()
                cursor.close()
                return render_template('mesaj.html', title="Succes",
                                       message="Zborul a fost sters.", tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_admin'))
            else:
                return render_template('mesaj.html', title="Eroare",
                                       message="Zborul are bilete cumparate.", tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_admin'))

        cursor.close()
        if zbor_data:
            return render_template('display_zbor.html', zbor_data=zbor_data,bilete_data=bilete_data,bagajcalainfo=bagajcalainfo)
        else:
            return render_template('mesaj.html', title="Eroare",
                                   message="Zborul nu există.", tipActiune="Acasa",
                                   redirectLink=url_for('zboruri_admin'))
    return redirect(url_for('index'))


@app.route('/modify_zbor/<int:zbor_id>', methods=['GET', 'POST'])
@login_required
def modify_zbor(zbor_id):
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ZBoruri WHERE ZborID = :zbor_id", zbor_id=zbor_id)
        zbor_data = cursor.fetchone()
        if request.method == 'POST':
            try:
                newPretBilet = request.form['PretBilet']
                cursor.execute("UPDATE Zboruri SET PRETBILET = :pretBilet WHERE ZBORID = :zbor_id", pretBilet= newPretBilet, zbor_id=zbor_id )
                conn.commit()
                cursor.close()
                return render_template('mesaj.html', title="Succes",
                                       message="Zborul a fost modificat.", tipActiune="Acasa",
                                       redirectLink=url_for('display_zbor',zbor_id=zbor_data[0]))
            except Exception as e:
                conn.rollback()
                return render_template('mesaj.html', title="Eroare",
                                       message="Campurile nu au fost completate corect.", tipActiune="Acasa",
                                       redirectLink=url_for('display_zbor', zbor_id=zbor_data[0]))


        cursor.close()
        if zbor_data:
            return render_template('modify_zbor.html', zbor_data=zbor_data)
        else:
            return render_template('mesaj.html', title="Eroare",
                                   message="Zborul nu există.", tipActiune="Acasa",
                                   redirectLink=url_for('zboruri_admin'))
    return redirect(url_for('index'))
@app.route('/zboruri_user', methods=['GET', 'POST'])
@login_required
def zboruri_user():
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT ORASPLECARE, ORASDESTINATIE, RUTAID FROM RUTE")
        rute_data = cursor.fetchall()
        if request.method == 'POST':
            dataPlecare = request.form['dataPlecare']
            rutaId = request.form['Ruta']
            if datetime.strptime(dataPlecare, '%Y-%m-%d').date() < date.today():
                cursor.close()
                return render_template('mesaj.html', title="Eroare",
                                       message="Nu poti cauta zboruri din trecut.",
                                       tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_user'))
            cursor.execute("SELECT ZBORID FROM ZBORURI WHERE DATAPLECARE = TO_DATE(:dataPlecare, 'YYYY-MM-DD') and RUTAID = :rutaId",dataPlecare=dataPlecare, rutaId=rutaId)
            zbor_id = cursor.fetchone()
            if zbor_id:
                zbor_id=zbor_id[0];
                return redirect(url_for('display_zbor_user',zbor_id=zbor_id))
            else:
                return render_template('mesaj.html', title="Eroare",
                                       message="Nu exista nici un zbor inregistrat la data sau ruta aceasta.", tipActiune="Acasa",
                                       redirectLink=url_for('zboruri_user'))
        return render_template('zboruri_user.html',rute_data=rute_data)
    else:
        return redirect(url_for('index'))

@app.route('/display_zbor_user/<int:zbor_id>', methods=['GET', 'POST'])
@login_required
def display_zbor_user(zbor_id):
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ZBORURI WHERE ZBORID = :zbor_id",zbor_id=zbor_id)
        zbor_data = cursor.fetchone()
        cursor.execute(
            "SELECT GREUTATEBAGAJ, GREUTATEMAXIMA, PRETBAGAJ,DIMENSIUNI FROM DETALIIBAGAJCALA WHERE ZborID = :zbor_id ",
            zbor_id=zbor_id)
        bagajcalainfo = cursor.fetchone()
        cursor.execute(
            "SELECT LOC, USERID ,STARE, CASE WHEN USERID IS NULL THEN NULL ELSE DATACUMPARARE END, BAGAJCALA FROM Bilete WHERE ZborID = :zbor_id AND STARE = 'Valabil' order by BiletID",
            zbor_id=zbor_id)
        bilete_data = cursor.fetchall()
        cursor.close()
        return render_template('display_zbor_user.html', zbor_data=zbor_data,bagajcalainfo=bagajcalainfo,bilete_data=bilete_data)
    return redirect(url_for('index'))

@app.route('/zboruri_viitoare', methods=['GET', 'POST'])
@login_required
def zboruri_viitoare():
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Zboruri WHERE DATAPLECARE >= TRUNC(CURRENT_DATE)  order by ZBORID" )
        zbor_data = cursor.fetchall()
        cursor.close()
        return render_template('zboruri_viitoare.html',zbor_data=zbor_data)
    return redirect(url_for('index'))


@app.route('/contul_meu', methods=['GET', 'POST'])
@login_required
def contul_meu():
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilizatori WHERE USERID = :user_id", user_id=current_user.id)
        user_data = cursor.fetchone()
        return render_template('contul_meu.html',user_data=user_data)
    return redirect(url_for('index'))

@app.route('/modificare_informatii', methods=['GET', 'POST'])
@login_required
def modificare_informatii():
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilizatori WHERE USERID = :user_id", user_id=current_user.id)
        user_data = cursor.fetchone()
        if request.method == 'POST':
            nume= request.form['nume']
            prenume = request.form['prenume']
            email = request.form['email']
            if not contains_digits(nume) and not contains_digits(prenume):
                cursor.execute("SELECT * FROM Utilizatori WHERE EMAIL=: email AND USERID <> :user_id",email=email, user_id=current_user.id)
                if cursor.fetchone() is None:
                    cursor.execute("UPDATE Utilizatori SET NUME= :nume, PRENUME = :prenume, EMAIL = :email WHERE USERID =: user_id",nume=nume,prenume=prenume,email=email,user_id=current_user.id)
                    conn.commit()
                    cursor.close
                    return redirect(url_for('contul_meu'))
                else:
                    return render_template('mesaj.html', title="Eroare",
                                           message="Exista deja un cont pe acest email.",
                                           tipActiune="Acasa",
                                           redirectLink=url_for('contul_meu'))
            else:
                return render_template('mesaj.html', title="Eroare",
                                       message="Numele si prenumele nu pot contine cifre.",
                                       tipActiune="Acasa",
                                       redirectLink=url_for('contul_meu'))

        cursor.close()
        return render_template('modificare_informatii.html',user_data=user_data)
    return redirect(url_for('index'))

@app.route('/buy_bilet/<int:zbor_id>/<int:bilet_id>', methods=['GET', 'POST'])
@login_required
def buy_bilet(zbor_id,bilet_id):
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT PretBilet FROM ZBORURI WHERE ZBORID =: zbor_id",zbor_id=zbor_id)
        pretBilet=cursor.fetchone()[0]
        cursor.execute("SELECT PretBagaj FROM DETALIIBAGAJCALA WHERE ZBORID =: zbor_id", zbor_id=zbor_id)
        pretBagaj = cursor.fetchone()
        if pretBagaj is None:
            pretBagaj = 0
        else:
            pretBagaj =pretBagaj[0];
        #print(pretBagaj)
        if request.method == 'POST':
            try:
                bagaj_cala = request.form.get('bagajCala')
                newPretBilet = pretBilet
                bc= 'NU'
                if bagaj_cala == 'on' :
                    newPretBilet=newPretBilet+pretBagaj
                    bc = 'DA'
                cursor.execute("UPDATE ZBORURI SET LOCURIDISPONIBILE= LOCURIDISPONIBILE -1 WHERE ZBORID =:zbor_id", zbor_id=zbor_id)
                print(newPretBilet)
                cursor.execute("UPDATE Bilete SET PretBilet= :newPretBilet , DataCumparare= TRUNC(CURRENT_DATE) "
                               ", STARE = 'Cumparat', USERID = :user_id, BAGAJCALA = :bagaj_cala WHERE ZBORID = :zbor_id AND BILETID= :bilet_id",newPretBilet=newPretBilet,
                               user_id= current_user.id , bagaj_cala=bc,zbor_id=zbor_id,bilet_id=bilet_id)
                if bc == 'DA':
                    try:
                        cursor.execute("UPDATE DETALIIBAGAJCALA SET GREUTATEMAXIMA = GREUTATEMAXIMA - GREUTATEBAGAJ WHERE ZBORID= :zbor_id",zbor_id=zbor_id)
                    except Exception:
                        conn.rollback()
                        return render_template('mesaj.html', title="Eroare",
                                               message="A fost atinsa cantitatea maxima de bagaje de cala", tipActiune="Acasa",
                                               redirectLink=url_for('display_zbor_user', zbor_id=zbor_id))
                conn.commit()
                cursor.close()
                return render_template('mesaj.html', title="Succes",
                                       message="Biletul a fost cumparat", tipActiune="Acasa",
                                       redirectLink=url_for('display_zbor_user', zbor_id=zbor_id))

            except KeyError:
                print("Cheia 'bagajCala' nu a fost găsită în formular.")
        return render_template('buy_bilet.html',zbor_id=zbor_id,bilet_id=bilet_id,pretBilet=pretBilet,pretBagaj=pretBagaj)
    return redirect(url_for('index'))


@app.route('/bilete', methods=['GET', 'POST'])
@login_required
def bilete():
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT BILETE.ZBORID, BILETE.BILETID, BILETE.PRETBILET, BILETE.BAGAJCALA, BILETE.DATACUMPARARE,
            RUTE.ORASPLECARE, RUTE.ORASDESTINATIE, ZBORURI.DATAPLECARE
            FROM BILETE
            JOIN ZBORURI ON BILETE.ZBORID = ZBORURI.ZBORID
            JOIN RUTE ON ZBORURI.RUTAID = RUTE.RUTAID
            WHERE USERID = :user_id
            ORDER BY DATACUMPARARE DESC
        """, user_id=current_user.id)
        bilete_data = cursor.fetchall()
        cursor.close()
        return render_template('bilete.html',bilete_data=bilete_data)
    return redirect(url_for('index'))

@app.route('/cancel_bilet/<int:zbor_id>/<int:bilet_id>', methods=['GET', 'POST'])
@login_required
def cancel_bilet(zbor_id,bilet_id):
    if not current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ZBORURI WHERE DATAPLECARE>= TRUNC(CURRENT_DATE) AND ZBORID= :zbor_id",zbor_id=zbor_id )
        if cursor.fetchone() is None:
            return render_template('mesaj.html', title="Ne pare rau",
                                   message="Biletul nu se poate anula deoarece zborul a avut deja loc.", tipActiune="Acasa",
                                   redirectLink=url_for('bilete'))
        else:
            cursor.execute("SELECT BAGAJCALA FROM BILETE WHERE ZBORID = :zbor_id AND BILETID = :bilet_id",zbor_id=zbor_id, bilet_id=bilet_id)
            bc= cursor.fetchone()
            cursor.execute("UPDATE BILETE SET USERID = null , DATACUMPARARE = CURRENT_DATE,"
                           " PRETBILET= null ,BAGAJCALA = 'NU', STARE = 'Valabil' "
                           "WHERE ZBORID = :zbor_id AND BILETID = :bilet_id",zbor_id=zbor_id, bilet_id=bilet_id)
            cursor.execute("UPDATE ZBORURI SET LOCURIDISPONIBILE= LOCURIDISPONIBILE +1 WHERE ZBORID =:zbor_id",
                           zbor_id=zbor_id)
            if bc is not None:
                if bc[0] == 'DA':
                    cursor.execute("UPDATE DETALIIBAGAJCALA SET GREUTATEMAXIMA=GREUTATEMAXIMA+GREUTATEBAGAJ")
            conn.commit()
            cursor.close();
            return render_template('mesaj.html', title="Succes",
                                   message="Biletul a fost anulat,",
                                   tipActiune="Acasa",
                                   redirectLink=url_for('bilete',))

    return redirect(url_for('index'))


@app.route('/rute')
@login_required
def rute():
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RUTE order by RUTAID")
        rute_data = cursor.fetchall()
        cursor.close()
        return render_template('rute.html', rute_data=rute_data)
    return redirect(url_for('index'))

@app.route('/new_ruta', methods=['GET', 'POST'])
@login_required
def new_ruta():
    if current_user.is_admin:
        if request.method == 'POST':
            orasPlecare = request.form['OrasPlecare']
            orasDestinatie = request.form['OrasDestinatie']
            distanta = request.form['Distanta']
            durataEstimata = request.form['DurataEstimata']
            if contains_digits(orasPlecare) or contains_digits(orasDestinatie):
                return render_template('mesaj.html', title="Eroare",
                                       message="Orasele nu pot contine cifre in denumire.", tipActiune="Acasa",
                                       redirectLink=url_for('rute'))
            if not contains_letters(durataEstimata):
                return render_template('mesaj.html', title="Eroare",
                                       message="Durata estimata trebuie sa fie numar", tipActiune="Acasa",
                                       redirectLink=url_for('rute'))

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM RUTE WHERE ORASDESTINATIE = :orasDestinatie and ORASPLECARE = :orasPlecare", orasPlecare=orasPlecare, orasDestinatie=orasDestinatie)
            if cursor.fetchone() is None:
                try:
                    cursor.execute("""
                            INSERT INTO RUTE (ORASPLECARE, ORASDESTINATIE, DISTANTA, DURATAESTIMATA) 
                            VALUES (:1, :2, :3,:4)
                            """, (orasPlecare, orasDestinatie, distanta, durataEstimata))
                    conn.commit()
                    return render_template('mesaj.html', title="Success",
                                           message="Ruta a fost adaugata in baza de date.", tipActiune="Acasa",
                                           redirectLink=url_for('rute'))
                except Exception :
                    conn.rollback()
                    return render_template('mesaj.html', title="Eroare",
                                           message="Campurile nu au fost completate corect.", tipActiune="Acasa",
                                           redirectLink=url_for('rute'))

            else:
                return render_template('mesaj.html', title="Eroare",
                                       message="Ruta este deja in baza de date.", tipActiune="Acasa",
                                       redirectLink=url_for('rute'))
        return render_template('new_ruta.html')
    return redirect(url_for('index'))

@app.route('/display_ruta/<int:ruta_id>', methods=['GET', 'POST'])
@login_required
def display_ruta(ruta_id):
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RUTE WHERE RutaID = :ruta_id", ruta_id=ruta_id)
        ruta_data = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM ZBORURI WHERE RutaID = :ruta_id", ruta_id=ruta_id)
        numar_zboruri = cursor.fetchone()[0]

        if request.method == 'POST':
            if numar_zboruri == 0:
                cursor.execute("DELETE FROM RUTE WHERE RutaID = :ruta_id", ruta_id=ruta_id)
                conn.commit()
                cursor.close()
                return render_template('mesaj.html', title="Succes",
                                       message="Ruta a fost stearsa.", tipActiune="Acasa",
                                       redirectLink=url_for('rute'))
            else:
                cursor.close()
                return render_template('mesaj.html', title="Eroare",
                                       message="Nu poți șterge ruta pentru că este asociată cu zboruri existente.",
                                       tipActiune="Acasa", redirectLink=url_for('rute'))

        cursor.close()
        if ruta_data:
            return render_template('display_ruta.html', ruta_data=ruta_data)
        else:
            return render_template('mesaj.html', title="Eroare",
                                   message="Ruta nu există.", tipActiune="Acasa",
                                   redirectLink=url_for('rute'))
    return redirect(url_for('index'))


@app.route('/display_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def display_user(user_id):
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilizatori WHERE USERID = :user_id", user_id=user_id)
        user_data = cursor.fetchone()
        cursor.execute("SELECT count(DISTINCT zborID) FROM Bilete WHERE USERID = :user_id", user_id=user_id)
        numar_zboruri = cursor.fetchone()[0]
        if numar_zboruri is None:
            numar_zboruri = 0
        cursor.execute("SELECT count(*) FROM Bilete WHERE USERID = :user_id", user_id=user_id)
        numar_bilete= cursor.fetchone()[0]
        if numar_bilete is None:
            numar_bilete = 0
        cursor.execute("SELECT sum(PRETBILET) FROM Bilete WHERE USERID = :user_id", user_id=user_id)
        suma_bani=cursor.fetchone()[0]
        if suma_bani is None:
            suma_bani = 0
        cursor.close()
        if user_data:
            return render_template('display_user.html', user_data=user_data,numar_zboruri=numar_zboruri,numar_bilete=numar_bilete,suma_bani=suma_bani)
        else:
            return render_template('mesaj.html', title="Eroare",
                                   message="Utilizatorul nu există.", tipActiune="Acasa",
                                   redirectLink=url_for('utilizatori'))
    return redirect(url_for('index'))

@app.route('/transfer_administrator/<int:user_id>', methods=['GET', 'POST'])
@login_required
def transfer_administrator(user_id):
    if current_user.is_admin:
        if request.method == 'POST':
            cursor = conn.cursor()
            cursor.execute("UPDATE UTILIZATORI SET ADMIN='DA' WHERE USERID= :user_id", user_id=user_id)
            conn.commit()
            cursor.close()
            return render_template('mesaj.html', title="Succes",
                                       message="Utilizatorul a fost promovat la administrator", tipActiune="Acasa",
                                       redirectLink=url_for('display_user',user_id=user_id))
    return redirect(url_for('index'))

@app.route('/transfer_utilizator/<int:user_id>', methods=['GET', 'POST'])
@login_required
def transfer_utilizator(user_id):
    if current_user.is_admin:
        if request.method == 'POST':
            cursor = conn.cursor()
            cursor.execute("UPDATE UTILIZATORI SET ADMIN='NU' WHERE USERID= :user_id", user_id=user_id)
            conn.commit()
            cursor.close()
            return render_template('mesaj.html', title="Succes",
                                       message="Utilizatorul a fost retrogradat la utilizator", tipActiune="Acasa",
                                       redirectLink=url_for('display_user',user_id=user_id))
    return redirect(url_for('index'))

@app.route('/utilizatori')
@login_required
def utilizatori():
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT USERID, NUME, PRENUME, EMAIL, DATANASTERE FROM Utilizatori order by USERID")
        users_data = cursor.fetchall()
        cursor.close()
        return render_template('utilizatori.html', users_data=users_data)
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('mesaj.html', title="Succes",
                           message="Te-ai deconectat", tipActiune="Acasa",
                           redirectLink=url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nume = request.form['nume']
        prenume = request.form['prenume']
        dataNastere = request.form['dataNastere']
        email = request.form['email']
        parola = request.form['parola']

        if not contains_digits(nume) and not contains_digits(prenume):
            if not user_exists(email):
                add_user(nume,prenume, dataNastere, email, parola)
                return render_template('mesaj.html', title="Felicitari",message = "Cont creat cu succes. Acum te poti autentifica!" , tipActiune = "Acasa", redirectLink = url_for('index') )
            else:
                return render_template('mesaj.html', title="Ne pare rau",message = "Exista deja cu un cont cu aceasta adresa de email.",tipActiune = "Acasa", redirectLink = url_for('index') )
        else:
            return render_template('mesaj.html', title="Ne pare rau",
                                   message="Numele și prenumele nu ar trebui să conțină cifre.",
                                   tipActiune="Acasa", redirectLink=url_for('index'))

    return render_template('register.html')


@app.route('/statistici')
@login_required
def statistici():
    if current_user.is_admin:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM Utilizatori WHERE ADMIN ='NU'")
        users = cursor.fetchone()
        if users is not None:
            users =users[0]
        else:
            users = 0
        cursor.execute("SELECT count(*) FROM Utilizatori WHERE ADMIN ='DA'")
        admins = cursor.fetchone()
        if admins is not None:
            admins = admins[0]
        else:
            admins = 0
        cursor.execute("SELECT count(*) FROM ZBORURI")
        total_zboruri = cursor.fetchone()
        if total_zboruri is not None:
            total_zboruri = total_zboruri[0]
        else:
            total_zboruri = 0

        cursor.execute("SELECT count(*) FROM ZBORURI WHERE DATAPLECARE < TRUNC(CURRENT_DATE)")
        zboruri_efectuate = cursor.fetchone()
        if zboruri_efectuate is not None:
            zboruri_efectuate = zboruri_efectuate[0]
        else:
            zboruri_efectuate = 0
        cursor.execute("SELECT count(*) FROM ZBORURI WHERE DATAPLECARE >= TRUNC(CURRENT_DATE)")
        zboruri_programate = cursor.fetchone()
        if zboruri_programate is not None:
            zboruri_programate = zboruri_programate[0]
        else:
            zboruri_programate = 0

        cursor.execute("SELECT count(*) FROM BILETE ")
        bilete_totale= cursor.fetchone()
        if bilete_totale is not None:
            bilete_totale =bilete_totale[0]
        else:
            bilete_totale=0
        cursor.execute("SELECT count(*) FROM BILETE WHERE STARE='Cumparat' ")
        bilete_vandute = cursor.fetchone()
        if bilete_totale is not None:
            bilete_vandute = bilete_vandute[0]
        else:
            bilete_vandute = 0
        cursor.execute("SELECT count(*) FROM BILETE WHERE STARE='Valabil' ")
        bilete_disponibile = cursor.fetchone()
        if bilete_disponibile is not None:
            bilete_disponibile = bilete_disponibile[0]
        else:
            bilete_disponibile = 0

        cursor.execute("SELECT SUM(PretBilet) FROM BILETE WHERE STARE='Cumparat'")
        incasari =cursor.fetchone()
        if incasari is not None:
            incasari= incasari[0]
        else:
            incasari = 0
        cursor.close()
        return render_template('statistici.html',admins=admins,users=users,
                               total_zboruri=total_zboruri,zboruri_efectuate=zboruri_efectuate,
                               zboruri_programate=zboruri_programate,bilete_totale=bilete_totale,
                               bilete_vandute=bilete_vandute,bilete_disponibile=bilete_disponibile,
                               incasari=incasari)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
    conn.close()
