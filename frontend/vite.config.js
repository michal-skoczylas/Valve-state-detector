import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/refresh_cameras': 'http://127.0.0.1:5000',
      '/set_camera': 'http://127.0.0.1:5000',
      '/update_cam_params': 'http://127.0.0.1:5000',
      '/video_original': 'http://127.0.0.1:5000',
      '/video_threshold': 'http://127.0.0.1:5000',
      '/camera_pixel_value': 'http://127.0.0.1:5000',
      '/camera_analyze': 'http://127.0.0.1:5000',
      '/image': 'http://127.0.0.1:5000',
      '/pixel_value': 'http://127.0.0.1:5000',
      '/threshold': 'http://127.0.0.1:5000',
      '/analyze_valves': 'http://127.0.0.1:5000',
      '/configs': 'http://127.0.0.1:5000',
      '/save_config': 'http://127.0.0.1:5000',
      '/load_config': 'http://127.0.0.1:5000'
    }
  }
})
