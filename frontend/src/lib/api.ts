import axios from 'axios'
import type {
  User,
  Task,
  Achievement,
  InventoryItem,
  Category,
  TaskTag,
} from '@/types/api'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth
export const login = async (username: string, password: string) => {
  const response = await api.post('/login/access-token', {
    username,
    password,
  })
  return response.data
}

export const register = async (userData: {
  first_name: string
  last_name: string
  username: string
  email: string
  password: string
  birthday: string
}) => {
  const response = await api.post('/register', userData)
  return response.data as User
}

// Users
export const getCurrentUser = async () => {
  const response = await api.get('/users/me')
  return response.data as User
}

// Tasks
export const getTasks = async (params?: {
  skip?: number
  limit?: number
  include_completed?: boolean
}) => {
  const response = await api.get('/tasks', { params })
  return response.data as Task[]
}

export const createTask = async (taskData: {
  title: string
  description?: string
  due_date?: string
  priority?: 'low' | 'medium' | 'high' | 'critical'
  difficulty?: 'trivial' | 'easy' | 'medium' | 'hard' | 'epic'
  parent_id?: number
  category_id?: number
}) => {
  const response = await api.post('/tasks', taskData)
  return response.data as Task
}

export const updateTask = async (taskId: number, taskData: Partial<Task>) => {
  const response = await api.put(`/tasks/${taskId}`, taskData)
  return response.data as Task
}

export const deleteTask = async (taskId: number) => {
  const response = await api.delete(`/tasks/${taskId}`)
  return response.data as Task
}

// Achievements
export const getAchievements = async () => {
  const response = await api.get('/game/achievements')
  return response.data as Achievement[]
}

// Inventory
export const getInventory = async () => {
  const response = await api.get('/game/inventory')
  return response.data as InventoryItem[]
}

export const updateInventoryItem = async (
  itemId: number,
  itemData: { quantity?: number; is_equipped?: boolean }
) => {
  const response = await api.put(`/game/inventory/${itemId}`, itemData)
  return response.data as InventoryItem
}

// Categories
export const getCategories = async () => {
  const response = await api.get('/game/categories')
  return response.data as Category[]
}

// Tags
export const getTaskTags = async (taskId: number) => {
  const response = await api.get(`/game/tasks/${taskId}/tags`)
  return response.data as TaskTag[]
}

export const createTaskTag = async (taskId: number, name: string) => {
  const response = await api.post(`/game/tasks/${taskId}/tags`, { name })
  return response.data as TaskTag
}

export const deleteTaskTag = async (tagId: number) => {
  const response = await api.delete(`/game/tasks/tags/${tagId}`)
  return response.data as TaskTag
}

// Add auth token to requests
export const setAuthToken = (token: string) => {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export const clearAuthToken = () => {
  delete api.defaults.headers.common['Authorization']
} 