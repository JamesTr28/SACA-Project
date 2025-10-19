from flask import Blueprint, request, jsonify

triage_bp = Blueprint("triage", __name__, url_prefix="/api/triage")

@triage_bp.post("/summary")
def summary():
    data = request.get_json(silent=True) or {}
    profile = data.get("profile") or {}

    name   = profile.get("full_name") or "Patient"
    age    = profile.get("age")
    gender = profile.get("gender")

    nlp     = profile.get("nlp_assessment")
    nlp_c   = profile.get("nlp_confidence")
    skin    = profile.get("skin_analysis")
    skin_c  = profile.get("skin_confidence")

    parts = [f"{name} ({gender or 'unspecified'}, {age or '?'}y)."]
    if nlp:  parts.append(f"Text suggests **{nlp}** ({nlp_c if nlp_c is not None else '?'}%).")
    if skin: parts.append(f"Skin analysis: **{skin}** ({skin_c if skin_c is not None else '?'}%).")

    summary = " ".join(parts) or "No clinical information available."
    next_steps = [
        "This is not a diagnosis.",
        "If symptoms worsen or you feel unwell, seek medical care."
    ]
    return jsonify({"summary": summary, "next_steps": next_steps})
