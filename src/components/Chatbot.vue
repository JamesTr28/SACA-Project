<template>
  <div class="chatbot-container">
    <div class="messages-container">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', message.sender]"
      >
        <p v-html="message.text.replace(/\n/g, '<br>')"></p>
      </div>
      <div v-if="isTyping" class="message bot"><p>...</p></div>
    </div>

    <div v-if="!conversationEnded" class="input-container">
      <!-- multiple-choice -->
      <template v-if="currentQuestion.type === 'choice'">
        <button
          v-for="(answer, index) in currentQuestion.answers"
          :key="index"
          @click="handleChoice(answer)"
        >
          {{ answer.text }}
        </button>
      </template>

      <!-- plain text / number -->
      <template v-else-if="currentQuestion.type === 'text'">
        <input
          v-model="userInput"
          :type="currentQuestion.inputType || 'text'"
          :min="currentQuestion.min"
          :max="currentQuestion.max"
          :step="currentQuestion.step"
          inputmode="numeric"
          placeholder="Type your answer..."
          class="text-entry"
          @keyup.enter="submitText"
        />
        <button :disabled="!userInput" @click="submitText">Send</button>
        <p v-if="error" class="error-message">{{ error }}</p>
      </template>
      <!-- Submit and return result -->
      <template v-if="currentQuestion.type === 'submit'">
        <button
          v-for="(answer, index) in currentQuestion.answers"
          :key="index"
          @click="handleChoice(answer)"
        >
          {{ answer.text }}
        </button>
      </template>
      <!-- symptom picker -->
      <template v-else-if="currentQuestion.type === 'symptom-picker'">
        <div class="symptom-grid">
          <div
            v-for="symptom in symptoms"
            :key="symptom.label"
            class="symptom-item"
            :class="{ selected: selectedSymptoms.includes(symptom.label) }"
            @click="toggleSymptom(symptom.label)"
          >
            <img :src="getSymptomImageUrl(symptom.img)" :alt="symptom.label" />
            <p>
              {{
                isWarlpiri
                  ? warlpiriTranslations[symptom.label] || symptom.label
                  : symptom.label
              }}
            </p>
            <p>{{ language.value }}</p>
          </div>
        </div>
        <button class="next-button" @click="submitSymptoms">Next</button>
      </template>

      <!-- NLP text + microphone -->
      <template v-else-if="currentQuestion.type === 'nlp-input'">
        <textarea
          v-model="userInput"
          class="nlp-textarea"
          placeholder="Describe your symptoms here..."
        ></textarea>

        <div
          style="
            display: flex;
            gap: 8px;
            align-items: center;
            width: 100%;
            justify-content: center;
          "
        >
          <!-- Handle file upload -->
          <input
            type="file"
            ref="fileInput"
            accept="audio/*"
            style="display: none"
            @change="handleFileSelect"
          />

          <button class="next-button" v-if="!isRec" @click="startRec">
            🎙️ Start
          </button>
          <button class="next-button" v-else @click="stopRec">⏹ Stop</button>
          <button class="next-button" @click="triggerUpload">
            Upload Video for demo
          </button>
          <span v-if="asrError" class="error-message" style="margin: 0">{{
            asrError
          }}</span>
        </div>

        <button class="next-button" @click="submitNLPText">
          Analyze Symptoms
        </button>
      </template>

      <!-- skin upload -->
      <template v-else-if="currentQuestion.type === 'skin-upload'">
        <input
          type="file"
          ref="skinUploadInput"
          style="display: none"
          accept="image/*"
          @change="handleSkinUpload"
        />
        <button class="next-button" @click="$refs.skinUploadInput.click()">
          Upload Photo
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useTriageStore } from "@/store/triageStore";
import { chatFlow } from "../chat-data.js";
import axios from "axios";
import { classifyDisease } from "./severityRating.js";
import i18nMessages from "@/i18n/messages"; // Renamed import to avoid conflict

/* ---------- API URLs ---------- */
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
const VISION_URL = `${API_BASE}/vision/predict`;
const NLP_URL = `${API_BASE}/nlp/process`;
const ASR_URL = `${API_BASE}/asr/transcribe`;
const ASR_BLOB_URL = `${API_BASE}/asr/transcribe-blob`;

/* ---------- STATE ---------- */
const isWarlpiri = computed(
  () => language.value?.trim().toLowerCase() === "warlpiri"
);
const router = useRouter();
const store = useTriageStore();
const collectedData = ref({});
const messages = ref([]); // This is for chat messages
const currentQuestionId = ref(0);
const isTyping = ref(false);
const conversationEnded = ref(false);
const userInput = ref("");
const error = ref("");
const language = ref("English");
const fileInput = ref(null);
const asrResult = ref(null);
const currentQuestion = ref(chatFlow[currentQuestionId.value]);
const selectedSymptoms = ref([]);

/* ---------- SYMPTOM GRID ---------- */
const warlpiriTranslations = {
  "Abdominal Pain": "Miyalu Raga",
  "High Fever": "Papimi",
  Cough: "Kuntulpa",
  "Sore throat": "Waninja-kiri",
  Headache: "Ruku-ruku",
  Nausea: "Kalti-kalti-mani",
  Vomit: "Karlti-karlti",
  Diarrhea: "Kuna-kalykala",
  "Chest Pain": "Yutarki raga",
  "Shortness of breath": "Ngaany-kutu-kutu",
  Rash: "Janjalyarra",
  Fatigue: "Murra-murra",
};
const symptoms = ref([
  { label: "Abdominal Pain", img: "abdominal-pain.png" },
  { label: "Chest Pain", img: "chest-pain.png" },
  { label: "Cough", img: "cough.png" },
  { label: "Diarrhea", img: "diarrhea.png" },
  { label: "Fatigue", img: "fatigue.png" },
  { label: "High Fever", img: "fever_high.png" },
  { label: "Headache", img: "headache.png" },
  { label: "Nausea", img: "nausea.png" },
  { label: "Rash", img: "rash.png" },
  { label: "Vomit", img: "vomit.png" },
]);

const getSymptomImageUrl = (imageName) =>
  new URL(`../assets/${imageName}`, import.meta.url).href;

/* ---------- CORE HELPERS ---------- */
const getTranslatedText = (questionId) => {
  const lang = language.value.toLowerCase() === "warlpiri" ? "wp" : "en";
  // Get text from i18n messages using the question ID
  return i18nMessages[lang][`${questionId}.text`] || currentQuestion.value.text;
};

const addMessage = (text, sender) => {
  // If it's a bot message, translate it
  const finalText =
    sender === "bot" ? getTranslatedText(currentQuestionId.value) : text;

  messages.value.push({ id: messages.value.length, text: finalText, sender });
  if (sender === "user" && currentQuestion.value.key) {
    collectedData.value[currentQuestion.value.key] = text;
  }
};
const addMessageNoT = (text, sender) => {
  messages.value.push({ id: messages.value.length, text, sender });
  if (sender === "user" && currentQuestion.value.key) {
    collectedData.value[currentQuestion.value.key] = text;
  }
};

const goToNextStep = (nextId) => {
  if (chatFlow[nextId]?.end) return finishConversation();
  isTyping.value = true;
  userInput.value = "";
  error.value = "";
  setTimeout(() => {
    isTyping.value = false;
    if (nextId && chatFlow[nextId]) {
      currentQuestionId.value = nextId;
      currentQuestion.value = chatFlow[nextId];
      addMessageNoT(getTranslatedText(nextId), "bot");
    }
  }, 800);
};

function finishConversation() {
  addMessage("Thank you! Generating your summary...", "bot");
  isTyping.value = false;
  conversationEnded.value = true;
  store.updateProfile(collectedData.value);
  router.push("/confirm");
  console.log("Collected Data:", collectedData.value);
}
// Handle submitting on chatbot

// Submit and disease preduction
const TRIAGE_URL = `${API_BASE}/predict`;
const result = ref("");
const submitting = ref(false);
// const subError = ref("");
async function handleSubmit() {
  store.updateProfile(collectedData.value);
  result.value = "";
  submitting.value = true;

  try {
    console.log("Selected symptoms for submission:", [
      store.selectedSymptoms.value,
    ]);
    const rawSymptoms = [...store.selectedSymptoms];

    const formattedSymptoms = rawSymptoms.map((s) =>
      s.trim().toLowerCase().replace(/\s+/g, "_")
    );

    console.log("Submitting symptoms:", formattedSymptoms);
    const { data } = await axios.post(
      TRIAGE_URL,
      { symptoms: formattedSymptoms },
      {
        headers: { "Content-Type": "application/json" },
      }
    );

    console.log("Triage API response:", data);
    console.log(data);
    console.log("Predicted Disease:", data.disease);
    addMessageNoT(
      `🩺 Based on your inputs, the predicted condition is: ${data.disease}`,
      "bot"
    );
    const severity = classifyDisease(data.disease);
    addMessageNoT(`And its severity is classified as: ${severity}`, "bot");
    let precautionsList = data.precautions.map((p) => `• ${p}`).join("\n");
    if (precautionsList == "") {
      switch (severity) {
        case "mild":
          precautionsList =
            "• Rest at home\n• Stay hydrated\n• Monitor symptoms";
          break;
        case "moderate":
          precautionsList =
            "• Consult a healthcare provider\n• Avoid strenuous activities\n• Follow prescribed medications";
          break;
        case "severe":
          precautionsList =
            "• Seek immediate medical attention\n• Follow emergency protocols\n• Do not self-medicate";
          break;
        default:
          precautionsList = "• Maintain general health precautions";
      }
    }
    addMessageNoT(`And the precautions for it are:\n${precautionsList}`, "bot");
  } catch (e) {
    error.value =
      e?.response?.data?.message ||
      e.message ||
      "NetworkError when attempting to fetch resource.";
  } finally {
    submitting.value = false;
  }
}

/* ---------- CHOICES / TEXT ---------- */
const handleChoice = async (answer) => {
  if (answer.text === "No, submit") {
    await handleSubmit();
    goToNextStep(answer.nextId);
  } else if (answer.text === "Reset") {
    // Reset conversation
    messages.value = [];
    currentQuestionId.value = 1;
    currentQuestion.value = chatFlow[1];
    conversationEnded.value = false;
    collectedData.value = {};
    selectedSymptoms.value = [];
    store.reset();
    addMessage(getTranslatedText(1), "bot");
  } else if (answer.text === "English" || answer.text === "Warlpiri") {
    language.value = answer.text;
    addMessageNoT(`Language set to ${language.value}.`, "bot");
    // Translate next question before moving on
    goToNextStep(answer.nextId);
  } else {
    addMessage(answer.text, "user");
    goToNextStep(answer.nextId);
    console.log(language.value);
  }
};

const submitText = () => {
  const q = currentQuestion.value;
  let valueToSubmit = userInput.value;
  if (q.inputType === "number") {
    if (
      String(userInput.value).toLowerCase() === "skip" ||
      userInput.value === ""
    ) {
      valueToSubmit = "Skipped";
    } else {
      const num = Number(userInput.value);
      if (
        isNaN(num) ||
        (q.min != null && num < q.min) ||
        (q.max != null && num > q.max)
      ) {
        error.value = `Please enter a valid number between ${q.min} and ${q.max}.`;
        return;
      }
      valueToSubmit = num;
    }
  }
  addMessage(String(valueToSubmit), "user");
  goToNextStep(q.answers[0].nextId);
};

/* ---------- NLP (text analysis) ---------- */
const submitNLPText = async () => {
  const text = userInput.value.trim();
  addMessage(text || "Skipped detailed description.", "user");
  if (!text) return goToNextStep(currentQuestion.value.answers[0].nextId);

  isTyping.value = true;
  error.value = "";

  try {
    // First translate if language is Warlpiri
    let processedText = text;
    if (language.value.toLowerCase() === "warlpiri") {
      addMessageNoT("Translating from Warlpiri...", "bot");
      const { data: translationData } = await axios.post(
        `${API_BASE}/translate`,
        { text: text },
        { headers: { "Content-Type": "application/json" } }
      );
      processedText = translationData.translation;
      addMessageNoT(`Translation: ${processedText}`, "bot");
    }

    // Now process the text (either translated or original)
    const { data } = await axios.post(NLP_URL, processedText, {
      headers: { "Content-Type": "text/plain" },
    });

    const results = data?.results || [];
    const summary = results.length ? results.join(", ") : "No findings";
    addMessageNoT(`🩺 NLP Results: ${summary}`, "bot");
    console.log("NLP Results:", results);
    console.log("NLP Summary:", summary);

    // Store both original and processed text
    collectedData.value.original_text = text;
    collectedData.value.nlp_text = processedText;
    collectedData.value.nlp_results = summary;

    // Add symptoms to store
    for (const symptom of results) {
      store.addSymptom(symptom);
      console.log("Added symptom from NLP:", store.selectedSymptoms);
      console.log([...store.selectedSymptoms]);
    }
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || "Analysis failed.";
    error.value = msg;
    addMessageNoT(`❌ ${msg}`, "bot");
  } finally {
    isTyping.value = false;
    goToNextStep(currentQuestion.value.answers[0].nextId);
  }
};
/* ---------- Symptom picker ---------- */
const toggleSymptom = (symptomLabel) => {
  const i = selectedSymptoms.value.indexOf(symptomLabel);
  if (i === -1) selectedSymptoms.value.push(symptomLabel);
  else selectedSymptoms.value.splice(i, 1);
};
const submitSymptoms = () => {
  const txt = selectedSymptoms.value.length
    ? selectedSymptoms.value.join(", ")
    : "No symptoms selected.";
  selectedSymptoms.value.forEach((symptom) => store.addSymptom(symptom));
  addMessage(txt, "user");
  goToNextStep(currentQuestion.value.answers[0].nextId);
};

/* ---------- Skin image upload ---------- */
const handleSkinUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  error.value = "";
  addMessage("Photo selected. Analyzing...", "user");
  isTyping.value = true;

  const formData = new FormData();
  formData.append("image", file);
  try {
    const { data: result } = await axios.post(VISION_URL, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    const msg = `Analysis Result: ${
      result.predicted_class_name
    }\nConfidence: ${(result.confidence * 100).toFixed(2)}%`;
    addMessageNoT(msg, "bot");

    // store + jump straight to confirm
    collectedData.value.skin_analysis = result.predicted_class_name;
    collectedData.value.skin_confidence = Math.round(
      (result.confidence ?? 0) * 100
    );
    finishConversation();
  } catch (err) {
    const msg =
      err?.response?.data?.message ||
      err?.message ||
      "Sorry, the analysis could not be completed.";
    error.value = msg;
    addMessage(`❌ ${msg}`, "bot");
    goToNextStep(currentQuestion.value.answers[0].nextId);
  } finally {
    isTyping.value = false;
    event.target.value = "";
  }
};

/* ---------- Microphone (ASR) ---------- */
const isRec = ref(false);
const asrError = ref("");
let mediaRecorder;
let chunks = [];

const startRec = async () => {
  asrError.value = "";
  try {
    if (!navigator.mediaDevices?.getUserMedia)
      throw new Error("Microphone not supported in this browser");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];
    mediaRecorder.ondataavailable = (e) => {
      if (e.data?.size) chunks.push(e.data);
    };
    mediaRecorder.onstop = async () => {
      try {
        const blob = new Blob(chunks, {
          type: mediaRecorder.mimeType || "audio/webm",
        });
        console.log("Blob type:", blob.type); // e.g., 'audio/webm'
        console.log("Blob size:", blob.size);
        const fd = new FormData();
        fd.append("audio", blob, "recording.webm");
        const { data } = await axios.post(ASR_BLOB_URL, fd);
        userInput.value =
          (userInput.value ? userInput.value + " " : "") + (data?.text || "");
        collectedData.value.voice_text = data?.text || "";
      } catch (e) {
        asrError.value = e?.response?.data?.message || "ASR failed";
      }
    };
    mediaRecorder.start();
    isRec.value = true;
  } catch (e) {
    asrError.value = e.message || "Microphone access denied";
  }
};
const stopRec = () => {
  if (mediaRecorder && isRec.value) {
    mediaRecorder.stop();
    isRec.value = false;
  }
};
function triggerUpload() {
  error.value = "";
  asrResult.value = null;
  fileInput.value?.click(); // opens file picker
}

async function handleFileSelect(event) {
  console.log("File selected");
  error.value = "";
  const file = event.target.files[0];
  console.log("Selected file:", file);
  if (!file) return;

  try {
    const formData = new FormData();
    formData.append("audio", file);
    const { data: result } = await axios.post(ASR_URL, formData);
    console.log("ASR Result:", result);
    userInput.value =
      (userInput.value ? userInput.value + " " : "") + (result?.text || "");
    collectedData.value.voice_text = result?.text || "";
  } catch (err) {
    error.value = err.message;
  } finally {
    event.target.value = ""; // allow re-selecting same file
  }
}
// Severity rating

/* ---------- Boot ---------- */
onMounted(() => {
  addMessage(getTranslatedText(0), "bot");
  collectedData.value = {};
  store.updateProfile({});
  store.reset();
});
</script>

<style scoped>
.chatbot-container {
  width: 600px;
  max-width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: sans-serif;
  margin: 20px auto;
  height: 70vh;
  background: white;
  background-image: linear-gradient(
      rgba(253, 207, 207, 0.144),
      rgba(147, 236, 4, 0.103)
    ),
    url("src/assets/bg/bg1.jpg");
  background-size: cover; /* scales image to cover entire area */
  background-repeat: no-repeat; /* prevents tiling */
  background-position: center; /* centers the image */

  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.messages-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.message {
  padding: 10px 15px;
  border-radius: 20px;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.4;
}
.message.bot {
  background-color: #f1f0f0;
  align-self: flex-start;
  color: #333;
}
.message.user {
  background-color: #2c5282;
  color: white;
  align-self: flex-end;
}
.input-container {
  padding: 15px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  align-items: center;
  background: #f9f9f9;
}
button {
  padding: 10px 15px;
  border: 1px solid #2c5282;
  background-color: white;
  color: #2c5282;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}
button:hover {
  background-color: #2c5282;
  color: white;
}
.text-entry {
  padding: 10px 15px;
  border: 1px solid #ccc;
  border-radius: 20px;
  flex: 1;
}
.error-message {
  color: #d93025;
  font-size: 12px;
  width: 100%;
  text-align: center;
  margin-top: 5px;
}
.symptom-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  width: 100%;
  padding: 10px;
}
.symptom-item {
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.symptom-item:hover {
  border-color: #2c5282;
}
.symptom-item.selected {
  border-color: #2c5282;
  background-color: #e6f2ff;
  box-shadow: 0 0 5px rgba(44, 82, 130, 0.5);
}
.symptom-item img {
  width: 48px;
  height: 48px;
  margin-bottom: 5px;
}
.symptom-item p {
  margin: 0;
  font-size: 12px;
  font-weight: bold;
}
.next-button {
  width: calc(100% - 20px);
  margin-top: 10px;
  background-color: #2c5282;
  color: white;
}
.nlp-textarea {
  width: 100%;
  height: 80px;
  border-radius: 10px;
  padding: 10px;
  border: 1px solid #ccc;
  font-family: sans-serif;
  resize: vertical;
}
</style>
