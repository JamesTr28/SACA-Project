from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    from .vision.routes import vision_bp
    from .nlp.routes   import nlp_bp
    from .asr.routes   import asr_bp
    from .triage.routes import triage_bp   # ← add this

    app.register_blueprint(vision_bp)
    app.register_blueprint(nlp_bp)
    app.register_blueprint(asr_bp)
    app.register_blueprint(triage_bp)      # ← add this

    return app
