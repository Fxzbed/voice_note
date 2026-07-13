import { ref } from 'vue'

const user = ref({
  isLoggedIn: false,
  username: ''
})

export function useUser() {
  const login = (username) => {
    user.value = {
      isLoggedIn: true,
      username
    }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  const logout = () => {
    user.value = {
      isLoggedIn: false,
      username: ''
    }
    localStorage.removeItem('user')
  }

  const initUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
  }

  return {
    user,
    login,
    logout,
    initUser
  }
}
