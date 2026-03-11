let video
let canvas
let ctx
let stream
let detectInterval

let capturedImages = []
let isUploading = false
let frameAbortController = null
let isSendingFrame = false  // lock — only one frame in-flight at a time

// ─── STATUS ───────────────────────────────────────────────
function showStatus(msg) {
  const bar = document.getElementById("status-bar")
  if (bar) bar.innerText = msg
}

// ─── PAUSE / RESUME DETECTION ─────────────────────────────
function pauseDetection() {
  clearInterval(detectInterval)
  detectInterval = null
  isSendingFrame = false       // reset lock so it never gets stuck

  if (frameAbortController) {
    frameAbortController.abort()
    frameAbortController = null
  }

  if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Pause all video tracks so camera fully stops sending frames
  if (stream) stream.getTracks().forEach(t => t.enabled = false)

  // Visually blur the video to signal it's paused
  if (video) video.style.filter = "blur(4px) brightness(0.5)"
}

function resumeDetection() {
  // Re-enable video tracks
  if (stream) stream.getTracks().forEach(t => t.enabled = true)

  // Remove blur
  if (video) video.style.filter = ""

  if (!detectInterval && stream) {
    detectInterval = setInterval(sendFrame, 333)
  }
}

// ─── LOADING OVERLAY ──────────────────────────────────────
function showUploadOverlay(label) {
  let overlay = document.getElementById("upload-overlay")
  if (!overlay) {
    overlay = document.createElement("div")
    overlay.id = "upload-overlay"
    overlay.innerHTML = `
      <div class="upload-overlay-inner">
        <div class="upload-spinner"></div>
        <div id="upload-overlay-label">Processing...</div>
        <div class="upload-progress-bar-bg">
          <div id="upload-progress-bar"></div>
        </div>
        <div id="upload-progress-pct">0%</div>
      </div>
    `
    if (!document.getElementById("upload-overlay-style")) {
      const style = document.createElement("style")
      style.id = "upload-overlay-style"
      style.textContent = `
        #upload-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.75);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
          backdrop-filter: blur(4px);
        }
        .upload-overlay-inner {
          background: #1e293b;
          border-radius: 14px;
          padding: 36px 48px;
          text-align: center;
          min-width: 280px;
          box-shadow: 0 0 40px rgba(0,0,0,0.6);
        }
        .upload-spinner {
          width: 48px;
          height: 48px;
          border: 4px solid #334155;
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin: 0 auto 16px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        #upload-overlay-label {
          font-size: 15px;
          color: #cbd5e1;
          margin-bottom: 18px;
        }
        .upload-progress-bar-bg {
          background: #334155;
          border-radius: 999px;
          height: 8px;
          overflow: hidden;
          margin-bottom: 8px;
        }
        #upload-progress-bar {
          height: 100%;
          width: 0%;
          background: #3b82f6;
          border-radius: 999px;
          transition: width 0.3s ease;
        }
        #upload-progress-pct {
          font-size: 13px;
          color: #64748b;
        }
      `
      document.head.appendChild(style)
    }
    document.body.appendChild(overlay)
  }
  document.getElementById("upload-overlay-label").innerText = label || "Processing..."
  setUploadProgress(0)
  overlay.style.display = "flex"
}

function setUploadProgress(pct, label) {
  const bar   = document.getElementById("upload-progress-bar")
  const pctEl = document.getElementById("upload-progress-pct")
  if (bar)   bar.style.width = pct + "%"
  if (pctEl) pctEl.innerText = Math.round(pct) + "%"
  if (label) document.getElementById("upload-overlay-label").innerText = label
}

function hideUploadOverlay() {
  const overlay = document.getElementById("upload-overlay")
  if (overlay) overlay.style.display = "none"
}

// ─── CAMERA ───────────────────────────────────────────────
function updateStreamButtons(running) {
  const startBtn = document.getElementById("start-btn")
  const stopBtn  = document.getElementById("stop-btn")
  if (startBtn) startBtn.disabled = running
  if (stopBtn)  stopBtn.disabled  = !running
}

async function startStream() {
  video  = document.getElementById("video")
  canvas = document.getElementById("overlay")
  ctx    = canvas.getContext("2d")

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.srcObject = stream

    video.onloadedmetadata = () => {
      canvas.width  = video.clientWidth
      canvas.height = video.clientHeight
      canvas.style.width  = video.clientWidth  + "px"
      canvas.style.height = video.clientHeight + "px"
    }

    window.addEventListener("resize", () => {
      if (!video.videoWidth) return
      canvas.width  = video.clientWidth
      canvas.height = video.clientHeight
    })

    detectInterval = setInterval(sendFrame, 333)
    updateStreamButtons(true)
    showStatus("Camera started")

  } catch (err) {
    console.error(err)
    showStatus("Camera permission denied")
  }
}

function stopStream() {
  if (stream) stream.getTracks().forEach(t => t.stop())
  stream = null
  clearInterval(detectInterval)
  detectInterval = null
  if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
  updateStreamButtons(false)
  showStatus("Camera stopped")
}

// ─── SEND FRAME ───────────────────────────────────────────
async function sendFrame() {
  if (isUploading)    return
  if (isSendingFrame) return
  if (!video || video.videoWidth === 0) return

  isSendingFrame = true  // lock BEFORE toBlob — nothing else gets in

  try {
    const blob = await new Promise(resolve => {
      const temp  = document.createElement("canvas")
      temp.width  = video.videoWidth
      temp.height = video.videoHeight
      temp.getContext("2d").drawImage(video, 0, 0)
      temp.toBlob(resolve, "image/jpeg")
    })

    if (!blob || isUploading) return  // check again after toBlob resolved

    frameAbortController = new AbortController()

    const formData = new FormData()
    formData.append("image", blob)

    const res  = await fetch("/upload", {
      method: "POST",
      body: formData,
      signal: frameAbortController.signal
    })
    const data = await res.json()

    if (data.success) {
      drawFaces(data.result.faces)
      updateDetectionList(data.result.faces)
    }

  } catch (err) {
    if (err.name === "AbortError") return
    console.error("Frame error:", err)
  } finally {
    frameAbortController = null
    isSendingFrame = false  // always unlock
  }
}

// ─── DRAW BOXES ───────────────────────────────────────────
function drawFaces(faces) {
  if (!ctx) return

  // Sync canvas internal resolution to match video display size exactly
  // so drawn coordinates always align with what the user sees
  const displayW = video.clientWidth
  const displayH = video.clientHeight

  if (canvas.width !== displayW || canvas.height !== displayH) {
    canvas.width  = displayW
    canvas.height = displayH
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Backend returns coords in natural video resolution — scale to display size
  const scaleX = displayW / video.videoWidth
  const scaleY = displayH / video.videoHeight

  faces.forEach(face => {
    const b = face.box
    const x = b.x1 * scaleX
    const y = b.y1 * scaleY
    const w = (b.x2 - b.x1) * scaleX
    const h = (b.y2 - b.y1) * scaleY

    ctx.strokeStyle = "#00ff41"
    ctx.lineWidth   = 2
    ctx.strokeRect(x, y, w, h)

    // label background for readability
    const label = face.label + " " + face.score.toFixed(2)
    ctx.font = "14px monospace"
    const textW = ctx.measureText(label).width
    ctx.fillStyle = "rgba(0,0,0,0.55)"
    ctx.fillRect(x, y - 20, textW + 8, 20)

    ctx.fillStyle = "#00ff41"
    ctx.fillText(label, x + 4, y - 5)
  })
}

// ─── DETECTION TABLE ──────────────────────────────────────
function updateDetectionList(faces) {
  const table = document.getElementById("recognition-table")
  if (!table) return

  table.innerHTML = ""

  if (!faces.length) {
    table.innerHTML = `<tr><td colspan="2" style="opacity:0.5">No faces detected</td></tr>`
    return
  }

  faces.forEach(face => {
    const row = document.createElement("tr")
    row.innerHTML = `
      <td>${face.label}</td>
      <td>${face.score.toFixed(2)}</td>
    `
    table.appendChild(row)
  })
}

// ─── CAPTURE FACE ─────────────────────────────────────────
function captureFace() {
  if (!video) return

  const temp  = document.createElement("canvas")
  temp.width  = video.videoWidth
  temp.height = video.videoHeight

  // FIX: use a separate variable, not ctx (which is the overlay canvas)
  const capCtx = temp.getContext("2d")
  capCtx.drawImage(video, 0, 0)

  temp.toBlob(blob => {
    capturedImages.push(blob)

    const img    = document.createElement("img")
    img.src      = URL.createObjectURL(blob)
    img.className = "captured-face"

    document.getElementById("captured-faces").appendChild(img)
    document.getElementById("capture-number").innerText = capturedImages.length

    // Enable upload as soon as there's at least 1 image
    document.getElementById("upload-btn").disabled = false

    showStatus(`Face captured (${capturedImages.length})`)
  }, "image/jpeg")
}

// ─── REGISTER USER ────────────────────────────────────────
async function uploadCapturedFaces() {
  const name = document.getElementById("person-name").value.trim()

  if (!name) { showStatus("Enter name first"); return }
  if (!capturedImages.length) { showStatus("Capture at least 1 image first"); return }
  if (isUploading) return

  isUploading = true

  // 1. Stop live detection so /upload doesn't compete
  pauseDetection()

  // 2. Show loading overlay
  showUploadOverlay(`Uploading ${capturedImages.length} image(s) for "${name}"...`)
  setUploadProgress(10)

  const formData = new FormData()
  formData.append("name", name)
  capturedImages.forEach(img => formData.append("images", img))

  try {
    setUploadProgress(25, "Sending images to server...")

    const res  = await fetch("/register-user", { method: "POST", body: formData })

    setUploadProgress(60, "Generating face embeddings...")

    const data = await res.json()

    if (!data.success) {
      hideUploadOverlay()
      showStatus("Upload failed: " + (data.message || data.error || "unknown error"))
      resumeDetection()
      isUploading = false
      return
    }

    setUploadProgress(85, "Reloading recognition model...")

    await fetch("/reload_embeddings", { method: "POST" })

    setUploadProgress(100, `Done! ${data.faces_added} face(s) registered for "${name}"`)

    showStatus(`User registered: ${name} (${data.faces_added} embeddings)`)

    // brief pause so user sees 100%
    await new Promise(r => setTimeout(r, 900))

    hideUploadOverlay()

    // clear state
    capturedImages = []
    document.getElementById("captured-faces").innerHTML = ""
    document.getElementById("capture-number").innerText = "0"
    document.getElementById("upload-btn").disabled      = true
    document.getElementById("person-name").value        = ""

    loadUsers()

  } catch (err) {
    console.error(err)
    hideUploadOverlay()
    showStatus("Upload error")
  } finally {
    // 3. Always resume detection when done
    resumeDetection()
    isUploading = false
  }
}

// ─── USERS ────────────────────────────────────────────────
async function loadUsers() {
  try {
    const res  = await fetch("/user_list")
    const data = await res.json()

    if (!data.success) return

    const list = document.getElementById("user-list")
    if (!list) return

    list.innerHTML = ""

    if (!data.users.length) {
      list.innerHTML = `<p style="opacity:0.5;font-size:13px">No registered users</p>`
      return
    }

    data.users.forEach(name => {
      const row = document.createElement("div")
      row.className = "user-item"
      row.innerHTML = `
        <span>${name}</span>
        <button onclick="deleteUser('${name}')">Delete</button>
      `
      list.appendChild(row)
    })

  } catch (err) {
    console.error(err)
    showStatus("Failed to load users")
  }
}

async function deleteUser(name) {
  isUploading = true
  pauseDetection()
  showUploadOverlay(`Deleting "${name}"...`)
  setUploadProgress(20)

  try {
    setUploadProgress(40, `Removing embeddings for "${name}"...`)

    const res  = await fetch("/user/" + encodeURIComponent(name), { method: "DELETE" })

    setUploadProgress(70, "Reloading recognition model...")

    const data = await res.json()

    if (!data.success) {
      hideUploadOverlay()
      showStatus("Delete failed: " + (data.message || data.error || "unknown error"))
      return
    }

    await fetch("/reload_embeddings", { method: "POST" })

    setUploadProgress(100, `"${name}" removed successfully`)

    showStatus("User removed: " + name)

    await new Promise(r => setTimeout(r, 900))

    hideUploadOverlay()

    loadUsers()

  } catch (err) {
    console.error(err)
    hideUploadOverlay()
    showStatus("Delete error")
  } finally {
    resumeDetection()
    isUploading = false
  }
}