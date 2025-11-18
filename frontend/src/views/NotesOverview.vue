<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { notesApi } from '../api/notes'
import CreateNoteModal from '../components/CreateNoteModal.vue'

const router = useRouter()

const notes = ref([])
const searchQuery = ref('')
const filteredNotes = ref([])
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)

// Notizen von API laden
async function loadNotes() {
  try {
    loading.value = true
    error.value = null
    const data = await notesApi.getAllNotes()
    notes.value = data
    filteredNotes.value = data
  } catch (err) {
    error.value = 'Fehler beim Laden der Notizen'
    console.error('Fehler:', err)
  } finally {
    loading.value = false
  }
}

// Beim Component-Mount Notizen laden
onMounted(() => {
  loadNotes()
})

function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'Heute'
  if (days === 1) return 'Gestern'
  if (days < 7) return `vor ${days} Tagen`
  
  return date.toLocaleDateString('de-DE', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric' 
  })
}

function formatDuration(seconds) {
  if (!seconds) return '0:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  
  if (mins >= 60) {
    const hours = Math.floor(mins / 60)
    const remainingMins = mins % 60
    return `${hours}:${remainingMins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function openNote(noteId) {
  router.push(`/note/${noteId}`)
}

function createNewNote() {
  showCreateModal.value = true
}

function onNoteCreated() {
  loadNotes()
}

function searchNotes() {
  if (!searchQuery.value.trim()) {
    filteredNotes.value = notes.value
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  filteredNotes.value = notes.value.filter(note => 
    note.title.toLowerCase().includes(query) ||
    (note.summary && note.summary.toLowerCase().includes(query))
  )
}
</script>

<template>
  <div class="container notes-overview">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Lade Notizen...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <h3>{{ error }}</h3>
      <button class="btn btn-primary" @click="loadNotes">Erneut versuchen</button>
    </div>

    <!-- Content -->
    <template v-else>
    <div class="page-header">
      <div>
        <h2 class="page-title">Meine Notizen</h2>
        <p class="page-subtitle">{{ filteredNotes.length }} {{ filteredNotes.length === 1 ? 'Notiz' : 'Notizen' }}</p>
      </div>
      <button class="btn btn-primary" @click="createNewNote">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
        </svg>
        Neue Notiz
      </button>
    </div>

    <div class="search-bar">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
      <input 
        type="text" 
        placeholder="Notizen durchsuchen..." 
        v-model="searchQuery"
        @input="searchNotes"
      />
    </div>

    <div class="notes-grid">
      <div 
        v-for="note in filteredNotes" 
        :key="note.id"
        class="note-card card"
        @click="openNote(note.id)"
      >
        <div class="note-header">
          <h3 class="note-title">{{ note.title }}</h3>
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>
        
        <p class="note-summary">{{ note.summary }}</p>
        
        <div class="note-footer">
          <div class="note-duration">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            {{ formatDuration(note.audio_duration) }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredNotes.length === 0" class="empty-state">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 11H3v2h6m2 0h6m2 0h2v-2h-2m-6-9h2v2h-2M4 9c-1.11 0-2 .89-2 2v2a2 2 0 0 0 2 2h1v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4h1a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-1V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v4H4z"></path>
      </svg>
      <h3>Keine Notizen gefunden</h3>
      <p>Erstelle deine erste Notiz per Sprachaufnahme</p>
    </div>
    </template>

    <!-- Create Note Modal -->
    <CreateNoteModal 
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @created="onNoteCreated"
    />
  </div>
</template>

<style scoped>
.notes-overview {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 2rem;
  transition: border-color 0.2s ease;
}

.search-bar:focus-within {
  border-color: var(--accent);
}

.search-bar svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-bar input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 1rem;
}

.search-bar input::placeholder {
  color: var(--text-muted);
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  animation: fadeIn 0.4s ease;
}

.note-card {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.note-title {
  font-size: 1.25rem;
  font-weight: 600;
  flex: 1;
  line-height: 1.3;
}

.note-date {
  color: var(--text-muted);
  font-size: 0.85rem;
  white-space: nowrap;
  margin-top: 4px;
}

.note-summary {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  margin-top: auto;
}

.note-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.note-duration svg {
  flex-shrink: 0;
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

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
}

.empty-state svg {
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 1rem;
}
</style>
