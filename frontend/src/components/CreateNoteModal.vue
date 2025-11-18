<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '../api/notes'

const router = useRouter()
const emit = defineEmits(['close', 'created'])

const isRecording = ref(false)
const audioBlob = ref(null)
const mediaRecorder = ref(null)
const recordingTime = ref(0)
const recordingInterval = ref(null)
const title = ref('')
const textContent = ref('')
const error = ref(null)
const isSaving = ref(false)

// Aufnahme starten
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    
    const chunks = []
    mediaRecorder.value.ondataavailable = (e) => {
      chunks.push(e.data)
    }
    
    mediaRecorder.value.onstop = () => {
      audioBlob.value = new Blob(chunks, { type: 'audio/webm' })
      stream.getTracks().forEach(track => track.stop())
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0
    
    // Timer starten
    recordingInterval.value = setInterval(() => {
      recordingTime.value++
    }, 1000)
  } catch (err) {
    error.value = 'Mikrofon-Zugriff verweigert'
    console.error('Fehler:', err)
  }
}

// Aufnahme stoppen
function stopRecording() {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    clearInterval(recordingInterval.value)
  }
}

// Aufnahme verwerfen
function discardRecording() {
  audioBlob.value = null
  recordingTime.value = 0
  title.value = ''
}

// Notiz speichern
async function saveNote() {
  if (!title.value.trim()) {
    error.value = 'Bitte Titel eingeben'
    return
  }
  
  if (!audioBlob.value && !textContent.value.trim()) {
    error.value = 'Bitte Audio aufnehmen oder Text eingeben'
    return
  }
  
  isSaving.value = true
  error.value = null
  
  try {
    // FormData für Datei-Upload erstellen
    const formData = new FormData()
    formData.append('title', title.value)
    
    if (textContent.value.trim()) {
      formData.append('text_content', textContent.value)
    }
    
    if (audioBlob.value) {
      // Audio-Datei hinzufügen
      const audioFile = new File([audioBlob.value], 'recording.webm', { type: 'audio/webm' })
      formData.append('audio_file', audioFile)
      formData.append('audio_duration', recordingTime.value.toString())
    }
    
    // An Backend senden
    await notesApi.createNote(formData)
    
    // Erfolgreich erstellt
    emit('created')
    emit('close')
  } catch (err) {
    console.error('Fehler beim Speichern:', err)
    error.value = 'Fehler beim Speichern der Notiz'
  } finally {
    isSaving.value = false
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Neue Sprach-Notiz</h2>
        <button class="close-btn" @click="$emit('close')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <!-- Error Message -->
        <div v-if="error" class="error-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {{ error }}
        </div>

        <!-- Titel eingeben -->
        <div class="form-group">
          <label for="note-title">Titel der Notiz</label>
          <input 
            id="note-title"
            v-model="title" 
            type="text" 
            placeholder="z.B. Meeting Notizen"
            class="input-field"
          />
        </div>

        <!-- Audio-Aufnahme Bereich -->
        <div class="audio-section">
          <h3 class="section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="22"></line>
              <line x1="8" y1="22" x2="16" y2="22"></line>
            </svg>
            Sprachaufnahme
          </h3>

          <div v-if="!audioBlob" class="record-controls">
            <button 
              v-if="!isRecording" 
              class="btn btn-primary"
              @click="startRecording"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10"></circle>
              </svg>
              Aufnahme starten
            </button>
            
            <div v-else class="recording-active">
              <div class="record-indicator">
                <div class="pulse-dot"></div>
                <span class="timer">{{ formatTime(recordingTime) }}</span>
              </div>
              <button 
                class="btn btn-danger"
                @click="stopRecording"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="6" width="12" height="12"></rect>
                </svg>
                Aufnahme beenden
              </button>
            </div>
          </div>

          <div v-else class="audio-preview">
            <div class="success-badge">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="9 12 11 14 15 10"></polyline>
              </svg>
              Aufnahme gespeichert ({{ formatTime(recordingTime) }})
            </div>
            <button class="btn btn-secondary btn-sm" @click="discardRecording">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
              Löschen
            </button>
          </div>
        </div>

        <!-- Text-Eingabe Bereich -->
        <div class="text-section">
          <h3 class="section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Zusätzliche Notize
          </h3>

          <div class="form-group">
            <textarea 
              v-model="textContent" 
              placeholder="Schreibe hier deine Notizen oder ergänzende Informationen..."
              class="textarea-field"
              rows="6"
            ></textarea>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="$emit('close')" :disabled="isSaving">
            Abbrechen
          </button>
          <button class="btn btn-primary" @click="saveNote" :disabled="isSaving">
            <svg v-if="!isSaving" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
              <polyline points="17 21 17 13 7 13 7 21"></polyline>
              <polyline points="7 3 7 8 15 8"></polyline>
            </svg>
            <span v-if="isSaving" class="spinner"></span>
            {{ isSaving ? 'Speichert...' : 'Notiz speichern' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.modal-body {
  padding: 2rem;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--danger);
  border-radius: 8px;
  color: var(--danger);
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.95rem;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.input-field:focus {
  outline: none;
  border-color: var(--accent);
}

.input-field::placeholder {
  color: var(--text-muted);
}

.audio-section,
.text-section {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.section-title svg {
  color: var(--accent);
}

.record-controls {
  text-align: center;
}

.recording-active {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.record-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.pulse-dot {
  width: 12px;
  height: 12px;
  background: var(--danger);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

.timer {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--danger);
  font-variant-numeric: tabular-nums;
}

.audio-preview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.success-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--success);
  font-weight: 500;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 0.9rem;
}

.textarea-field {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.textarea-field:focus {
  outline: none;
  border-color: var(--accent);
}

.textarea-field::placeholder {
  color: var(--text-muted);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
