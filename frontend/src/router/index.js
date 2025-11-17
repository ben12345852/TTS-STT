import { createRouter, createWebHistory } from 'vue-router'
import NotesOverview from '../views/NotesOverview.vue'
import NoteDetail from '../views/NoteDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: NotesOverview
    },
    {
      path: '/note/:id',
      name: 'note-detail',
      component: NoteDetail
    }
  ],
})

export default router
