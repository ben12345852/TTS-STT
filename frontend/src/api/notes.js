import axios from 'axios'

// Axios-Instanz mit Base URL
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// API-Funktionen
export const notesApi = {
  // Alle Notizen abrufen
  getAllNotes: async () => {
    const response = await api.get('/api/notes')
    return response.data.notes
  },

  // Eine Notiz abrufen
  getNote: async (id) => {
    const response = await api.get(`/api/notes/${id}`)
    return response.data
  },

  // Notiz erstellen
  createNote: async (noteData) => {
    const response = await api.post('/api/notes', noteData)
    return response.data
  },

  // Notiz aktualisieren
  updateNote: async (id, noteData) => {
    const response = await api.put(`/api/notes/${id}`, noteData)
    return response.data
  },

  // Notiz löschen
  deleteNote: async (id) => {
    const response = await api.delete(`/api/notes/${id}`)
    return response.data
  },
}

export default api
