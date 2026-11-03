const $ = (id) => document.getElementById(id);
let questions = [],
  answers = [],
  current = 0,
  setup = {},
  datasetContext = "",
  recognition = null,
  cameraStream = null,
  questionAudio = null;
async function speakQuestion(text) {
  if (questionAudio) {
    questionAudio.pause();
    questionAudio.remove();
  }

  questionAudio = document.createElement("audio");
  questionAudio.controls = true;

  $("questionText").insertAdjacentElement("afterend", questionAudio);

  try {
    const res = await fetch("/api/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text }),
    });

    if (!res.ok) {
      const error = await res.json();
      throw Error(error.detail || "Voice generation failed");
    }

    const audioBlob = await res.blob();
    const audioURL = URL.createObjectURL(audioBlob);

    questionAudio.src = audioURL;

    questionAudio.onended = () => {
      URL.revokeObjectURL(audioURL);
    };

    try {
      await questionAudio.play();
    } catch {
      setError(
        "answerError",
        "Click the audio play button to hear the question.",
      );
    }
  } catch (err) {
    setError("answerError", "Voice error: " + err.message);
  }
}

function show(id) {
  $(id).classList.remove("hidden");
}
function hide(id) {
  $(id).classList.add("hidden");
}
function setError(id, msg) {
  $(id).textContent = msg || "";
}

$("dataset").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  datasetContext = "";
  if (!file) {
    $("datasetStatus").textContent = "No dataset selected.";
    return;
  }
  $("datasetStatus").textContent = "Reading CSV...";
  const form = new FormData();
  form.append("file", file);
  try {
    const res = await fetch("/api/dataset-preview", {
      method: "POST",
      body: form,
    });
    const d = await res.json();
    if (!res.ok) throw Error(d.detail || "Could not read CSV");
    datasetContext = d.context;
    $("datasetStatus").textContent =
      `${d.filename}: ${d.rows_read} rows read (first 40 used as reference).`;
  } catch (err) {
    $("datasetStatus").textContent = err.message;
  }
});

$("startBtn").addEventListener("click", async () => {
  setError("setupError", "");
  setup = {
    company: $("company").value.trim(),
    role: $("role").value.trim(),
    experience: $("experience").value,
    interview_type: $("interviewType").value,
    question_count: Number($("questionCount").value),
    company_rules: $("rules").value.trim(),
    dataset_context: datasetContext,
  };
  if (!setup.company || !setup.role) {
    setError("setupError", "Enter company and job role.");
    return;
  }
  $("startBtn").disabled = true;
  $("startBtn").textContent = "Generating...";
  try {
    const res = await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(setup),
    });
    const d = await res.json();
    if (!res.ok) throw Error(d.detail || "Could not start");
    questions = d.questions;
    answers = [];
    current = 0;
    hide("setupPanel");
    hide("reportPanel");
    show("interviewPanel");
    renderQuestion();
  } catch (err) {
    setError("setupError", err.message);
  } finally {
    $("startBtn").disabled = false;
    $("startBtn").textContent = "Generate interview questions";
  }
});
function renderQuestion() {
    $("questionText").textContent = questions[current];

    $("progress").textContent =
        `Question ${current + 1} of ${questions.length}`;

    $("answer").value = "";

    hide("feedback");
    hide("nextBtn");
    hide("finishBtn");

    show("submitBtn");
    $("submitBtn").disabled = false;

    setError("answerError", "");

    speakQuestion(questions[current]);
}
function addList(parent, title, items) {
  const h = document.createElement("h4");
  h.textContent = title;
  parent.append(h);
  const ul = document.createElement("ul");
  (items || []).forEach((x) => {
    const li = document.createElement("li");
    li.textContent = x;
    ul.append(li);
  });
  parent.append(ul);
}
function renderFeedback(r) {
  const box = $("feedback");
  box.innerHTML = "";
  const score = document.createElement("p");
  score.className = "score";
  score.textContent = `Practice score: ${r.score}/10`;
  const summary = document.createElement("p");
  summary.textContent = r.brief_feedback;
  box.append(score, summary);
  addList(box, "What went well", r.strengths);
  addList(box, "Areas to improve", r.improvements);
  const sample = document.createElement("p");
  sample.textContent = "Example improvement: " + r.sample_answer;
  box.append(sample);
  show("feedback");
}
$("nextBtn").addEventListener("click", () => {
  current++;
  renderQuestion();
});
$("finishBtn").addEventListener("click", async () => {
  $("finishBtn").disabled = true;
  $("finishBtn").textContent = "Preparing report...";
  try {
    const res = await fetch("/api/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        company: setup.company,
        role: setup.role,
        answers,
      }),
    });
    const d = await res.json();
    if (!res.ok) throw Error(d.detail || "Report failed");
    renderReport(d);
    hide("interviewPanel");
    show("reportPanel");
  } catch (err) {
    setError("answerError", err.message);
  } finally {
    $("finishBtn").disabled = false;
    $("finishBtn").textContent = "Finish interview";
  }
});
function reportBlock(root, title, content) {
  const d = document.createElement("div");
  d.className = "report-block";
  const h = document.createElement("h3");
  h.textContent = title;
  d.append(h);
  if (Array.isArray(content)) {
    const ul = document.createElement("ul");
    content.forEach((x) => {
      const li = document.createElement("li");
      li.textContent = x;
      ul.append(li);
    });
    d.append(ul);
  } else {
    const p = document.createElement("p");
    p.textContent = content;
    d.append(p);
  }
  root.append(d);
}
function renderReport(r) {
  const root = $("reportContent");
  root.innerHTML = "";
  reportBlock(root, "Overall summary", r.overall_summary);
  reportBlock(root, "Strengths", r.good_points);
  reportBlock(root, "Practice areas", r.practice_areas);
  reportBlock(root, "Next steps", r.next_steps);
}
$("restartBtn").addEventListener("click", () => {
  hide("reportPanel");
  show("setupPanel");
});
$("speakBtn").addEventListener("click", () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    setError(
      "answerError",
      "Speech recognition is not supported. Please type your answer.",
    );
    return;
  }
  recognition = new SR();
  recognition.lang = "en-IN";
  recognition.interimResults = true;
  recognition.continuous = true;
  recognition.onresult = (e) => {
    let t = "";
    for (let i = 0; i < e.results.length; i++)
      t += e.results[i][0].transcript + " ";
    $("answer").value = t.trim();
  };
  recognition.onerror = (e) =>
    setError("answerError", "Speech error: " + e.error);
  recognition.start();
  setError("answerError", "Listening... speak your answer.");
});
$("stopSpeakBtn").addEventListener("click", () => {
  if (recognition) recognition.stop();
  setError("answerError", "");
});
$("cameraBtn").addEventListener("click", async () => {
  try {
    if (!navigator.mediaDevices?.getUserMedia)
      throw Error("Camera needs localhost or HTTPS and a supported browser.");
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false,
    });
    $("camera").srcObject = cameraStream;
    $("cameraBtn").textContent = "Camera enabled";
  } catch (err) {
    setError("answerError", err.message);
  }
});
window.addEventListener("beforeunload", () => {
  if (recognition) recognition.stop();
  if (cameraStream) cameraStream.getTracks().forEach((t) => t.stop());
});

