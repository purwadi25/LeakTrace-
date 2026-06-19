from flask import Flask, render_template, request, redirect, session
import os
import hashlib
import pymysql
import hmac

SECRET_KEY = "LEAKTRACE2026_SECRET"

app = Flask(__name__)
app.secret_key = "LEAKTRACE_LOGIN_SECRET"


# ==========================
# KONFIGURASI DATABASE
# ==========================
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='leaktrace'
    )

def generate_fingerprint(
    document_hash,
    receiver_id
):

    data = (
        document_hash +
        receiver_id
    ).encode()

    fingerprint = hmac.new(
        SECRET_KEY.encode(),
        data,
        hashlib.sha256
    ).hexdigest()

    return fingerprint



# ==========================
# KONFIGURASI UPLOAD
# ==========================
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Membuat folder uploads otomatis
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ==========================
# KONFIGURASI Login Admin
# ==========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            session['logged_in'] = True

            return redirect('/')

        else:

            return """
            <h3>Login Gagal</h3>
            <a href='/login'>Coba Lagi</a>
            """

    return render_template('login.html')

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

# ==========================
# DASHBOARD
# ==========================
@app.route('/')
def dashboard():

    if 'logged_in' not in session:
        return redirect('/login')

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM documents"
    )
    total_documents = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM distributions"
    )
    total_distributions = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM investigations"
    )
    total_investigations = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        'dashboard.html',
        total_documents=total_documents,
        total_distributions=total_distributions,
        total_investigations=total_investigations
    )


# ==========================
# UPLOAD DOKUMEN
# ==========================
@app.route('/upload', methods=['GET', 'POST'])
def upload_document():

    if request.method == 'POST':

        # cek apakah file dipilih
        if 'document' not in request.files:
            return "Tidak ada file yang dipilih"

        file = request.files['document']

        if file.filename == '':
            return "Tidak ada file yang dipilih"

        if file:

            # simpan file
            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                file.filename
            )

            file.save(filepath)

            # baca file
            with open(filepath, "rb") as f:
                file_data = f.read()

            # generate SHA-256
            sha256_hash = hashlib.sha256(
                file_data
            ).hexdigest()

            # ==========================
            # SIMPAN KE DATABASE
            # ==========================
            connection = get_db_connection()

            cursor = connection.cursor()

            sql = """
            INSERT INTO documents
            (filename, original_hash)
            VALUES (%s, %s)
            """

            cursor.execute(
                sql,
                (
                    file.filename,
                    sha256_hash
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            # ==========================
            # TAMPILKAN HASIL
            # ==========================
            return f"""
            <html>
            <body>

                <h2>Upload Berhasil</h2>

                <p><b>Nama File:</b> {file.filename}</p>

                <p><b>SHA-256 Hash:</b></p>

                <textarea rows="6" cols="90">
{sha256_hash}
                </textarea>

                <br><br>

                <a href="/">
                    <button>Kembali ke Dashboard</button>
                </a>

            </body>
            </html>
            """

    return render_template('upload.html')

# ==========================
# INVESTIGASI
# ==========================
@app.route('/investigation', methods=['GET', 'POST'])
def investigation():

    if request.method == 'POST':

        file = request.files['document']

        if file.filename == '':
            return "File tidak dipilih"

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename
        )

        file.save(filepath)

        with open(filepath, "rb") as f:
            file_data = f.read()

        leaked_hash = hashlib.sha256(
            file_data
        ).hexdigest()

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, filename
            FROM documents
            WHERE original_hash=%s
        """, (leaked_hash,))

        document = cursor.fetchone()

        if document:

            document_id = document[0]
            filename = document[1]

            cursor.execute("""
                SELECT recipient_name
                FROM distributions
                WHERE document_id=%s
            """, (document_id,))

            distribution = cursor.fetchone()

            recipient = (
                distribution[0]
                if distribution
                else "Tidak Diketahui"
            )

            cursor.execute("""
                INSERT INTO investigations
                (
                    uploaded_file,
                    detected_recipient,
                    status
                )
                VALUES
                (%s,%s,%s)
            """,
            (
                file.filename,
                recipient,
                "TERDETEKSI"
            ))

            connection.commit()

            cursor.close()
            connection.close()

            return f"""
<h2>Hasil Investigasi</h2>

<p><b>Dokumen:</b> {filename}</p>

<p><b>Penerima Terindikasi:</b>
{recipient}</p>

<p><b>Status:</b>
TERDETEKSI</p>

<br>

<br><br>

<a href="/">
    <button>Kembali Dashboard</button>
</a>
"""

        else:

            cursor.execute("""
                INSERT INTO investigations
                (
                    uploaded_file,
                    detected_recipient,
                    status
                )
                VALUES
                (%s,%s,%s)
            """,
            (
                file.filename,
                "-",
                "TIDAK DITEMUKAN"
            ))

            connection.commit()

            cursor.close()
            connection.close()

            return """
            <h2>Hasil Investigasi</h2>

            <p>Dokumen tidak ditemukan dalam database.</p>

            <a href="/">
                <button>Kembali Dashboard</button>
            </a>
            """

    return render_template(
        'investigation.html'
    )

@app.route('/distribute', methods=['GET', 'POST'])
def distribute_document():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':

        document_id = request.form['document_id']
        recipient_name = request.form['recipient_name']

        cursor.execute(
            """
            SELECT original_hash
            FROM documents
            WHERE id=%s
            """,
            (document_id,)
        )

        result = cursor.fetchone()

        if not result:
            return "Dokumen tidak ditemukan"

        original_hash = result[0]

        fingerprint = generate_fingerprint(
            original_hash,
            recipient_name
        )

        cursor.execute(
            """
            INSERT INTO distributions
            (document_id, recipient_name, fingerprint)
            VALUES (%s, %s, %s)
            """,
            (
                document_id,
                recipient_name,
                fingerprint
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return f"""
        <h2>Distribusi Berhasil</h2>

        <p>Dokumen ID: {document_id}</p>

        <p>Penerima: {recipient_name}</p>

        <p>Fingerprint:</p>

        <textarea rows="6" cols="90">
{fingerprint}
        </textarea>

        <br><br>

        <a href="/">
            <button>Kembali Dashboard</button>
        </a>
        """

    cursor.execute(
        """
        SELECT id, filename
        FROM documents
        """
    )

    documents = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'distribute.html',
        documents=documents
    )

@app.route('/history')
def history():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            uploaded_file,
            detected_recipient,
            status,
            investigated_at
        FROM investigations
        ORDER BY investigated_at DESC
    """)

    investigations = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'history.html',
        investigations=investigations
    )

# ==========================
# DAFTAR DISTRUSI DOKUMEN
# ==========================
@app.route('/distributions')
def distributions():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            distributions.id,
            documents.filename,
            distributions.recipient_name,
            distributions.fingerprint,
            distributions.distributed_at
        FROM distributions
        JOIN documents
        ON distributions.document_id = documents.id
        ORDER BY distributions.distributed_at DESC
    """)

    data_distributions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'distributions.html',
        data_distributions=data_distributions
    )

@app.route('/documents')
def documents():

    if 'logged_in' not in session:
        return redirect('/login')

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            filename,
            original_hash,
            upload_date
        FROM documents
        ORDER BY upload_date DESC
    """)

    documents = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'documents.html',
        documents=documents
    )

# ==========================
# DETAIL DOKUMEN
# ==========================
@app.route('/document/<int:id>')
def document_detail(id):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Ambil data dokumen
    cursor.execute("""
        SELECT id, filename, original_hash
        FROM documents
        WHERE id=%s
    """, (id,))

    document = cursor.fetchone()

    if not document:
        cursor.close()
        connection.close()
        return "Dokumen tidak ditemukan"

    # Ambil daftar distribusi dokumen
    cursor.execute("""
        SELECT
            recipient_name,
            fingerprint,
            distributed_at
        FROM distributions
        WHERE document_id=%s
        ORDER BY distributed_at DESC
    """, (id,))

    distributions = cursor.fetchall()

    total_distributions = len(distributions)

    cursor.close()
    connection.close()

    return render_template(
        'document_detail.html',
        document=document,
        distributions=distributions,
        total_distributions=total_distributions
    )

# ==========================
# SEARCH
# ==========================
@app.route('/search', methods=['GET', 'POST'])
def search():

    results = []

    if request.method == 'POST':

        keyword = request.form['keyword']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                documents.filename,
                distributions.recipient_name,
                distributions.fingerprint,
                distributions.distributed_at
            FROM distributions
            JOIN documents
            ON distributions.document_id = documents.id
            WHERE documents.filename LIKE %s
            OR distributions.recipient_name LIKE %s
            ORDER BY distributions.distributed_at DESC
        """, (
            '%' + keyword + '%',
            '%' + keyword + '%'
        ))

        results = cursor.fetchall()

        cursor.close()
        connection.close()

    return render_template(
        'search.html',
        results=results
    )


# ==========================
# MAIN
# ==========================
if __name__ == '__main__':
    app.run(debug=True)