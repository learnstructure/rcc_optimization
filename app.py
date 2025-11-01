from flask import Flask, request, jsonify
from flask_cors import CORS
from rectangular_beam.model_loader import load_models
from rectangular_beam.optimizer import predict_beam_design


def create_app():
    """
    Application factory for scalability and modularity.
    """
    app = Flask(__name__)
    CORS(app)

    # Load models once during app startup
    models = load_models()

    @app.route("/")
    def home():
        return jsonify(
            {"message": "RCC Beam Design Optimization API is active.", "status": "ok"}
        )

    @app.route("/srrs_beam", methods=["POST"])
    def design_beam():
        """
        Example Input JSON:
        {
            "fck": 30,
            "fy": 415,
            "Mu": 120
        }
        """
        try:
            data = request.get_json(force=True)
            result = predict_beam_design(data, models)
            return jsonify({"status": "success", "result": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    return app


# Gunicorn entrypoint
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
