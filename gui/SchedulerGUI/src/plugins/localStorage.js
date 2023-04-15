import { customRef } from 'vue'

class useLocalStorageHandler {
    
    get(key, defaultValue){
        const value = localStorage.getItem(key)
        return value ? JSON.parse(value) : defaultValue
    }

    set(key, value) {
        if (value === null) {
            localStorage.removeItem(key)
        } else {
            localStorage.setItem(key, JSON.stringify(value))
        }
    }
    
}
const useLocalStorage = new useLocalStorageHandler()
export {useLocalStorage}