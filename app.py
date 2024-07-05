from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from scraper.scraper import scrape_content

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content.db'
db = SQLAlchemy(app)

# def create_app():
#     app = Flask(__name__)
#     # app configuration
#     return app


class EducationalContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    link = db.Column(db.String(255))
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'description': self.description
        }
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    results = EducationalContent.query.filter(EducationalContent.title.like(f'%{query}%')).all()
    if not results:
        scraped_results = scrape_content(query)
        for result in scraped_results:
            content = EducationalContent(**result)
            db.session.add(content)
        db.session.commit()
        results = EducationalContent.query.filter(EducationalContent.title.like(f'%{query}%')).all()
    return jsonify([r.to_dict() for r in results])

if __name__ == '__main__':
    db.create_all()  # Create tables
    app.run(debug=True)
