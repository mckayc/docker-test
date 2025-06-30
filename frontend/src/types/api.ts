export interface User {
  id: number
  first_name: string
  last_name: string
  username: string
  email: string
  birthday: string
  is_active: boolean
  is_superuser: boolean
  experience_points: number
  level: number
  gold: number
}

export interface Task {
  id: number
  title: string
  description: string | null
  created_at: string
  due_date: string | null
  completed_at: string | null
  is_completed: boolean
  priority: 'low' | 'medium' | 'high' | 'critical'
  difficulty: 'trivial' | 'easy' | 'medium' | 'hard' | 'epic'
  experience_reward: number
  gold_reward: number
  streak_count: number
  owner_id: number
  parent_id: number | null
  category_id: number | null
  tags: string[]
}

export interface Achievement {
  id: number
  name: string
  description: string | null
  icon_url: string | null
  unlocked_at: string
  experience_reward: number
  gold_reward: number
  requirements: Record<string, any>
  user_id: number
}

export interface InventoryItem {
  id: number
  name: string
  description: string | null
  icon_url: string | null
  acquired_at: string
  item_type: 'weapon' | 'armor' | 'potion' | 'scroll' | 'quest_item' | 'cosmetic'
  rarity: number
  level_requirement: number
  stats: Record<string, any>
  effects: Record<string, any>
  quantity: number
  is_equipped: boolean
  owner_id: number
}

export interface Category {
  id: number
  name: string
  description: string | null
  color: string | null
  icon_name: string | null
}

export interface TaskTag {
  id: number
  name: string
  task_id: number
} 