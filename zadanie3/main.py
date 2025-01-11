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

    @marshal_with(irisFields)
    def delete(self, id):
        iris = IrisModel.query.get(id)
        if not iris:
            abort(404, message="Iris with id {} not found".format(id))
        db.session.delete(iris)
        db.session.commit()
        return '', 204
    @marshal_with(irisFields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sepal_length_cm', type=float, required=True, help="Sepal length cannot be blank")
        parser.add_argument('sepal_width_cm', type=float, required=True, help="Sepal width cannot be blank")
        parser.add_argument('petal_length_cm', type=float, required=True, help="Petal length cannot be blank")
        parser.add_argument('petal_width_cm', type=float, required=True, help="Petal width cannot be blank")
        parser.add_argument('species', type=str, required=True, help="Species cannot be blank")
        
        try:
            args = parser.parse_args()
        except Exception as e:
            abort(400, message=str(e))

        new_iris = IrisModel(
            sepal_length_cm=args['sepal_length_cm'],
            sepal_width_cm=args['sepal_width_cm'],
            petal_length_cm=args['petal_length_cm'],
            petal_width_cm=args['petal_width_cm'],
            species=args['species']
        )

        db.session.add(new_iris)
        db.session.commit()

        return new_iris, 201 
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
            except Exception as e:
                return f"An error occurred: {e}", 400
        return render_template('form.html')

api.add_resource(Iris, '/api/data', '/api/data/<int:id>')

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

@app.route('/delete/<int:id>', methods=['POST', 'DELETE'])
def delete_iris(id):
    try:
        iris = IrisModel.query.get(id)        
        if not iris:
            return f"Iris with id {id} not found", 404
        db.session.delete(iris)
        db.session.commit()

        return render_template('index.html')
    except Exception as e:
        return f"An error occurred: {e}", 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
