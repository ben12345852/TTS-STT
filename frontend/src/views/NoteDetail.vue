<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { notesApi } from '../api/notes'
import { marked } from 'marked'

const router = useRouter()
const route = useRoute()

const activeTab = ref(null)
const loading = ref(true)
const error = ref(null)

// Audio Player State
const audioElement = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)

const note = ref(null)

// Computed property für Markdown-Rendering
const summaryHtml = computed(() => {
  if (!note.value?.summary) return ''
  return marked(note.value.summary)
})

// Auto-Refresh für processing Status
let refreshInterval = null

// Notiz von API laden
async function loadNote() {
  try {
    loading.value = true
    error.value = null
    const data = await notesApi.getNote(route.params.id)
    note.value = data
    
    // Auto-Refresh starten wenn Status = processing
    if (data.status === 'processing') {
      if (!refreshInterval) {
        refreshInterval = setInterval(() => {
          loadNote()
        }, 3000) // Alle 3 Sekunden aktualisieren
      }
    } else {
      // Refresh stoppen wenn fertig
      if (refreshInterval) {
        clearInterval(refreshInterval)
        refreshInterval = null
      }
    }
    
    // Standard-Tab setzen basierend auf verfügbaren Daten
    if (!activeTab.value) {
      if (data.transcript) {
        activeTab.value = 'transcript'
      } else if (data.manual_notes) {
        activeTab.value = 'manual_notes'
      } else if (data.summary) {
        activeTab.value = 'summary'
      }
    }
  } catch (err) {
    error.value = 'Fehler beim Laden der Notiz'
    console.error('Fehler:', err)
  } finally {
    loading.value = false
  }
}

// Beim Component-Mount Notiz laden
onMounted(() => {
  loadNote()
})

// Cleanup bei Component-Unmount
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

function goBack() {
  router.push('/')
}

function formatDateTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function playAudio() {
  // TODO: TTS implementieren
  console.log('Audio abspielen')
}

function editNote() {
  // TODO: Edit-Modus implementieren
  console.log('Notiz bearbeiten')
}

function deleteNote() {
  // TODO: Löschen implementieren
  if (confirm('Notiz wirklich löschen?')) {
    notesApi.deleteNote(route.params.id)
      .then(() => {
        router.push('/')
      })
      .catch(err => {
        console.error('Fehler beim Löschen:', err)
        alert('Fehler beim Löschen der Notiz')
      })
  }
}

function exportNote() {
  // TODO: Export-Dialog öffnen
  console.log('Notiz exportieren')
}

// Audio Player Functions
function togglePlayPause() {
  if (!audioElement.value) return
  
  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    audioElement.value.play()
  }
  isPlaying.value = !isPlaying.value
}

function onTimeUpdate() {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime
  }
}

function onLoadedMetadata() {
  if (audioElement.value) {
    duration.value = audioElement.value.duration
  }
}

function onEnded() {
  isPlaying.value = false
  currentTime.value = 0
}

function seekTo(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  const newTime = percent * duration.value
  
  if (audioElement.value) {
    audioElement.value.currentTime = newTime
    currentTime.value = newTime
  }
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function changeVolume(event) {
  const newVolume = parseFloat(event.target.value)
  volume.value = newVolume
  if (audioElement.value) {
    audioElement.value.volume = newVolume
  }
}
</script>

<template>
  <div class="container note-detail">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Lade Notiz...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <h3>{{ error }}</h3>
      <button class="btn btn-primary" @click="loadNote">Erneut versuchen</button>
    </div>

    <!-- Content -->
    <template v-else-if="note">
    <!-- Header mit Navigation -->
    <div class="detail-header">
      <button class="btn-back" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Zurück
      </button>

      <div class="action-buttons">
        <button class="btn btn-secondary" @click="playAudio" title="Zusammenfassung vorlesen">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
          </svg>
        </button>
        <button class="btn btn-secondary" @click="editNote" title="Bearbeiten">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
        </button>
        <button class="btn btn-secondary" @click="exportNote" title="Exportieren">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
        </button>
        <button class="btn btn-secondary delete-btn" @click="deleteNote" title="Löschen">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Note Info -->
    <div class="note-info">
      <h1 class="note-title-detail">{{ note.title }}</h1>
      <div class="note-meta">
        <span class="meta-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          {{ formatDateTime(note.created_at) }}
        </span>
        
        <!-- Processing Status Badge -->
        <span v-if="note.status === 'processing'" class="meta-item status-processing">
          <div class="processing-spinner"></div>
          KI verarbeitet Audio...
        </span>
        <span v-else-if="note.status === 'error'" class="meta-item status-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          Verarbeitungsfehler
        </span>
      </div>
    </div>

    <!-- Audio Player -->
    <div class="audio-player-container" v-if="note.audio_url">
      <div class="audio-player">
        <audio
          ref="audioElement"
          :src="`http://localhost:8000${note.audio_url}`"
          @timeupdate="onTimeUpdate"
          @loadedmetadata="onLoadedMetadata"
          @ended="onEnded"
        ></audio>

        <button class="play-button" @click="togglePlayPause">
          <svg v-if="!isPlaying" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16"></rect>
            <rect x="14" y="4" width="4" height="16"></rect>
          </svg>
        </button>

        <div class="time-display">{{ formatTime(currentTime) }}</div>

        <div class="progress-bar-container" @click="seekTo">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: duration > 0 ? (currentTime / duration * 100) + '%' : '0%' }"
            ></div>
            <div 
              class="progress-handle" 
              :style="{ left: duration > 0 ? (currentTime / duration * 100) + '%' : '0%' }"
            ></div>
          </div>
        </div>

        <div class="time-display">{{ formatTime(duration) }}</div>

        <div class="volume-control">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            <path v-if="volume > 0.5" d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            <path v-if="volume > 0" d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
          </svg>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.01" 
            :value="volume"
            @input="changeVolume"
            class="volume-slider"
          />
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-container">
      <div class="tabs">
        <button 
          :class="['tab', { active: activeTab === 'transcript' }]"
          @click="activeTab = 'transcript'"
          v-if="note.transcript"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          Transkription
        </button>
        <button 
          :class="['tab', { active: activeTab === 'manual_notes' }]"
          @click="activeTab = 'manual_notes'"
          v-if="note.manual_notes"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20h9"></path>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
          </svg>
          Notizen
        </button>
        <button 
          :class="['tab', { active: activeTab === 'summary' }]"
          @click="activeTab = 'summary'"
          v-if="note.summary"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <line x1="9" y1="15" x2="15" y2="15"></line>
          </svg>
          Zusammenfassung
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Transkription -->
        <div v-if="activeTab === 'transcript'" class="content-panel fade-in">
          <div class="panel-header">
            <h3>Vollständige Transkription</h3>
            <span v-if="note.transcript" class="word-count">{{ note.transcript.split(' ').length }} Wörter</span>
          </div>
          <div class="text-content">
            <div v-if="note.transcript">
              {{ note.transcript }}
            </div>
            <div v-else class="empty-state">
              <p>Keine Transkription vorhanden</p>
            </div>
          </div>
        </div>

        <!-- Manuelle Notizen -->
        <div v-if="activeTab === 'manual_notes'" class="content-panel fade-in">
          <div class="panel-header">
            <h3>Manuelle Notizen</h3>
            <span v-if="note.manual_notes" class="word-count">{{ note.manual_notes.split(' ').length }} Wörter</span>
          </div>
          <div class="text-content">
            <div v-if="note.manual_notes">
              {{ note.manual_notes }}
            </div>
            <div v-else class="empty-state">
              <p>Keine manuellen Notizen vorhanden</p>
            </div>
          </div>
        </div>

        <!-- Zusammenfassung -->
        <div v-if="activeTab === 'summary'" class="content-panel fade-in">
          <div class="panel-header">
            <h3>KI-Zusammenfassung</h3>
            <button class="btn btn-primary btn-sm" @click="playAudio">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              Vorlesen
            </button>
          </div>
          <div class="text-content summary-content">
            <div v-if="note.summary" class="markdown-content" v-html="summaryHtml"></div>
            <div v-else class="empty-state">
              <p>Keine Zusammenfassung vorhanden</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<style scoped>
.note-detail {
  max-width: 900px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1rem;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-back:hover {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.delete-btn:hover {
  background-color: var(--danger);
  color: white;
}

.status-processing {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--accent);
  font-weight: 500;
}

.status-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--danger);
  font-weight: 500;
}

.processing-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.note-info {
  margin-bottom: 2rem;
}

.note-title-detail {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.note-meta {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.meta-item svg {
  color: var(--text-muted);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--bg-tertiary);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state svg {
  color: var(--danger);
  margin-bottom: 1rem;
}

.error-state h3 {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

/* Audio Player */
.audio-player-container {
  margin-bottom: 2rem;
}

.audio-player {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.play-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--accent);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.play-button:hover {
  background-color: var(--accent-hover);
  transform: scale(1.05);
}

.play-button:active {
  transform: scale(0.95);
}

.time-display {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
  min-width: 45px;
  text-align: center;
}

.progress-bar-container {
  flex: 1;
  cursor: pointer;
  padding: 10px 0;
}

.progress-bar {
  height: 6px;
  background-color: var(--bg-tertiary);
  border-radius: 3px;
  position: relative;
  overflow: visible;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-light));
  border-radius: 3px;
  transition: width 0.1s linear;
  position: relative;
}

.progress-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 16px;
  height: 16px;
  background-color: var(--accent-light);
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  transition: left 0.1s linear;
  cursor: grab;
}

.progress-handle:active {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.2);
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 140px;
}

.volume-control svg {
  color: var(--text-secondary);
  flex-shrink: 0;
}

.volume-slider {
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-tertiary);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: var(--accent);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.volume-slider::-webkit-slider-thumb:hover {
  background: var(--accent-light);
  transform: scale(1.2);
}

.volume-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: var(--accent);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.volume-slider::-moz-range-thumb:hover {
  background: var(--accent-light);
  transform: scale(1.2);
}

.tabs-container {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  background-color: var(--bg-tertiary);
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 1rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 3px solid transparent;
}

.tab:hover {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.tab.active {
  color: var(--accent-light);
  border-bottom-color: var(--accent);
  background-color: var(--bg-secondary);
}

.tab svg {
  flex-shrink: 0;
}

.tab-content {
  padding: 2rem;
}

.content-panel {
  animation: fadeIn 0.3s ease;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.panel-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
}

.word-count {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 0.9rem;
}

.manual-notes h4 {
  color: var(--accent);
  font-size: 1rem;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-muted);
}

.empty-state p {
  font-size: 1rem;
}

.text-content {
  color: var(--text-secondary);
  font-size: 1.05rem;
  line-height: 1;
  white-space: pre-wrap;
}

.summary-content {
  font-weight: 400;
}

/* Markdown Content Styling */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  color: var(--text-primary);
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.35rem;
  line-height: 1.3;
}

.markdown-content :deep(h1) { font-size: 2rem; }
.markdown-content :deep(h2) { font-size: 1.5rem; }
.markdown-content :deep(h3) { font-size: 1.25rem; }
.markdown-content :deep(h4) { font-size: 1.1rem; }

.markdown-content :deep(p) {
  margin-bottom: 0.5rem;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-left: 1.5rem;
  margin-top: 0.25rem;
  margin-bottom: 0.5rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0;
  line-height: 1.5;
}

.markdown-content :deep(li + li) {
  margin-top: 0.15rem;
}

.markdown-content :deep(code) {
  background-color: var(--bg-tertiary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.95em;
}

.markdown-content :deep(pre) {
  background-color: var(--bg-tertiary);
  padding: 0.75rem;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 0.5rem;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid var(--accent);
  padding-left: 1rem;
  margin-left: 0;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-style: italic;
}

.markdown-content :deep(a) {
  color: var(--accent-light);
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1rem 0;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0.5rem;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid var(--border);
  padding: 0.5rem;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: var(--bg-tertiary);
  font-weight: 600;
}
</style>
