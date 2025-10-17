// src/chat-data.js
export const chatFlow = {
  // --- PART 1: BASIC INFORMATION (Unchanged) ---
  1: { key: 'fullName', type: 'text', text: 'To begin, what is your full name?', answers: [{ text: 'Continue', nextId: 2 }] },
  2: { key: 'gender', type: 'choice', text: 'What is your gender?', answers: [ { text: 'Male', nextId: 3 }, { text: 'Female', nextId: 3 }, { text: 'Other', nextId: 3 }, { text: 'Prefer not to say', nextId: 3 } ] },
  3: { key: 'age', type: 'text', text: 'And your age?', inputType: 'number', min: 1, max: 120, answers: [{ text: 'Continue', nextId: 4 }] },
  4: { key: 'weight', type: 'text', text: 'What is your current weight in kilograms (kg)? (Optional)', inputType: 'number', min: 1, max: 500, answers: [{ text: 'Continue', nextId: 5 }] },
  5: { key: 'conditions', type: 'text', text: 'Do you have any ongoing medical conditions, like diabetes or high blood pressure? (Optional)', answers: [{ text: 'Continue', nextId: 6 }] },
  6: { key: 'allergies', type: 'text', text: 'Do you have any known allergies? (Optional)', answers: [{ text: 'Continue', nextId: 7 }] },
  7: { key: 'medications', type: 'text', text: 'Finally, are you taking any regular medications? (Optional)', answers: [{ text: 'Continue', nextId: 8 }] },

  // --- PART 2: SERVICE SELECTION (Now with 3 options) ---
  8: {
    key: 'service',
    type: 'choice',
    text: 'Thank you. How can I help you today?',
    answers: [
      { text: 'General Check-up (by text)', nextId: 9 },      // Path 1: NLP
      { text: 'Select Symptoms by Image', nextId: 10 },  // Path 2: Symptom Picker (Restored)
      { text: 'Skin Lesion Analysis', nextId: 11 }          // Path 3: Skin Upload
    ]
  },

  // --- PATH 1: NLP FLOW ---
  9: {
    key: 'nlpSymptoms',
    type: 'nlp-input',
    text: 'Please describe your symptoms in detail.',
    answers: [{ text: 'Analyze', nextId: 13 }] // Goes to final summary
  },

  // --- PATH 2: SYMPTOM PICKER FLOW ---
  10: {
    key: 'symptoms',
    type: 'symptom-picker',
    text: 'Please select your primary symptoms from the list.',
    answers: [{ text: 'Next', nextId: 13 }] // Goes to final summary
  },

  // --- PATH 3: SKIN LESION ANALYSIS FLOW ---
  11: {
    key: 'skinImage',
    type: 'skin-upload',
    text: 'Please upload a clear photo of the skin area for analysis.',
    answers: [{ text: 'Get Result', nextId: 12 }]
  },
  12: {
    key: 'skinResult',
    text: 'Analyzing your image...',
    nextId: 13 // Goes to final summary
  },

  // --- FINAL STEP: SUMMARY REPORT ---
  13: {
    type: 'summary',
    text: 'Please confirm your input below. This is your final report.',
    end: true
  }
};