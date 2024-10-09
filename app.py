from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Livro
class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    ano_publicacao = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'ano_publicacao': self.ano_publicacao
        }

# Rota para a interface web principal
@app.route('/')
def index():
    livros = Livro.query.all()
    return render_template('index.html', livros=livros)

# Rota para pesquisar livro pelo ID
@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    livro_id = request.form.get('livro_id')
    if livro_id:
        livro = Livro.query.get(livro_id)
        if livro:
            return redirect(url_for('livro_detalhes', id=livro.id))
        else:
            return "Livro não encontrado", 404
    return redirect(url_for('index'))

@app.route('/livros/<int:id>', methods=['GET'])
def livro_detalhes(id):
    livro = Livro.query.get(id)
    if livro is None:
        return "Livro não encontrado", 404
    return render_template('livro_detalhes.html', livro=livro)


# Rota para adicionar um novo livro com ID fornecido
@app.route('/api/livros', methods=['POST'])
def adicionar_livro():
    livro_id = request.json.get('id')
    titulo = request.json.get('titulo')
    autor = request.json.get('autor')
    ano_publicacao = request.json.get('ano_publicacao')

    # Verifica se o ID já existe
    if Livro.query.get(livro_id):
        return jsonify({"error": "Livro com este ID já existe."}), 400

    novo_livro = Livro(id=livro_id, titulo=titulo, autor=autor, ano_publicacao=ano_publicacao)
    db.session.add(novo_livro)
    db.session.commit()

    return jsonify(novo_livro.to_dict()), 201

# Rota para editar um livro existente
@app.route('/livros/editar/<int:id>', methods=['GET', 'POST'])
def editar_livro(id):
    livro = Livro.query.get(id)
    
    if livro is None:
        return "Livro não encontrado", 404

    if request.method == 'POST':
        # Atualiza os dados do livro com base nos dados enviados pelo formulário
        livro.titulo = request.form['titulo']
        livro.autor = request.form['autor']
        livro.ano_publicacao = request.form['ano_publicacao']
        
        db.session.commit()
        return redirect(url_for('livro_detalhes', id=livro.id))  # Volta para a página de detalhes do livro

    return render_template('editar_livro.html', livro=livro)


# Rota para excluir um livro
@app.route('/livros/deletar/<int:id>', methods=['POST'])
def deletar_livro(id):
    livro = Livro.query.get(id)
    if livro is None:
        return "Livro não encontrado", 404
    
    db.session.delete(livro)
    db.session.commit()
    return redirect(url_for('index'))

# Inicializando o banco de dados ao iniciar o app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
