from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///solicitacoes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "chave_super_secreta"

db = SQLAlchemy(app)

USUARIO_ADMIN = "admin"
SENHA_ADMIN = "123"

fuso_brasil = pytz.timezone("America/Sao_Paulo")

class Solicitacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(100), nullable=False)
    produto = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Pendente")
    data = db.Column(db.DateTime, default=lambda: datetime.now(fuso_brasil))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")   
        senha = request.form.get("senha")

        if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
            session["logado"] = True
            return redirect(url_for("admin"))

        return render_template("login.html", erro="Usuário ou senha inválidos.")

    return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":

        nome = request.form.get("nome")
        setor = request.form.get("setor")
        produto = request.form.get("produto")
        quantidade = request.form.get("quantidade")

        if not nome or not setor or not produto or not quantidade:
            return render_template("formulario.html", erro="Preencha todos os campos!")

        nova = Solicitacao(
            nome=nome,
            setor=setor,
            produto=produto,
            quantidade=int(quantidade)
        )

        db.session.add(nova)
        db.session.commit()

        return redirect(url_for("sucesso"))

    return render_template("formulario.html")

@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))

    solicitacoes = Solicitacao.query.all()
    return render_template("admin.html", solicitacoes=solicitacoes)

@app.route("/excluir/<int:id>")
def excluir(id):
    solicitacao = Solicitacao.query.get_or_404(id)
    db.session.delete(solicitacao)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/status/<int:id>/<novo_status>")
def alterar_status(id, novo_status):
    if not session.get("logado"):
        return redirect(url_for("login"))

    solicitacao = Solicitacao.query.get_or_404(id)
    solicitacao.status = novo_status
    db.session.commit()

    return redirect(url_for("admin"))

@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)