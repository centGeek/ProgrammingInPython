from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class IrisModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    sepal_length_cm = db.Column(db.Float, nullable=False)
    sepal_width_cm = db.Column(db.Float, nullable=False)
    petal_length_cm = db.Column(db.Float, nullable=False)
    petal_width_cm = db.Column(db.Float, nullable=False)
    species = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return (f"Iris(sepal_length_cm={self.sepal_length_cm}, "
                f"sepal_width_cm={self.sepal_width_cm}, "
                f"petal_length_cm={self.petal_length_cm}, "
                f"petal_width_cm={self.petal_width_cm}, "
                f"species={self.species})")

iris_args = reqparse.RequestParser()
iris_args.add_argument('sepal_length_cm', type=float, required=True, help="sepal length cannot be blank")
iris_args.add_argument('sepal_width_cm', type=float, required=True, help="sepal width cannot be blank")
iris_args.add_argument('petal_length_cm', type=float, required=True, help="petal length cannot be blank")
iris_args.add_argument('petal_width_cm', type=float, required=True, help="petal width cannot be blank")
iris_args.add_argument('species', type=str, required=True, help="species cannot be blank")

irisFields = {
    'id':fields.Integer,
    'sepal_length_cm':fields.Float,
    'sepal_width_cm':fields.Float,
    'petal_length_cm':fields.Float,
    'petal_width_cm':fields.Float,
    'species':fields.String
}

class Iris(Resource):
    @marshal_with(irisFields)
    def get(self):
        iris_data = IrisModel.query.all()
        result = []
        for iris in iris_data:
            result.append({
                'id': iris.id,
                'sepal_length_cm': iris.sepal_length_cm,
                'sepal_width_cm': iris.sepal_width_cm,
                'petal_length_cm': iris.petal_length_cm,
                'petal_width_cm': iris.petal_width_cm,
                'species': iris.species
            })
        return result

api.add_resource(Iris, '/api/data')

@app.route('/')
def home():
    iris_data = IrisModel.query.all()
    return render_template('index.html', data=iris_data)

@app.route('/add', methods=['GET', 'POST'])
def add_iris():
    if request.method == 'POST':
        try:
            iris = IrisModel(
                sepal_length_cm=float(request.form['sepal_length_cm']),
                sepal_width_cm=float(request.form['sepal_width_cm']),
                petal_length_cm=float(request.form['petal_length_cm']),
                petal_width_cm=float(request.form['petal_width_cm']),
                species=request.form['species']
            )
            db.session.add(iris)
            db.session.commit()
            return render_template('success.html', iris=iris)
        except Exception as e:
            return f"An error occurred: {e}", 400
    return render_template('form.html')
def delete_iris(id):
    iris = IrisModel.query.filter_by(id=id).first()
    if not iris:
        abort(404, "Not found Iris")
    db.session.delete(iris)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
