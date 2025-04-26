from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular_media', methods=['POST'])
def calcular_media():
    data = request.get_json()
    gastos = data.get('gastos', [])

    if not gastos:
        return jsonify({'erro': 'Nenhum gasto enviado.'}), 400

    try:
        gastos = [float(g) for g in gastos]
        media = sum(gastos) / len(gastos)
        return jsonify({'media': round(media, 2)})
    except ValueError:
        return jsonify({'erro': 'Dados inválidos.'}), 400


if __name__ == '__main__':
    app.run(debug=True)

